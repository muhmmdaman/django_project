from django.db import migrations, models
class Migration(migrations.Migration):
    dependencies = [
        ('students', '0005_salarypayment_alter_teacher_options_and_more'),
    ]
    operations = [
        migrations.AlterField(
            model_name='student',
            name='class_name',
            field=models.CharField(choices=[('CSE', 'Computer Science'), ('IT', 'Information Technology'), ('ECE', 'Electronics'), ('EEE', 'Electrical'), ('ME', 'Mechanical'), ('CE', 'Civil'), ('BBA', 'BBA'), ('MBA', 'MBA'), ('BCA', 'BCA'), ('MCA', 'MCA'), ('BA', 'BA'), ('BSc', 'BSc'), ('BTech', 'BTech')], default='CSE', max_length=10),
        ),
        migrations.AlterField(
            model_name='student',
            name='department',
            field=models.CharField(choices=[('CSE', 'Computer Science & Engineering'), ('IT', 'Information Technology'), ('ECE', 'Electronics & Communication'), ('EEE', 'Electrical & Electronics'), ('ME', 'Mechanical Engineering'), ('CE', 'Civil Engineering'), ('BBA', 'Bachelor of Business Administration'), ('MBA', 'Master of Business Administration'), ('BCA', 'Bachelor of Computer Applications'), ('MCA', 'Master of Computer Applications'), ('BA', 'Bachelor of Arts'), ('BSc', 'Bachelor of Science'), ('BTech', 'Bachelor of Technology')], default='CSE', max_length=10),
        ),
        migrations.AlterField(
            model_name='subject',
            name='department',
            field=models.CharField(choices=[('CSE', 'Computer Science & Engineering'), ('IT', 'Information Technology'), ('ECE', 'Electronics & Communication'), ('EEE', 'Electrical & Electronics'), ('ME', 'Mechanical Engineering'), ('CE', 'Civil Engineering'), ('BBA', 'Bachelor of Business Administration'), ('MBA', 'Master of Business Administration'), ('BCA', 'Bachelor of Computer Applications'), ('MCA', 'Master of Computer Applications'), ('BA', 'Bachelor of Arts'), ('BSc', 'Bachelor of Science'), ('BTech', 'Bachelor of Technology'), ('GEN', 'General (All Departments)')], default='GEN', max_length=10),
        ),
        migrations.AlterField(
            model_name='teacher',
            name='department',
            field=models.CharField(choices=[('CSE', 'Computer Science & Engineering'), ('IT', 'Information Technology'), ('ECE', 'Electronics & Communication'), ('EEE', 'Electrical & Electronics'), ('ME', 'Mechanical Engineering'), ('CE', 'Civil Engineering'), ('BBA', 'Bachelor of Business Administration'), ('MBA', 'Master of Business Administration'), ('BCA', 'Bachelor of Computer Applications'), ('MCA', 'Master of Computer Applications'), ('BA', 'Bachelor of Arts'), ('BSc', 'Bachelor of Science'), ('BTech', 'Bachelor of Technology')], default='CSE', max_length=10),
        ),
    ]
