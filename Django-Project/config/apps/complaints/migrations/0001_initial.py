import django.db.models.deletion
from django.db import migrations, models
class Migration(migrations.Migration):
    initial = True
    dependencies = [
        ('students', '0002_alter_marks_options_alter_student_options_and_more'),
    ]
    operations = [
        migrations.CreateModel(
            name='Complaint',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('description', models.TextField()),
                ('complaint_type', models.CharField(choices=[('infrastructure', 'Infrastructure'), ('academic', 'Academic'), ('other', 'Other')], default='other', max_length=20)),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('in_progress', 'In Progress'), ('resolved', 'Resolved')], default='pending', max_length=20)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('resolution_notes', models.TextField(blank=True, null=True)),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='complaints', to='students.student')),
            ],
            options={
                'verbose_name': 'Complaint',
                'verbose_name_plural': 'Complaints',
                'ordering': ['-created_at'],
            },
        ),
    ]
