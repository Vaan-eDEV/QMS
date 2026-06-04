from django.contrib import admin
from django.utils.html import format_html
from .models import Employee, EmployeeCertificate,Test, StudyMaterial

admin.site.register(Test)
admin.site.register(StudyMaterial)

# ================= CERTIFICATE INLINE =================
class EmployeeCertificateInline(admin.TabularInline):
    model = EmployeeCertificate
    extra = 0
    readonly_fields = ("file_preview", "uploaded_at")
    fields = ("certificate_name", "file", "file_preview", "uploaded_at")

    def file_preview(self, obj):
        if obj.file:
            return format_html(
                '<a href="{}" target="_blank">View</a>',
                obj.file.url
            )
        return "-"
    file_preview.short_description = "Preview"


# ================= EMPLOYEE ADMIN =================
@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):

    # 🔥 LIST VIEW
    list_display = (
        "emp_id",
        "profile_preview",
        "name",
        "email",
        "user",
        "department",
        "role",
        "status",
    )

    list_filter = ("department", "status", "role")
    search_fields = ("emp_id", "name", "email")
    ordering = ("-created_at",)

    # 🔥 IMAGE PREVIEW
    def profile_preview(self, obj):
        if obj.profile_image:
            return format_html(
                '<img src="{}" width="40" height="40" style="border-radius:50%;object-fit:cover;" />',
                obj.profile_image.url
            )
        return "—"
    profile_preview.short_description = "Photo"

    # 🔥 READONLY
    readonly_fields = ("created_at", "profile_image_preview")

    # 🔥 FIELDSETS
    fieldsets = (

        ("👤 Basic Info", {
            "fields": (
                "profile_image",
                "profile_image_preview",
                "emp_id",
                "name",
                "email",
                "user",
                "status",
            )
        }),

        ("📌 Personal", {
            "fields": (
                "dob", "gender", "marital_status",
                "nationality", "blood_group",
                "qualification", "skills", "experience", "notes"
            )
        }),

        ("🪪 Government IDs", {
            "fields": (
                "pan_number", "aadhar_number",
                "uan_number", "pf_number", "esi_number"
            )
        }),

        ("📞 Contact", {
            "fields": ("mobile_number", "alternate_number")
        }),

        ("🏠 Address", {
            "fields": ("current_address", "permanent_address")
        }),

        ("💼 Employment", {
            "fields": (
                "department", "role", "date_of_joining",
                "employment_type", "work_location",
                "shift", "cost_center", "reporting_manager"
            )
        }),

        ("🏦 Bank", {
            "fields": (
                "bank_name", "branch_name",
                "account_number", "account_type", "ifsc_code"
            )
        }),

        ("💰 Salary", {
            "fields": (
                "pay_grade", "basic_salary",
                "effective_date", "payment_cycle"
            )
        }),

        ("🚨 Emergency", {
            "fields": (
                "emergency_contact_name",
                "emergency_relationship",
                "emergency_mobile",
                "emergency_alternate",
                "emergency_address"
            )
        }),

        ("⚙️ System", {
            "fields": ("created_at",)
        }),
    )

    # 🔥 INLINE CERTIFICATES
    inlines = [EmployeeCertificateInline]

    # 🔥 IMAGE PREVIEW IN FORM
    def profile_image_preview(self, obj):
        if obj.profile_image:
            return format_html(
                '<img src="{}" width="120" style="border-radius:10px;" />',
                obj.profile_image.url
            )
        return "No Image"
    profile_image_preview.short_description = "Profile Preview"