from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.core.cache import cache
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_cookie
from django.db.models import Q
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST
from .forms import ItemReportForm, SignUpForm, ClaimRequestForm
from .models import Category, ItemReport, ClaimRequest

@cache_page(60)
@vary_on_cookie
def home(request):
    latest_reports = ItemReport.objects.select_related("category", "created_by")[:6]
    return render(request, "reports/home.html", {"latest_reports": latest_reports})

@cache_page(60)
@vary_on_cookie
def report_list(request):
    reports = ItemReport.objects.select_related("category", "created_by").all()
    query = request.GET.get("q", "").strip()
    report_type = request.GET.get("type", "")
    status = request.GET.get("status", "")
    category_id = request.GET.get("category", "")
    if query:
        reports = reports.filter(Q(title__icontains=query) | Q(description__icontains=query) | Q(location__icontains=query))
    if report_type in ItemReport.ReportType.values:
        reports = reports.filter(report_type=report_type)
    if status in ItemReport.Status.values:
        reports = reports.filter(status=status)
    if category_id.isdigit():
        reports = reports.filter(category_id=category_id)
    page_obj = Paginator(reports, 9).get_page(request.GET.get("page"))
    return render(request, "reports/report_list.html", {
        "page_obj": page_obj, "categories": Category.objects.all(),
        "q": query, "selected_type": report_type, "selected_status": status,
        "selected_category": category_id,
    })

def report_detail(request, pk):
    report = get_object_or_404(ItemReport.objects.select_related("category", "created_by"), pk=pk)
    existing_claim = None
    if request.user.is_authenticated:
        existing_claim = ClaimRequest.objects.filter(item=report, requester=request.user).first()
    return render(request, "reports/report_detail.html", {"report": report, "claim_form": ClaimRequestForm(), "existing_claim": existing_claim})

@login_required
def create_report(request):
    if request.method == "POST":
        form = ItemReportForm(request.POST, request.FILES)
        if form.is_valid():
            report = form.save(commit=False)
            report.created_by = request.user
            report.save()
            cache.clear()  # Clear cached home, listings, and API responses.
            messages.success(request, "Your report has been published.")
            return redirect("report_detail", pk=report.pk)
    else:
        form = ItemReportForm()
    return render(request, "reports/report_form.html", {"form": form, "page_title": "Create report"})

@login_required
def edit_report(request, pk):
    report = get_object_or_404(ItemReport, pk=pk)
    if report.created_by_id != request.user.id and not request.user.is_staff:
        return HttpResponseForbidden("You can only edit your own report.")
    if request.method == "POST":
        form = ItemReportForm(request.POST, request.FILES, instance=report)
        if form.is_valid():
            form.save()
            cache.clear()
            messages.success(request, "Report updated.")
            return redirect("report_detail", pk=report.pk)
    else:
        form = ItemReportForm(instance=report)
    return render(request, "reports/report_form.html", {"form": form, "page_title": "Edit report"})

@login_required
@require_POST
def delete_report(request, pk):
    report = get_object_or_404(ItemReport, pk=pk)
    if report.created_by_id != request.user.id and not request.user.is_staff:
        return HttpResponseForbidden("You can only delete your own report.")
    report.delete()
    cache.clear()
    messages.success(request, "Report deleted.")
    return redirect("report_list")

def signup(request):
    if request.user.is_authenticated:
        return redirect("report_list")
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Account created. Welcome!")
            return redirect("report_list")
    else:
        form = SignUpForm()
    return render(request, "registration/signup.html", {"form": form})

@login_required
@require_POST
def create_claim(request, pk):
    report = get_object_or_404(ItemReport, pk=pk)
    if report.created_by_id == request.user.id:
        messages.error(request, "You cannot claim your own report.")
    elif report.status != ItemReport.Status.OPEN:
        messages.error(request, "This report is not open for claims.")
    elif ClaimRequest.objects.filter(item=report, requester=request.user).exists():
        messages.error(request, "You have already submitted a claim for this report.")
    else:
        form = ClaimRequestForm(request.POST)
        if form.is_valid():
            claim = form.save(commit=False)
            claim.item = report
            claim.requester = request.user
            claim.save()
            cache.clear()
            messages.success(request, "Claim request sent to the report owner.")
    return redirect("report_detail", pk=report.pk)

@login_required
@require_POST
def decide_claim(request, pk, claim_id):
    report = get_object_or_404(ItemReport, pk=pk)
    if report.created_by_id != request.user.id and not request.user.is_staff:
        return HttpResponseForbidden("Only the report owner can decide claims.")
    claim = get_object_or_404(ClaimRequest, pk=claim_id, item=report)
    decision = request.POST.get("decision")
    if claim.status != ClaimRequest.ClaimStatus.PENDING:
        messages.error(request, "This claim has already been decided.")
    elif decision == "approve":
        claim.status = ClaimRequest.ClaimStatus.APPROVED
        claim.save()
        report.status = ItemReport.Status.CLAIMED
        report.save(update_fields=["status", "updated_at"])
        ClaimRequest.objects.filter(item=report).exclude(pk=claim.pk).update(status=ClaimRequest.ClaimStatus.REJECTED)
        cache.clear()
        messages.success(request, "Claim approved.")
    elif decision == "reject":
        claim.status = ClaimRequest.ClaimStatus.REJECTED
        claim.save()
        cache.clear()
        messages.success(request, "Claim rejected.")
    else:
        messages.error(request, "Unknown action.")
    return redirect("report_detail", pk=report.pk)
