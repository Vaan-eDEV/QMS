from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django import forms
from .models import CustomUser,Customer
from .models import Form, Stage, FormField, FormSubmission, MachineSession, FormFolder
from .models import SignatureVerification

admin.site.register(SignatureVerification)

class CustomUserCreationForm(forms.ModelForm):
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput, required=False)
    password2 = forms.CharField(label='Password confirmation', widget=forms.PasswordInput, required=False)

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
    model = CustomUser
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
@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'phone')  # Columns to display in list view
    search_fields = ('name', 'email', 'phone')  # Add search box
    list_filter = ()  # You can add filters if needed
admin.site.register(CustomUser, CustomUserAdmin)





class FormFieldInline(admin.TabularInline):
    model = FormField
    extra = 1

# Inline for Stage inside Form
class StageInline(admin.TabularInline):
    model = Stage
    extra = 1

# Form Admin
@admin.register(Form)
class FormAdmin(admin.ModelAdmin):
    inlines = [StageInline]
    list_display = ('name', 'description', 'created_by', 'created_at')
    search_fields = ('name',)

# Stage Admin
@admin.register(Stage)
class StageAdmin(admin.ModelAdmin):
    inlines = [FormFieldInline]
    list_display = ('name', 'form', 'order')
    list_filter = ('form',)
    search_fields = ('name',)

# FormField Admin
@admin.register(FormField)
class FormFieldAdmin(admin.ModelAdmin):
    list_display = ('label', 'stage', 'field_type', 'order')  # removed 'required'
    list_filter = ('field_type', 'stage')
    search_fields = ('label',)

# FormSubmission Admin
@admin.register(FormSubmission)
class FormSubmissionAdmin(admin.ModelAdmin):
    list_display = ('form', 'stage', 'submitted_by', 'submitted_at')
    list_filter = ('form', 'stage', 'submitted_by')
    search_fields = ('form__name', 'stage__name', 'submitted_by__username')
    
    
admin.site.register(MachineSession)
admin.site.register(FormFolder)