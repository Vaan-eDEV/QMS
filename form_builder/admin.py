from django.contrib import admin
from .models import Form, Stage, Field, Table, TableColumn, FormResponse
# Register your models here.
admin.site.register(Form)
admin.site.register(Stage)
admin.site.register(Field)
admin.site.register(Table)
admin.site.register(TableColumn)
admin.site.register(FormResponse)