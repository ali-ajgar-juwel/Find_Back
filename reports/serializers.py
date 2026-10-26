from rest_framework import serializers
from .models import Category, ItemReport, ClaimRequest

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name", "description", "created_at"]

class ItemReportSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source="category.name", read_only=True)
    created_by_username = serializers.CharField(source="created_by.username", read_only=True)
    class Meta:
        model = ItemReport
        fields = ["id", "title", "description", "report_type", "status", "location", "date_occurred", "category", "category_name", "created_by", "created_by_username", "image", "created_at", "updated_at"]
        read_only_fields = ["status", "created_by", "created_at", "updated_at"]

class ClaimRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClaimRequest
        fields = ["id", "item", "requester", "message", "status", "created_at"]
        read_only_fields = ["requester", "status", "created_at"]
