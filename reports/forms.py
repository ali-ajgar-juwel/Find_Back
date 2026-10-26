from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from .models import ItemReport, ClaimRequest

class ItemReportForm(forms.ModelForm):
    class Meta:
        model = ItemReport
        fields = ["title", "description", "report_type", "location", "date_occurred", "category", "image"]
        widgets = {
            "date_occurred": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
            "description": forms.Textarea(attrs={"rows": 4, "class": "form-control"}),
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            if not isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs.setdefault("class", "form-control")

class SignUpForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = get_user_model()
        fields = ("username", "email")
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs["class"] = "form-control"

class ClaimRequestForm(forms.ModelForm):
    class Meta:
        model = ClaimRequest
        fields = ["message"]
        widgets = {"message": forms.Textarea(attrs={"rows": 3, "class": "form-control", "placeholder": "Explain why this item belongs to you (optional)"})}
