from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import CustomUser
from django.contrib.auth.models import Group


@receiver(post_save, sender=CustomUser)
def assign_user_to_group(sender, instance, created, **kwargs):

    if created and instance.role:
        # Convert role to group name format
        group_name = instance.role.capitalize()

        # Get or create the group
        group, _ = Group.objects.get_or_create(name=group_name)

        # Add the user to the group
        instance.groups.add(group)
