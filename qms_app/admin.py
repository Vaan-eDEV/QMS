from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django import forms
from django.utils.html import format_html

from .models import (
    CustomUser, Customer,
    Form, Stage, FormField, FormSubmission,
    MachineSession, FormFolder,
    QMSDocument, DocumentFolder, QMSDocumentVersion, DocumentRevision,
    CertificateCategory, Certificate
)
from .models import SignatureVerification


# =========================
# REGISTER SIMPLE MODELS
# =========================
admin.site.register(SignatureVerification)
admin.site.register(MachineSession)
admin.site.register(FormFolder)
admin.site.register(DocumentFolder)
admin.site.register(DocumentRevision)


# =========================
# CUSTOM USER ADMIN
# =========================
class CustomUserCreationForm(forms.ModelForm):
    password1 = forms.CharField(widget=forms.PasswordInput, required=False)
    password2 = forms.CharField(widget=forms.PasswordInput, required=False)

    class Meta:
        model = CustomUser
        fields = ('email', 'first_name', 'last_name', 'role')

    def clean_password2(self):
        p1 = self.cleaned_data.get("password1")
        p2 = self.cleaned_data.get("password2")
        if p1 or p2:
            if p1 != p2:
                raise forms.ValidationError("Passwords don't match")
        return p2

    def save(self, commit=True):
        user = super().save(commit=False)
        p = self.cleaned_data.get("password1")
        if p:
            user.set_password(p)
        if commit:
            user.save()
        return user


class CustomUserChangeForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ('email','first_name','last_name','role','is_active','is_staff','is_superuser')


class CustomUserAdmin(BaseUserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm

    list_display = ('email','first_name','last_name','role','is_staff')
    list_filter = ('role','is_staff','is_superuser')
    search_fields = ('email','first_name','last_name')
    ordering = ('email',)

    fieldsets = (
        (None, {'fields': ('email','password')}),
        ('Personal info', {'fields': ('first_name','last_name','role')}),
        ('Permissions', {'fields': ('is_active','is_staff','is_superuser','groups','user_permissions')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email','first_name','last_name','role','password1','password2','is_staff','is_superuser'),
        }),
    )


admin.site.register(CustomUser, CustomUserAdmin)


# =========================
# CUSTOMER ADMIN
# =========================
@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'phone')
    search_fields = ('name', 'email', 'phone')


# =========================
# FORM BUILDER ADMIN
# =========================
class FormFieldInline(admin.TabularInline):
    model = FormField
    extra = 1


class StageInline(admin.TabularInline):
    model = Stage
    extra = 1


@admin.register(Form)
class FormAdmin(admin.ModelAdmin):
    inlines = [StageInline]
    list_display = ('name', 'folder', 'description', 'created_by', 'created_at')
    search_fields = ('name',)


@admin.register(Stage)
class StageAdmin(admin.ModelAdmin):
    inlines = [FormFieldInline]
    list_display = ('name', 'form', 'order')
    list_filter = ('form',)
    search_fields = ('name',)


@admin.register(FormField)
class FormFieldAdmin(admin.ModelAdmin):
    list_display = ('label', 'stage', 'field_type', 'order')
    list_filter = ('field_type', 'stage')
    search_fields = ('label',)


@admin.register(FormSubmission)
class FormSubmissionAdmin(admin.ModelAdmin):
    list_display = ('form', 'stage', 'submitted_by', 'submitted_at')
    list_filter = ('form', 'stage', 'submitted_by')


# =========================
# CERTIFICATE ADMIN
# =========================
@admin.register(Certificate)
class CertificateAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)


# =========================
# CERTIFICATE CATEGORY ADMIN
# =========================
@admin.register(CertificateCategory)
class CertificateCategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "certificate")
    list_filter = ("certificate",)
    search_fields = ("name",)


# =========================
# QMS DOCUMENT ADMIN
# =========================
@admin.register(QMSDocument)
class QMSDocumentAdmin(admin.ModelAdmin):

    list_display = (
        "title",
        "folder",
        "created_by",
        "created_at",
        "get_certificates",
        "get_categories",
        "file_link"
    )

    search_fields = ("title",)

    list_filter = ("folder", "created_at", "certificate", "certificate_category")

    # 🔥 MULTI SELECT UI
    filter_horizontal = ("certificate", "certificate_category")

    # =========================
    # FILE LINK
    # =========================
    def file_link(self, obj):
        if obj.original_file:
            return format_html(
                '<a href="{}" target="_blank">Open</a>',
                obj.original_file.url
            )
        return "-"
    file_link.short_description = "File"

    # =========================
    # SHOW CERTIFICATES
    # =========================
    def get_certificates(self, obj):
        return ", ".join([c.name for c in obj.certificate.all()]) or "N/A"
    get_certificates.short_description = "Certificates"

    # =========================
    # SHOW CATEGORIES
    # =========================
    def get_categories(self, obj):
        return ", ".join([c.name for c in obj.certificate_category.all()]) or "N/A"
    get_categories.short_description = "Categories"


# =========================
# VERSION ADMIN
# =========================
@admin.register(QMSDocumentVersion)
class QMSDocumentVersionAdmin(admin.ModelAdmin):
    list_display = ("get_document_title","version_number","edited_by", "edited_at")
    search_fields = ("document__title","version_number")
    list_filter = ("document",)

    def get_document_title(self, obj):
        return obj.document.title if obj.document else "-"
    get_document_title.short_description = "Document"




from .models import WorkOrder, WorkOrderPart


# =========================================================
# WORK ORDER PART INLINE
# =========================================================

class WorkOrderPartInline(admin.TabularInline):

    model = WorkOrderPart

    extra = 1

    fields = (

        "part_id",

        "quantity",

        "material",

        "revision",

        "assigned_to",

        "status",

    )

    raw_id_fields = (
        "assigned_to",
    )


# =========================================================
# WORK ORDER ADMIN
# =========================================================

@admin.register(WorkOrder)
class WorkOrderAdmin(admin.ModelAdmin):

    list_display = (

        "workorder_id",

        "rfq_ref_id",

        "company_name",

        "priority",

        "status",

        "delivery_date",

        "created_by",

        "created_at",

    )

    search_fields = (

        "workorder_id",

        "rfq_ref_id",

        "company_name",

    )

    list_filter = (

        "status",

        "priority",

        "created_at",

    )

    readonly_fields = (

        "created_at",
    )

    ordering = (
        "-created_at",
    )

    inlines = [
        WorkOrderPartInline
    ]


# =========================================================
# WORK ORDER PART ADMIN
# =========================================================

@admin.register(WorkOrderPart)
class WorkOrderPartAdmin(admin.ModelAdmin):

    list_display = (

        "part_id",

        "workorder",

        "quantity",

        "assigned_to",

        "status",

        "created_at",

    )

    search_fields = (

        "part_id",

        "workorder__workorder_id",

    )

    list_filter = (

        "status",

        "created_at",

    )

    raw_id_fields = (
        "workorder",
        "assigned_to",
    )

    ordering = (
        "-created_at",
    )