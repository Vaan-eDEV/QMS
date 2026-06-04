from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('qms_app', '0031_certificate_uploadedimage_alter_qmsdocument_options_and_more'),
    ]

    operations = [

        migrations.AddField(
            model_name='workorderpart',
            name='stage_folder',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to='qms_app.formfolder',
            ),
        ),

    ]