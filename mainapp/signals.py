from django.contrib.auth.models import User
from mainapp.models import Course
from django.db.models.signals import post_save
from django.dispatch import receiver
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync


@receiver(post_save, sender=Course)
def announce_new_course(sender, instance, created, **kwargs):
    if created:
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            "gossip", {
                "type": "course.gossip",
                "event": "New Course",
                'course_title': instance.russian_title,
                "course_id": instance.id
            }
        )
