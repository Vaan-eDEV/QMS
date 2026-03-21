from django import forms
from django.contrib.auth.forms import AuthenticationForm
from .models import CustomUser,Customer
from .models import QMSDocument, QMSDocumentVersion, Form, Stage, FormSubmission



# ==============================================================================================
#----------------------------- Register Form ---------------------------------------------------
#===============================================================================================
class RegisterForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, label="Password")

    class Meta:
        model = CustomUser
        fields = ['email','first_name','last_name','role','password']


        


# ==============================================================================================
#----------------------------- LogIn  Form -----------------------------------------------------
#===============================================================================================

class LoginForm(AuthenticationForm):
    username = forms.EmailField(label='Email')


# ==============================================================================================
#----------------------------- QMS Process Form ------------------------------------------------
#===============================================================================================

# class QMSProcessForm(forms.ModelForm):
#     class Meta:
#         model = QMSProcess
#         fields = ['customer', 'customer_name', 'rfq_no', 'po_no', 'stage']
#         widgets = {
#             'customer': forms.Select(attrs={'class': 'form-select', 'placeholder': 'Select a Customer'}),
#             'customer_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Customer Name (optional)'}),
#             'rfq_no': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter RFQ Number'}),
#             'po_no': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter PO Number'}),
#             'stage': forms.Select(attrs={'class': 'form-select'}),
#         }

#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         self.fields['customer'].required = False
#         self.fields['customer_name'].required = False
#         self.fields['customer'].queryset = Customer.objects.all()
#         self.fields['stage'].initial = 'rfq_po'

#     def save(self, commit=True):
#         instance = super().save(commit=False)
#         if instance.customer:
#             instance.customer_name = instance.customer.name
#         if commit:
#             instance.save()
#         return instance

# ==============================================================================================
#----------------------------- QMS Process Form ------------------------------------------------
#===============================================================================================

def generate_form(stage, data=None):
    from django import forms

    fields = {}

    for field in stage.fields.all().order_by('order'):
        if field.field_type == 'text':
            fields[field.label] = forms.CharField(required=False)
        elif field.field_type == 'textarea':
            fields[field.label] = forms.CharField(widget=forms.Textarea, required=False)
        elif field.field_type == 'number':
            fields[field.label] = forms.IntegerField(required=False)
        elif field.field_type == 'date':
            fields[field.label] = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), required=False)
        elif field.field_type == 'select':
            choices = [(opt.strip(), opt.strip()) for opt in (field.options or '').split(',')]
            fields[field.label] = forms.ChoiceField(choices=choices, required=False)
        elif field.field_type == 'checkbox':
            fields[field.label] = forms.BooleanField(required=False)

    DynamicStageForm = type('DynamicStageForm', (forms.Form,), fields)
    return DynamicStageForm(data)



from django import forms
from .models import CAPA


class CAPAForm(forms.ModelForm):

    class Meta:
        model = CAPA

        # Exclude auto fields
        exclude = [
            "created_by",
            "created_at",
            "closed_at",
            "capa_number",
            "risk_score",
        ]

        widgets = {
            "due_date": forms.DateInput(
                attrs={"type": "date", "class": "form-control"}
            ),

            "problem_statement": forms.Textarea(
                attrs={"rows": 3, "class": "form-control"}
            ),

            "root_cause_analysis": forms.Textarea(
                attrs={"rows": 4, "class": "form-control"}
            ),

            "five_why_analysis": forms.Textarea(
                attrs={"rows": 4, "class": "form-control"}
            ),

            "corrective_action": forms.Textarea(
                attrs={"rows": 4, "class": "form-control"}
            ),

            "preventive_action": forms.Textarea(
                attrs={"rows": 4, "class": "form-control"}
            ),

            "effectiveness_validation": forms.Textarea(
                attrs={"rows": 4, "class": "form-control"}
            ),
        }

    # =====================================================
    # FORM INITIALIZATION
    # =====================================================
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for name, field in self.fields.items():

            # Skip already styled
            if "class" in field.widget.attrs:
                continue

            if isinstance(field.widget, forms.Select):
                field.widget.attrs.update({"class": "form-select"})
            else:
                field.widget.attrs.update({"class": "form-control"})

        # Industry-Friendly Labels (AS9100D Language)
        self.fields["problem_statement"].label = "Problem Statement"
        self.fields["root_cause_analysis"].label = "Root Cause Analysis"
        self.fields["five_why_analysis"].label = "5 Why Analysis"
        self.fields["corrective_action"].label = "Corrective Action Plan"
        self.fields["preventive_action"].label = "Preventive Action Plan"
        self.fields["effectiveness_validation"].label = "Effectiveness Verification"

        self.fields["severity_score"].label = "Severity (1-5)"
        self.fields["occurrence_score"].label = "Occurrence (1-5)"
        self.fields["detection_score"].label = "Detection (1-5)"

        self.fields["related_batch_part"].label = "Related Production Part"
        self.fields["related_ncr"].label = "Linked NCR"
        self.fields["assigned_to"].label = "Responsible Person"
