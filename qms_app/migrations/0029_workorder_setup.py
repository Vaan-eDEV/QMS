from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('qms_app', '0028_certificate_remove_qmsdocument_certificate_and_more'),
    ]

    operations = [

        migrations.CreateModel(
            name='WorkOrder',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rfq_ref_id', models.CharField(max_length=100)),
                ('company_name', models.CharField(max_length=255)),
                ('workorder_id', models.CharField(max_length=100, unique=True)),
                ('created_by', models.ForeignKey(
                    null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    to=settings.AUTH_USER_MODEL
                )),
            ],
        ),

        migrations.CreateModel(
            name='WorkOrderPart',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('part_id', models.CharField(max_length=100)),

                ('workorder', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='parts',
                    to='qms_app.workorder'
                )),
            ],
        ),
    ]