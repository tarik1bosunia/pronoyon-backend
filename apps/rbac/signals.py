"""
Signals for RBAC
"""
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import UserRole, RoleHistory


@receiver(post_save, sender=UserRole)
def log_role_assignment(sender, instance, created, **kwargs):
    """Log role assignment in history"""
    if created:
        RoleHistory.objects.create(
            user=instance.user,
            role=instance.role,
            action='assigned',
            performed_by=instance.assigned_by,
            reason=f"Role assigned{'with expiration' if instance.expires_at else ''}",
            metadata={
                'expires_at': instance.expires_at.isoformat() if instance.expires_at else None,
                'context': instance.context,
                'is_primary': instance.is_primary,
            }
        )
    else:
        # Check if role was deactivated
        if not instance.is_active:
            RoleHistory.objects.create(
                user=instance.user,
                role=instance.role,
                action='revoked',
                reason="Role deactivated",
                metadata={
                    'context': instance.context,
                }
            )


@receiver(post_delete, sender=UserRole)
def log_role_removal(sender, instance, **kwargs):
    """Log role removal in history"""
    RoleHistory.objects.create(
        user=instance.user,
        role=instance.role,
        action='revoked',
        reason="Role assignment deleted",
        metadata={
            'context': instance.context,
        }
    )
