from django.db import migrations, models
class Migration(migrations.Migration):
    dependencies = [
        ('messaging', '0003_message_read_at'),
    ]
    operations = [
        migrations.AlterField(
            model_name='activitylog',
            name='action_type',
            field=models.CharField(choices=[('login', 'Login'), ('logout', 'Logout'), ('message_sent', 'Message Sent'), ('broadcast_sent', 'Broadcast Sent'), ('department_message_sent', 'Department Message Sent'), ('message_deleted', 'Message Deleted'), ('message_recovered', 'Message Recovered'), ('user_banned', 'User Banned'), ('user_unbanned', 'User Unbanned'), ('user_muted', 'User Muted'), ('user_unmuted', 'User Unmuted'), ('teacher_added', 'Teacher Added'), ('teacher_updated', 'Teacher Updated'), ('teacher_deleted', 'Teacher Deleted'), ('teacher_salary_paid', 'Teacher Salary Paid'), ('user_promoted_to_admin', 'User Promoted to Admin'), ('user_demoted_from_admin', 'User Demoted from Admin')], help_text='Type of action performed', max_length=30),
        ),
    ]
