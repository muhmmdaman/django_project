from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Marks
@receiver(post_save, sender=Marks)
def update_prediction_on_marks_save(sender, instance, **kwargs):
    """Signal to update prediction when marks are saved.
    Automatically calculates average marks and generates/updates
    the prediction for the student.
    """
    from analytics.models import Prediction
    student = instance.student
    Prediction.generate_prediction(student)
