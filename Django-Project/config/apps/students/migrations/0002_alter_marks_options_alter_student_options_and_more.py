import django.core.validators
import django.db.models.deletion
from django.db import migrations, models
class Migration(migrations.Migration):
    dependencies = [
        ('students', '0001_initial'),
    ]
    operations = [
        migrations.AlterModelOptions(
            name='marks',
            options={'ordering': ['-exam_date', 'student', 'subject'], 'verbose_name': 'Marks', 'verbose_name_plural': 'Marks'},
        ),
        migrations.AlterModelOptions(
            name='student',
            options={'ordering': ['-enrolled_date', 'user__first_name']},
        ),
        migrations.AlterModelOptions(
            name='subject',
            options={'ordering': ['department', 'semester', 'name']},
        ),
        migrations.AlterUniqueTogether(
            name='marks',
            unique_together=set(),
        ),
        migrations.AddField(
            model_name='marks',
            name='exam_type',
            field=models.CharField(choices=[('MID1', 'Mid Semester 1'), ('MID2', 'Mid Semester 2'), ('END', 'End Semester'), ('INTERNAL', 'Internal Assessment')], default='END', max_length=10),
        ),
        migrations.AddField(
            model_name='student',
            name='cgpa',
            field=models.FloatField(blank=True, help_text='Cumulative Grade Point Average (0-10)', null=True, validators=[django.core.validators.MinValueValidator(0.0), django.core.validators.MaxValueValidator(10.0)]),
        ),
        migrations.AddField(
            model_name='student',
            name='department',
            field=models.CharField(choices=[('CSE', 'Computer Science & Engineering'), ('IT', 'Information Technology'), ('ECE', 'Electronics & Communication'), ('EEE', 'Electrical & Electronics'), ('ME', 'Mechanical Engineering'), ('CE', 'Civil Engineering'), ('MBA', 'Business Administration')], default='CSE', max_length=10),
        ),
        migrations.AddField(
            model_name='student',
            name='enrollment_number',
            field=models.CharField(blank=True, default='', help_text='Unique enrollment/registration number', max_length=20, unique=True),
        ),
        migrations.AddField(
            model_name='student',
            name='semester',
            field=models.IntegerField(default=1, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(8)]),
        ),
        migrations.AddField(
            model_name='subject',
            name='credits',
            field=models.IntegerField(default=3, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(6)]),
        ),
        migrations.AddField(
            model_name='subject',
            name='department',
            field=models.CharField(choices=[('CSE', 'Computer Science & Engineering'), ('IT', 'Information Technology'), ('ECE', 'Electronics & Communication'), ('EEE', 'Electrical & Electronics'), ('ME', 'Mechanical Engineering'), ('CE', 'Civil Engineering'), ('MBA', 'Business Administration'), ('GEN', 'General (All Departments)')], default='GEN', max_length=10),
        ),
        migrations.AddField(
            model_name='subject',
            name='semester',
            field=models.IntegerField(default=1, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(8)]),
        ),
        migrations.AlterField(
            model_name='student',
            name='class_name',
            field=models.CharField(choices=[('CSE', 'Computer Science'), ('IT', 'Information Technology'), ('ECE', 'Electronics'), ('EEE', 'Electrical'), ('ME', 'Mechanical'), ('CE', 'Civil'), ('MBA', 'MBA')], default='CSE', max_length=10),
        ),
        migrations.AlterField(
            model_name='subject',
            name='name',
            field=models.CharField(max_length=100),
        ),
        migrations.AlterUniqueTogether(
            name='marks',
            unique_together={('student', 'subject', 'exam_type')},
        ),
        migrations.AlterUniqueTogether(
            name='subject',
            unique_together={('code', 'department')},
        ),
        migrations.CreateModel(
            name='PerformanceHistory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('semester', models.IntegerField(validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(8)])),
                ('sgpa', models.FloatField(help_text='Semester Grade Point Average', validators=[django.core.validators.MinValueValidator(0.0), django.core.validators.MaxValueValidator(10.0)])),
                ('cgpa', models.FloatField(help_text='Cumulative Grade Point Average at this point', validators=[django.core.validators.MinValueValidator(0.0), django.core.validators.MaxValueValidator(10.0)])),
                ('attendance', models.FloatField(validators=[django.core.validators.MinValueValidator(0.0), django.core.validators.MaxValueValidator(100.0)])),
                ('total_credits', models.IntegerField(default=0)),
                ('recorded_at', models.DateTimeField(auto_now_add=True)),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='performance_history', to='students.student')),
            ],
            options={
                'verbose_name_plural': 'Performance Histories',
                'ordering': ['student', 'semester'],
                'unique_together': {('student', 'semester')},
            },
        ),
    ]
