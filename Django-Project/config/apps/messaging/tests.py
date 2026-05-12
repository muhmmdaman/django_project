"""Comprehensive integration tests for the messaging system.
Tests all core functionality including messaging, broadcasting, restrictions, and activity logging.
"""
from django.test import TestCase
from django.utils import timezone
from django.contrib.auth import get_user_model
from accounts.models import CustomUser
from students.models import Student
from messaging.models import (
    Message, ActivityLog, UserRestriction,
    BroadcastRecipient, MessageRecipientGroup
)
User = get_user_model()
class MessagingSystemTestSetup(TestCase):
    def setUp(self):
        self.admin_user = CustomUser.objects.create_user(
            username='admin_test',
            email='admin@test.com',
            password='admin123',
            role='admin'
        )
        self.teacher1 = CustomUser.objects.create_user(
            username='teacher1',
            email='teacher1@test.com',
            password='teacher123',
            role='teacher'
        )
        self.teacher2 = CustomUser.objects.create_user(
            username='teacher2',
            email='teacher2@test.com',
            password='teacher123',
            role='teacher'
        )
        self.student1 = CustomUser.objects.create_user(
            username='student1',
            email='student1@test.com',
            password='student123',
            role='student'
        )
        Student.objects.create(
            user=self.student1,
            enrollment_number='CS001',
            department='CSE',
            semester=1
        )
        self.student2 = CustomUser.objects.create_user(
            username='student2',
            email='student2@test.com',
            password='student123',
            role='student'
        )
        Student.objects.create(
            user=self.student2,
            enrollment_number='CS002',
            department='CSE',
            semester=1
        )
        self.student3 = CustomUser.objects.create_user(
            username='student3',
            email='student3@test.com',
            password='student123',
            role='student'
        )
        Student.objects.create(
            user=self.student3,
            enrollment_number='IT001',
            department='IT',
            semester=1
        )
        self.student4 = CustomUser.objects.create_user(
            username='student4',
            email='student4@test.com',
            password='student123',
            role='student'
        )
        Student.objects.create(
            user=self.student4,
            enrollment_number='CS003',
            department='CSE',
            semester=2
        )
        self.student5 = CustomUser.objects.create_user(
            username='student5',
            email='student5@test.com',
            password='student123',
            role='student'
        )
        Student.objects.create(
            user=self.student5,
            enrollment_number='ECE001',
            department='ECE',
            semester=1
        )
    def tearDown(self):
        CustomUser.objects.all().delete()
        Student.objects.all().delete()
        Message.objects.all().delete()
        ActivityLog.objects.all().delete()
        UserRestriction.objects.all().delete()
        BroadcastRecipient.objects.all().delete()
        MessageRecipientGroup.objects.all().delete()
class PrivateMessagingTestCase(MessagingSystemTestSetup):
    def test_send_private_message(self):
        message = Message.objects.create(
            sender=self.student1,
            receiver=self.student2,
            content="Hello Student 2!",
            message_type="private",
            receiver_type="individual"
        )
        self.assertEqual(message.sender, self.student1)
        self.assertEqual(message.receiver, self.student2)
        self.assertEqual(message.content, "Hello Student 2!")
        self.assertFalse(message.is_read)
        self.assertFalse(message.is_deleted)
    def test_message_appears_in_inbox(self):
        message = Message.objects.create(
            sender=self.student1,
            receiver=self.student2,
            content="Test message",
            message_type="private",
            receiver_type="individual"
        )
        inbox_messages = Message.objects.filter(
            receiver=self.student2,
            message_type="private",
            is_deleted=False
        )
        self.assertIn(message, inbox_messages)
    def test_restriction_prevents_sending(self):
        restriction = UserRestriction.objects.create(
            user=self.student1,
            restriction_type="banned",
            reason="Test ban",
            restricted_by=self.admin_user,
            can_send_messages=False,
            is_active=True
        )
        active_restriction = UserRestriction.objects.filter(
            user=self.student1,
            restriction_type="banned",
            is_active=True
        ).first()
        self.assertIsNotNone(active_restriction)
        self.assertFalse(active_restriction.can_send_messages)
        restriction.is_active = False
        restriction.save()
        active_restriction = UserRestriction.objects.filter(
            user=self.student1,
            is_active=True
        ).first()
        self.assertIsNone(active_restriction)
class DepartmentBroadcastTestCase(MessagingSystemTestSetup):
    def test_department_broadcast_creation(self):
        message = Message.objects.create(
            sender=self.teacher1,
            content="Attention CSE students!",
            message_type="broadcast",
            receiver_type="department",
            department="CSE"
        )
        self.assertEqual(message.message_type, "broadcast")
        self.assertEqual(message.receiver_type, "department")
        self.assertEqual(message.department, "CSE")
    def test_department_broadcast_recipients(self):
        message = Message.objects.create(
            sender=self.teacher1,
            content="CSE Department Announcement",
            message_type="broadcast",
            receiver_type="department",
            department="CSE"
        )
        cse_students = [self.student1, self.student2, self.student4]
        for student in cse_students:
            BroadcastRecipient.objects.create(
                message=message,
                recipient=student,
                receiver_type="department_broadcast",
                is_delivered=True
            )
        recipients = BroadcastRecipient.objects.filter(
            message=message,
            receiver_type="department_broadcast"
        )
        self.assertEqual(recipients.count(), 3)
        recipient_users = [r.recipient for r in recipients]
        self.assertIn(self.student1, recipient_users)
        self.assertIn(self.student2, recipient_users)
        self.assertIn(self.student4, recipient_users)
    def test_other_departments_dont_receive(self):
        message = Message.objects.create(
            sender=self.teacher1,
            content="CSE Department Announcement",
            message_type="broadcast",
            receiver_type="department",
            department="CSE"
        )
        BroadcastRecipient.objects.create(
            message=message,
            recipient=self.student1,
            receiver_type="department_broadcast"
        )
        BroadcastRecipient.objects.create(
            message=message,
            recipient=self.student2,
            receiver_type="department_broadcast"
        )
        it_student_recipient = BroadcastRecipient.objects.filter(
            message=message,
            recipient=self.student3
        ).exists()
        ece_student_recipient = BroadcastRecipient.objects.filter(
            message=message,
            recipient=self.student5
        ).exists()
        self.assertFalse(it_student_recipient)
        self.assertFalse(ece_student_recipient)
class GlobalBroadcastTestCase(MessagingSystemTestSetup):
    def test_global_broadcast_creation(self):
        message = Message.objects.create(
            sender=self.admin_user,
            content="Attention all users!",
            message_type="broadcast",
            receiver_type="all_users"
        )
        self.assertEqual(message.message_type, "broadcast")
        self.assertEqual(message.receiver_type, "all_users")
    def test_global_broadcast_all_users_receive(self):
        message = Message.objects.create(
            sender=self.admin_user,
            content="Global Announcement",
            message_type="broadcast",
            receiver_type="all_users"
        )
        all_users = CustomUser.objects.filter(is_active=True)
        for user in all_users:
            if user != self.admin_user:
                BroadcastRecipient.objects.create(
                    message=message,
                    recipient=user,
                    receiver_type="global_broadcast",
                    is_delivered=True
                )
        recipients = BroadcastRecipient.objects.filter(
            message=message,
            receiver_type="global_broadcast"
        )
        expected_count = all_users.count() - 1
        self.assertEqual(recipients.count(), expected_count)
class UserRestrictionTestCase(MessagingSystemTestSetup):
    def test_ban_user(self):
        restriction = UserRestriction.objects.create(
            user=self.student1,
            restriction_type="banned",
            reason="Violating community guidelines",
            restricted_by=self.admin_user,
            can_send_messages=False,
            is_active=True
        )
        self.assertEqual(restriction.restriction_type, "banned")
        self.assertTrue(restriction.is_active)
        self.assertFalse(restriction.can_send_messages)
    def test_unban_user(self):
        restriction = UserRestriction.objects.create(
            user=self.student1,
            restriction_type="banned",
            reason="Test ban",
            restricted_by=self.admin_user,
            can_send_messages=False,
            is_active=True
        )
        restriction.is_active = False
        restriction.save()
        active_restrictions = UserRestriction.objects.filter(
            user=self.student1,
            is_active=True
        )
        self.assertEqual(active_restrictions.count(), 0)
    def test_mute_user(self):
        restriction = UserRestriction.objects.create(
            user=self.student1,
            restriction_type="muted",
            reason="Spam messages",
            restricted_by=self.teacher1,
            can_send_messages=False,
            is_active=True
        )
        self.assertEqual(restriction.restriction_type, "muted")
        self.assertFalse(restriction.can_send_messages)
    def test_restriction_expiration(self):
        future_time = timezone.now() + timezone.timedelta(days=1)
        restriction = UserRestriction.objects.create(
            user=self.student1,
            restriction_type="banned",
            reason="Temporary ban",
            restricted_by=self.admin_user,
            expires_at=future_time,
            is_active=True
        )
        self.assertFalse(restriction.is_expired())
        past_time = timezone.now() - timezone.timedelta(days=1)
        expired_restriction = UserRestriction.objects.create(
            user=self.student2,
            restriction_type="muted",
            reason="Expired mute",
            restricted_by=self.admin_user,
            expires_at=past_time,
            is_active=True
        )
        self.assertTrue(expired_restriction.is_expired())
class ActivityLoggingTestCase(MessagingSystemTestSetup):
    def test_message_sent_logging(self):
        message = Message.objects.create(
            sender=self.student1,
            receiver=self.student2,
            content="Test message",
            message_type="private",
            receiver_type="individual"
        )
        activity = ActivityLog.objects.create(
            user=self.student1,
            action_type="message_sent",
            message=message,
            ip_address="127.0.0.1",
            user_agent="TestClient"
        )
        self.assertEqual(activity.action_type, "message_sent")
        self.assertEqual(activity.user, self.student1)
        self.assertEqual(activity.message, message)
        self.assertIsNotNone(activity.created_at)
    def test_broadcast_sent_logging(self):
        message = Message.objects.create(
            sender=self.teacher1,
            content="Department announcement",
            message_type="broadcast",
            receiver_type="department",
            department="CSE"
        )
        activity = ActivityLog.objects.create(
            user=self.teacher1,
            action_type="broadcast_sent",
            message=message,
            ip_address="127.0.0.1",
            user_agent="TestClient"
        )
        self.assertEqual(activity.action_type, "broadcast_sent")
        self.assertEqual(activity.message, message)
    def test_user_ban_logging(self):
        activity = ActivityLog.objects.create(
            user=self.admin_user,
            action_type="user_banned",
            target_user=self.student1,
            old_value=str(False),
            new_value=str(True),
            ip_address="127.0.0.1"
        )
        self.assertEqual(activity.action_type, "user_banned")
        self.assertEqual(activity.target_user, self.student1)
        self.assertEqual(activity.old_value, "False")
        self.assertEqual(activity.new_value, "True")
    def test_activity_log_ordering(self):
        activity1 = ActivityLog.objects.create(
            user=self.student1,
            action_type="message_sent"
        )
        activity2 = ActivityLog.objects.create(
            user=self.student2,
            action_type="message_sent"
        )
        activity3 = ActivityLog.objects.create(
            user=self.student3,
            action_type="message_sent"
        )
        ordered = ActivityLog.objects.all()
        self.assertEqual(ordered[0].id, activity3.id)
        self.assertEqual(ordered[1].id, activity2.id)
        self.assertEqual(ordered[2].id, activity1.id)
class SoftDeleteTestCase(MessagingSystemTestSetup):
    def test_soft_delete_message(self):
        message = Message.objects.create(
            sender=self.student1,
            receiver=self.student2,
            content="Message to delete",
            message_type="private",
            receiver_type="individual"
        )
        message.soft_delete(self.admin_user)
        self.assertTrue(message.is_deleted)
        self.assertIsNotNone(message.deleted_at)
        self.assertEqual(message.deleted_by, self.admin_user)
    def test_deleted_message_not_in_normal_inbox(self):
        message = Message.objects.create(
            sender=self.student1,
            receiver=self.student2,
            content="Message to delete",
            message_type="private",
            receiver_type="individual"
        )
        message.soft_delete(self.admin_user)
        normal_inbox = Message.objects.filter(
            receiver=self.student2,
            is_deleted=False
        )
        self.assertNotIn(message, normal_inbox)
    def test_deleted_message_in_trash(self):
        message = Message.objects.create(
            sender=self.student1,
            receiver=self.student2,
            content="Message to delete",
            message_type="private",
            receiver_type="individual"
        )
        message.soft_delete(self.admin_user)
        trash = Message.objects.filter(
            receiver=self.student2,
            is_deleted=True
        )
        self.assertIn(message, trash)
    def test_recover_deleted_message(self):
        message = Message.objects.create(
            sender=self.student1,
            receiver=self.student2,
            content="Message to recover",
            message_type="private",
            receiver_type="individual"
        )
        message.soft_delete(self.admin_user)
        self.assertTrue(message.is_deleted)
        message.recover()
        self.assertFalse(message.is_deleted)
        self.assertIsNone(message.deleted_at)
        self.assertIsNone(message.deleted_by)
        normal_inbox = Message.objects.filter(
            receiver=self.student2,
            is_deleted=False
        )
        self.assertIn(message, normal_inbox)
class MessageMarkingTestCase(MessagingSystemTestSetup):
    def test_mark_as_read(self):
        message = Message.objects.create(
            sender=self.student1,
            receiver=self.student2,
            content="Test message",
            message_type="private",
            receiver_type="individual",
            is_read=False
        )
        self.assertFalse(message.is_read)
        message.mark_as_read()
        message.refresh_from_db()
        self.assertTrue(message.is_read)
    def test_broadcast_read_status(self):
        message = Message.objects.create(
            sender=self.admin_user,
            content="Global announcement",
            message_type="broadcast",
            receiver_type="all_users"
        )
        recipient = BroadcastRecipient.objects.create(
            message=message,
            recipient=self.student1,
            receiver_type="global_broadcast",
            is_read=False
        )
        self.assertFalse(recipient.is_read)
        recipient.is_read = True
        recipient.read_at = timezone.now()
        recipient.save()
        recipient.refresh_from_db()
        self.assertTrue(recipient.is_read)
        self.assertIsNotNone(recipient.read_at)
