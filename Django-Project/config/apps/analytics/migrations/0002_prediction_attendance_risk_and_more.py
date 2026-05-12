from django.db import migrations, models
class Migration(migrations.Migration):
    dependencies = [
        ('analytics', '0001_initial'),
    ]
    operations = [
        migrations.AddField(
            model_name='prediction',
            name='attendance_risk',
            field=models.BooleanField(default=False, help_text='True if attendance is below 75%'),
        ),
        migrations.AddField(
            model_name='prediction',
            name='performance_trend',
            field=models.CharField(choices=[('improving', 'Improving'), ('stable', 'Stable'), ('declining', 'Declining'), ('new', 'New Student')], default='new', max_length=20),
        ),
        migrations.AddField(
            model_name='prediction',
            name='predicted_cgpa',
            field=models.FloatField(default=0.0, help_text='Predicted CGPA (0-10)'),
        ),
        migrations.AddField(
            model_name='prediction',
            name='suggestions',
            field=models.TextField(blank=True, help_text='AI-generated suggestions for improvement'),
        ),
        migrations.AddField(
            model_name='prediction',
            name='weak_subjects',
            field=models.JSONField(blank=True, default=list, help_text='List of weak subjects'),
        ),
        migrations.AlterField(
            model_name='prediction',
            name='risk_level',
            field=models.CharField(choices=[('low', 'Low Risk'), ('medium', 'Medium Risk'), ('high', 'High Risk'), ('critical', 'Critical Risk')], default='low', max_length=10),
        ),
    ]
