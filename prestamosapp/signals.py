from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Cliente

@receiver(post_save, sender=Cliente)
def update_cliente_saldo(sender, instance, **kwargs):
    if kwargs.get('created', False):  # Only for newly created instances
        instance.update_saldo()