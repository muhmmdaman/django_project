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
            name='Document',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('description', models.TextField(blank=True)),
                ('document_type', models.CharField(choices=[('notes', 'Class Notes'), ('assignment', 'Assignment'), ('solution', 'Solution'), ('reference', 'Reference Material')], default='notes', max_length=20)),
                ('file', models.FileField(upload_to='documents/%Y/%m/%d/')),
                ('uploaded_at', models.DateTimeField(auto_now_add=True)),
                ('downloads', models.IntegerField(default=0)),
                ('subject', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='documents', to='students.subject')),
                ('uploaded_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='uploaded_documents', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Document',
                'verbose_name_plural': 'Documents',
                'ordering': ['-uploaded_at'],
            },
        ),
    ]
