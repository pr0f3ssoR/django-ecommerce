from django.dispatch import receiver
from django.db.models.signals import post_delete
from .models import VariantImage




@receiver(post_delete,sender=VariantImage)
def delete_image_file(sender,instance,**kwagrs):
    if instance.image_url:
        instance.image_url.delete(save=False)


