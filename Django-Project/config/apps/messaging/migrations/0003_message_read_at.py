from django.db import migrations, models
class Migration(migrations.Migration):
    dependencies = [
        ('messaging', '0002_extended_messaging_system'),
    ]
    operations = [
        migrations.AddField(
            model_name='message',
            name='read_at',
            field=models.DateTimeField(blank=True, help_text='Timestamp when message was read by recipient', null=True),
        ),
    ]
