from django.core.cache import cache
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from api.utils.cache_keys import user_cache_key
from users.models import User


def register_signals():
    @receiver(post_save, sender=User)
    def update_user_cache(sender, instance, **kwargs):
        cache.set(user_cache_key(instance.id), instance, timeout=300)

    @receiver(post_delete, sender=User)
    def delete_user_cache(sender, instance, **kwargs):
        cache.delete(user_cache_key(instance.id))
