from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("portal", "0001_initial_portal_models")]

    operations = [
        migrations.AddField(
            model_name="activitymedia",
            name="height",
            field=models.PositiveIntegerField(
                blank=True,
                editable=False,
                null=True,
                verbose_name="媒体高度",
            ),
        ),
        migrations.AddField(
            model_name="activitymedia",
            name="width",
            field=models.PositiveIntegerField(
                blank=True,
                editable=False,
                null=True,
                verbose_name="媒体宽度",
            ),
        ),
    ]
