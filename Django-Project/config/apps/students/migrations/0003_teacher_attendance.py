import django.core.validators
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models
class Migration(migrations.Migration):
    dependencies = [
        ('students', '0002_alter_marks_options_alter_student_options_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]
    operations = [
        migrations.CreateModel(
            name='Teacher',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('employee_id', models.CharField(help_text='Unique employee/faculty ID', max_length=20, unique=True)),
                ('department', models.CharField(choices=[('CSE', 'Computer Science & Engineering'), ('IT', 'Information Technology'), ('ECE', 'Electronics & Communication'), ('EEE', 'Electrical & Electronics'), ('ME', 'Mechanical Engineering'), ('CE', 'Civil Engineering'), ('MBA', 'Business Administration')], default='CSE', max_length=10)),
                ('designation', models.CharField(default='Assistant Professor', help_text='e.g., Professor, Assistant Professor, Lecturer', max_length=50)),
                ('phone', models.CharField(blank=True, max_length=15)),
                ('joined_date', models.DateField(auto_now_add=True)),
                ('subjects', models.ManyToManyField(blank=True, help_text='Subjects taught by this teacher', related_name='teachers', to='students.subject')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='teacher_profile', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['department', 'user__first_name'],
            },
        ),
        migrations.CreateModel(
            name='Attendance',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('semester', models.IntegerField(validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(8)])),
                ('total_classes', models.IntegerField(default=0, help_text='Total classes conducted', validators=[django.core.validators.MinValueValidator(0)])),
                ('attended_classes', models.IntegerField(default=0, help_text='Classes attended by student', validators=[django.core.validators.MinValueValidator(0)])),
                ('percentage', models.FloatField(default=0.0, help_text='Attendance percentage (auto-calculated)', validators=[django.core.validators.MinValueValidator(0.0), django.core.validators.MaxValueValidator(100.0)])),
                ('recorded_at', models.DateTimeField(auto_now=True)),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='attendance_records', to='students.student')),
                ('subject', models.ForeignKey(blank=True, help_text='Optional: Track attendance per subject', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='attendance_records', to='students.subject')),
            ],
            options={
                'verbose_name_plural': 'Attendance Records',
                'ordering': ['student', 'semester', 'subject'],
                'unique_together': {('student', 'semester', 'subject')},
            },
        ),
    ]
