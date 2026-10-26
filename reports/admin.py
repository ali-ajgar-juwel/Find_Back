from django.contrib import admin
from .models import Category, ItemReport, ClaimRequest

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "created_at")
    search_fields = ("name",)

@admin.register(ItemReport)
class ItemReportAdmin(admin.ModelAdmin):
    list_display = ("title", "report_type", "status", "category", "created_by", "created_at")
    list_filter = ("report_type", "status", "category")
    search_fields = ("title", "description", "location")
    readonly_fields = ("created_at", "updated_at")

@admin.register(ClaimRequest)
class ClaimRequestAdmin(admin.ModelAdmin):
    list_display = ("item", "requester", "status", "created_at")
    list_filter = ("status",)
