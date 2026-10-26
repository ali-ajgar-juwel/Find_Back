from django.conf import settings
from django.db import models

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        ordering = ["name"]
    def __str__(self):
        return self.name

class ItemReport(models.Model):
    class ReportType(models.TextChoices):
        LOST = "LOST", "Lost"
        FOUND = "FOUND", "Found"
    class Status(models.TextChoices):
        OPEN = "OPEN", "Open"
        CLAIMED = "CLAIMED", "Claimed"
        RESOLVED = "RESOLVED", "Resolved"
    title = models.CharField(max_length=200)
    description = models.TextField()
    report_type = models.CharField(max_length=5, choices=ReportType.choices)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.OPEN)
    location = models.CharField(max_length=200)
    date_occurred = models.DateField()
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name="reports")
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="item_reports")
    image = models.ImageField(upload_to="reports/", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        ordering = ["-created_at"]
    def __str__(self):
        return f"{self.title} ({self.report_type})"

class ClaimRequest(models.Model):
    class ClaimStatus(models.TextChoices):
        PENDING = "PENDING", "Pending"
        APPROVED = "APPROVED", "Approved"
        REJECTED = "REJECTED", "Rejected"
    item = models.ForeignKey(ItemReport, on_delete=models.CASCADE, related_name="claim_requests")
    requester = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="claim_requests")
    message = models.TextField(blank=True)
    status = models.CharField(max_length=10, choices=ClaimStatus.choices, default=ClaimStatus.PENDING)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        ordering = ["-created_at"]
        constraints = [models.UniqueConstraint(fields=["item", "requester"], name="unique_claim_per_user_item")]
    def __str__(self):
        return f"Claim for {self.item.title} by {self.requester}"
