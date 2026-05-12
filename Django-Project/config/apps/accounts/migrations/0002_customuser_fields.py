from django.db import migrations, models
class Migration(migrations.Migration):
    dependencies = [
        ("accounts", "0001_initial"),
    ]
    operations = [
        migrations.AddField(
            model_name="customuser",
            name="is_restricted",
            field=models.BooleanField(
                default=False,
                help_text="Quick lookup cache for whether user has active restrictions",
            ),
        ),
        migrations.AddField(
            model_name="customuser",
            name="last_activity",
            field=models.DateTimeField(
                null=True, blank=True, help_text="Track last active timestamp"
            ),
        ),
        migrations.AddField(
            model_name="customuser",
            name="messaging_enabled",
            field=models.BooleanField(
                default=True, help_text="Admin toggle for messaging features"
            ),
        ),
    ]
