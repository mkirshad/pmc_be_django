# signals.py
from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.dispatch import receiver
from django.utils.timezone import now
from .models import AuditLog
from django.db.models.signals import post_save, post_delete
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User
from pmc_api.threadlocals import get_current_user

@receiver(post_save, sender=User)
def debug_user_signal(sender, instance, created, **kwargs):
    print(f"🔔 Signal triggered for user: {instance.username}, created: {created}")

@receiver(user_logged_in)
def log_user_login(sender, request, user, **kwargs):
    AuditLog.objects.create(
        user=user,
        action='login',
        ip_address=get_client_ip(request),
        description=f"{user.username} logged in."
    )

@receiver(user_logged_out)
def log_user_logout(sender, request, user, **kwargs):
    AuditLog.objects.create(
        user=user,
        action='logout',
        ip_address=get_client_ip(request),
        description=f"{user.username} logged out."
    )

def get_client_ip(request):
    return request.META.get('REMOTE_ADDR')

@receiver(post_save)
def log_save(sender, instance, created, **kwargs):
    if sender.__name__ == 'AuditLog':  # Avoid recursive logs
        return

    action = "create" if created else "update"
    AuditLog.objects.create(
        user=get_current_user(),  # You’ll set this with middleware (see next section)
        action=action,
        model_name=sender.__name__,
        object_id=str(instance.pk),
        description=f"{sender.__name__} {'created' if created else 'updated'} with ID {instance.pk}"
    )

@receiver(post_delete)
def log_delete(sender, instance, **kwargs):
    if sender.__name__ == 'AuditLog':
        return

    AuditLog.objects.create(
        user=get_current_user(),
        action="delete",
        model_name=sender.__name__,
        object_id=str(instance.pk),
        description=f"{sender.__name__} deleted with ID {instance.pk}"
    )