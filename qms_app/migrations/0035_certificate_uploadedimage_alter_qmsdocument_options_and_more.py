from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ("qms_app", "0034_fix_batchpart_unique"),
    ]

    operations = [
        migrations.AddField(
            model_name="formbatch",
            name="rfq_ref_id",
            field=models.CharField(
                max_length=100,
                blank=True,
                null=True,
                db_index=True,
            ),
        ),
    ]

