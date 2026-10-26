from datetime import date
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from .models import Category, ItemReport

User = get_user_model()

class ReportFlowTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="Strong-test-pass-123")
        self.category = Category.objects.create(name="Electronics")
        self.report = ItemReport.objects.create(
            title="Lost keys", description="A set of keys", report_type=ItemReport.ReportType.LOST,
            location="Library", date_occurred=date.today(), category=self.category, created_by=self.user,
        )
    def test_report_list_loads(self):
        response = self.client.get(reverse("report_list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Lost keys")
    def test_create_requires_login(self):
        response = self.client.get(reverse("create_report"))
        self.assertEqual(response.status_code, 302)
    def test_owner_can_edit(self):
        self.client.login(username="testuser", password="Strong-test-pass-123")
        response = self.client.get(reverse("edit_report", args=[self.report.pk]))
        self.assertEqual(response.status_code, 200)
    def test_other_user_cannot_edit(self):
        User.objects.create_user(username="other", password="Strong-test-pass-123")
        self.client.login(username="other", password="Strong-test-pass-123")
        response = self.client.get(reverse("edit_report", args=[self.report.pk]))
        self.assertEqual(response.status_code, 403)

class ReportAPITests(TestCase):
    def setUp(self):
        from rest_framework.test import APIClient
        self.api = APIClient()
        self.user = User.objects.create_user(username="apiuser", password="Strong-test-pass-123")
        self.category = Category.objects.create(name="Documents")

    def test_public_report_api_lists_reports(self):
        response = self.api.get("/api/reports/")
        self.assertEqual(response.status_code, 200)
        self.assertIn("results", response.data)

    def test_authenticated_user_can_create_report(self):
        self.api.force_authenticate(user=self.user)
        response = self.api.post("/api/reports/", {
            "title": "Blue notebook", "description": "Blue notebook found near the gate",
            "report_type": "FOUND", "location": "Main gate",
            "date_occurred": date.today().isoformat(), "category": self.category.pk,
        }, format="json")
        self.assertEqual(response.status_code, 201)
        self.assertEqual(ItemReport.objects.count(), 1)
        self.assertEqual(ItemReport.objects.get().created_by, self.user)
