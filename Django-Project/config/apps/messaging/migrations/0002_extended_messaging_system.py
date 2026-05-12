from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('messaging', '0001_initial'),
    ]
    operations = [
        migrations.CreateModel(
            name='ActivityLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('action_type', models.CharField(choices=[('login', 'Login'), ('logout', 'Logout'), ('message_sent', 'Message Sent'), ('broadcast_sent', 'Broadcast Sent'), ('department_message_sent', 'Department Message Sent'), ('message_deleted', 'Message Deleted'), ('message_recovered', 'Message Recovered'), ('user_banned', 'User Banned'), ('user_unbanned', 'User Unbanned'), ('user_muted', 'User Muted'), ('user_unmuted', 'User Unmuted')], help_text='Type of action performed', max_length=30)),
                ('old_value', models.TextField(blank=True, null=True)),
                ('new_value', models.TextField(blank=True, null=True)),
                ('ip_address', models.CharField(blank=True, max_length=45, null=True)),
                ('user_agent', models.CharField(blank=True, max_length=500, null=True)),
                ('status_code', models.IntegerField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('timestamp_range', models.DateTimeField(blank=True, null=True)),
                ('metadata', models.JSONField(blank=True, default=dict)),
            ],
            options={
                'verbose_name': 'Activity Log',
                'verbose_name_plural': 'Activity Logs',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='BroadcastRecipient',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('receiver_type', models.CharField(choices=[('individual_broadcast', 'Individual Broadcast'), ('department_broadcast', 'Department Broadcast'), ('global_broadcast', 'Global Broadcast'), ('admin_broadcast', 'Admin Broadcast')], help_text='Type of broadcast message', max_length=30)),
                ('is_delivered', models.BooleanField(default=True)),
                ('is_read', models.BooleanField(default=False)),
                ('read_at', models.DateTimeField(blank=True, null=True)),
                ('delivery_error', models.TextField(blank=True, null=True)),
                ('delivery_timestamp', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'verbose_name': 'Broadcast Recipient',
                'verbose_name_plural': 'Broadcast Recipients',
                'ordering': ['-delivery_timestamp'],
            },
        ),
        migrations.CreateModel(
            name='MessageRecipientGroup',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('recipient_type', models.CharField(choices=[('department', 'Department'), ('all_students', 'All Students'), ('all_users', 'All Users'), ('custom_list', 'Custom List')], help_text='Type of recipient group', max_length=20)),
                ('department', models.CharField(blank=True, help_text='Department filter if applicable', max_length=10, null=True)),
                ('total_recipients', models.IntegerField(help_text='Total number of recipients in group')),
                ('delivered_count', models.IntegerField(default=0)),
                ('failed_count', models.IntegerField(default=0)),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('in_progress', 'In Progress'), ('completed', 'Completed'), ('failed', 'Failed')], default='pending', max_length=20)),
                ('started_at', models.DateTimeField(auto_now_add=True)),
                ('completed_at', models.DateTimeField(blank=True, null=True)),
                ('error_log', models.TextField(blank=True, null=True)),
            ],
            options={
                'verbose_name': 'Message Recipient Group',
                'verbose_name_plural': 'Message Recipient Groups',
                'ordering': ['-started_at'],
            },
        ),
        migrations.CreateModel(
            name='UserRestriction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('restriction_type', models.CharField(choices=[('banned', 'Banned'), ('muted', 'Muted'), ('blocked_by_admin', 'Blocked By Admin')], help_text='Type of restriction', max_length=20)),
                ('reason', models.TextField(help_text='Reason for restriction')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('expires_at', models.DateTimeField(blank=True, null=True)),
                ('is_active', models.BooleanField(default=True)),
                ('can_receive_broadcasts', models.BooleanField(default=False)),
                ('can_send_messages', models.BooleanField(default=False)),
            ],
            options={
                'verbose_name': 'User Restriction',
                'verbose_name_plural': 'User Restrictions',
                'ordering': ['-created_at'],
            },
        ),
        migrations.AddField(
            model_name='message',
            name='created_via',
            field=models.CharField(choices=[('ui', 'UI'), ('api', 'API'), ('bulk_upload', 'Bulk Upload')], default='ui', help_text='Channel through which message was created', max_length=20),
        ),
        migrations.AddField(
            model_name='message',
            name='deleted_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='message',
            name='deleted_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='deleted_messages', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='message',
            name='is_broadcast_optimized',
            field=models.BooleanField(default=False, help_text='True if this is an optimized broadcast message'),
        ),
        migrations.AddField(
            model_name='message',
            name='is_deleted',
            field=models.BooleanField(default=False, help_text='Soft delete flag'),
        ),
        migrations.AddField(
            model_name='message',
            name='metadata',
            field=models.JSONField(blank=True, default=dict, help_text='Additional metadata for the message'),
        ),
        migrations.AddField(
            model_name='message',
            name='receiver_type',
            field=models.CharField(choices=[('individual', 'Individual'), ('department', 'Department'), ('all_users', 'All Users'), ('custom', 'Custom List')], default='individual', help_text='Type of receiver for this message', max_length=20),
        ),
        migrations.AlterField(
            model_name='message',
            name='receiver',
            field=models.ForeignKey(blank=True, help_text='For individual messages only', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='received_messages', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddIndex(
            model_name='message',
            index=models.Index(fields=['-timestamp'], name='messaging_m_timesta_44a7ea_idx'),
        ),
        migrations.AddIndex(
            model_name='message',
            index=models.Index(fields=['sender', '-timestamp'], name='messaging_m_sender__ef92c2_idx'),
        ),
        migrations.AddIndex(
            model_name='message',
            index=models.Index(fields=['receiver', '-timestamp'], name='messaging_m_receive_8ce8b1_idx'),
        ),
        migrations.AddIndex(
            model_name='message',
            index=models.Index(fields=['is_deleted'], name='messaging_m_is_dele_12264e_idx'),
        ),
        migrations.AddField(
            model_name='userrestriction',
            name='restricted_by',
            field=models.ForeignKey(help_text='Admin who created the restriction', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='restrictions_created', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='userrestriction',
            name='user',
            field=models.ForeignKey(help_text='User being restricted', on_delete=django.db.models.deletion.CASCADE, related_name='restrictions', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='messagerecipientgroup',
            name='message',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='recipient_groups', to='messaging.message'),
        ),
        migrations.AddField(
            model_name='broadcastrecipient',
            name='message',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='broadcast_recipients', to='messaging.message'),
        ),
        migrations.AddField(
            model_name='broadcastrecipient',
            name='recipient',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='received_broadcasts', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='activitylog',
            name='message',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='activity_logs', to='messaging.message'),
        ),
        migrations.AddField(
            model_name='activitylog',
            name='target_user',
            field=models.ForeignKey(blank=True, help_text='User who is the target of the action', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='target_activity_logs', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='activitylog',
            name='user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='activity_logs', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddIndex(
            model_name='userrestriction',
            index=models.Index(fields=['user', 'is_active'], name='messaging_u_user_id_0c3547_idx'),
        ),
        migrations.AddIndex(
            model_name='userrestriction',
            index=models.Index(fields=['restriction_type', 'is_active'], name='messaging_u_restric_cae2bb_idx'),
        ),
        migrations.AddIndex(
            model_name='userrestriction',
            index=models.Index(fields=['expires_at'], name='messaging_u_expires_3bdf8f_idx'),
        ),
        migrations.AlterUniqueTogether(
            name='userrestriction',
            unique_together={('user', 'restriction_type')},
        ),
        migrations.AddIndex(
            model_name='messagerecipientgroup',
            index=models.Index(fields=['message', 'status'], name='messaging_m_message_75a6b7_idx'),
        ),
        migrations.AddIndex(
            model_name='messagerecipientgroup',
            index=models.Index(fields=['status'], name='messaging_m_status_1a230e_idx'),
        ),
        migrations.AddIndex(
            model_name='broadcastrecipient',
            index=models.Index(fields=['message', 'recipient'], name='messaging_b_message_b685c4_idx'),
        ),
        migrations.AddIndex(
            model_name='broadcastrecipient',
            index=models.Index(fields=['recipient', 'is_read'], name='messaging_b_recipie_c685b9_idx'),
        ),
        migrations.AddIndex(
            model_name='broadcastrecipient',
            index=models.Index(fields=['is_delivered'], name='messaging_b_is_deli_084698_idx'),
        ),
        migrations.AlterUniqueTogether(
            name='broadcastrecipient',
            unique_together={('message', 'recipient')},
        ),
        migrations.AddIndex(
            model_name='activitylog',
            index=models.Index(fields=['-created_at'], name='messaging_a_created_20b111_idx'),
        ),
        migrations.AddIndex(
            model_name='activitylog',
            index=models.Index(fields=['user', '-created_at'], name='messaging_a_user_id_a510c5_idx'),
        ),
        migrations.AddIndex(
            model_name='activitylog',
            index=models.Index(fields=['action_type', '-created_at'], name='messaging_a_action__b5470f_idx'),
        ),
        migrations.AddIndex(
            model_name='activitylog',
            index=models.Index(fields=['target_user', '-created_at'], name='messaging_a_target__f55aad_idx'),
        ),
    ]
