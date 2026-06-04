from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('qms_app', '0029_workorder_setup'),
    ]

    operations = [

        migrations.CreateModel(
            name='WorkOrderPartFormSubmission',
            fields=[
                ('id', models.BigAutoField(
                    auto_created=True,
                    primary_key=True,
                    serialize=False,
                    verbose_name='ID'
                )),

                ('submitted_at', models.DateTimeField(
                    auto_now_add=True
                )),

                ('form', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    to='qms_app.form'
                )),

                ('form_submission', models.ForeignKey(
                    blank=True,
                    null=True,
                    on_delete=django.db.models.deletion.CASCADE,
                    to='qms_app.formsubmission'
                )),

                ('submitted_by', models.ForeignKey(
                    blank=True,
                    null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    to=settings.AUTH_USER_MODEL
                )),

                ('workorder_part', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='qms_forms',
                    to='qms_app.WorkOrderPart'
                )),
            ],

            options={
                'unique_together': {
                    ('workorder_part', 'form')
                },
            },
        ),
    ]