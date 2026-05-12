import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models
class Migration(migrations.Migration):
    initial = True
    dependencies = [
        ('students', '0002_alter_marks_options_alter_student_options_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]
    operations = [
        migrations.CreateModel(
            name='TimeSlot',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('day_of_week', models.CharField(choices=[('monday', 'Monday'), ('tuesday', 'Tuesday'), ('wednesday', 'Wednesday'), ('thursday', 'Thursday'), ('friday', 'Friday'), ('saturday', 'Saturday')], max_length=10)),
                ('start_time', models.TimeField()),
                ('end_time', models.TimeField()),
                ('room_number', models.CharField(blank=True, max_length=50)),
                ('department', models.CharField(max_length=10)),
                ('semester', models.IntegerField()),
                ('faculty', models.ForeignKey(blank=True, limit_choices_to={'role': 'teacher'}, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='teaching_slots', to=settings.AUTH_USER_MODEL)),
                ('subject', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='time_slots', to='students.subject')),
            ],
            options={
                'verbose_name': 'Time Slot',
                'verbose_name_plural': 'Time Slots',
                'ordering': ['day_of_week', 'start_time'],
                'unique_together': {('subject', 'day_of_week', 'start_time', 'semester')},
            },
        ),
    ]
