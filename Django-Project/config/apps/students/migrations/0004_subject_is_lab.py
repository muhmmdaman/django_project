from django.db import migrations, models
class Migration(migrations.Migration):
    dependencies = [
        ('students', '0003_teacher_attendance'),
    ]
    operations = [
        migrations.AddField(
            model_name='subject',
            name='is_lab',
            field=models.BooleanField(default=False, help_text='True if this is a lab/practical subject'),
        ),
    ]
