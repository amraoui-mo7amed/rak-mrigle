from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import UserProfile

@receiver(post_save, sender=User)
def create_admin_profile(sender, instance, created, **kwargs):
    if created and instance.is_superuser:
        UserProfile.objects.get_or_create(
            user=instance,
            defaults={
                'role': UserProfile.roleChoices.ADMIN,
                'is_approved': True
            }
        )
