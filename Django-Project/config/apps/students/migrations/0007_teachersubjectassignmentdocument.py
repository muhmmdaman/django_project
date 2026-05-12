from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('students', '0006_alter_student_class_name_alter_student_department_and_more'),
    ]
    operations = [
        migrations.CreateModel(
            name='TeacherSubjectAssignmentDocument',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('document', models.FileField(help_text='Assignment letter or documentation', upload_to='teacher_documents/%Y/%m/%d/')),
                ('document_name', models.CharField(help_text='Name/title of the document', max_length=255)),
                ('status', models.CharField(choices=[('pending', 'Pending Review'), ('approved', 'Approved'), ('rejected', 'Rejected')], default='pending', help_text='Approval status of the document', max_length=10)),
                ('uploaded_at', models.DateTimeField(auto_now_add=True, help_text='When the document was uploaded')),
                ('approval_notes', models.TextField(blank=True, help_text='Notes from admin during approval/rejection')),
                ('approved_by', models.ForeignKey(blank=True, help_text='Admin who approved this document', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='approved_teacher_documents', to=settings.AUTH_USER_MODEL)),
                ('subjects', models.ManyToManyField(help_text='Subjects to be assigned based on this document', to='students.subject')),
                ('teacher', models.ForeignKey(help_text='Teacher uploading the document', on_delete=django.db.models.deletion.CASCADE, related_name='subject_assignment_documents', to='students.teacher')),
            ],
            options={
                'verbose_name': 'Teacher Subject Assignment Document',
                'verbose_name_plural': 'Teacher Subject Assignment Documents',
                'ordering': ['-uploaded_at'],
                'indexes': [models.Index(fields=['teacher', '-uploaded_at'], name='students_te_teacher_baf074_idx'), models.Index(fields=['status'], name='students_te_status_cb987f_idx')],
            },
        ),
    ]
