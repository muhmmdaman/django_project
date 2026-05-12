from django.db import migrations, models
class Migration(migrations.Migration):
    dependencies = [
        ('accounts', '0002_customuser_fields'),
    ]
    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='role',
            field=models.CharField(choices=[('student', 'Student'), ('teacher', 'Teacher'), ('admin', 'Administrator')], default='student', max_length=10),
        ),
    ]
