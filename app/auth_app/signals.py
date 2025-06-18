from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver
import logging
from django.db.models.signals import Signal

logger = logging.getLogger('auth_app')

# user_logged_in = Signal()

@receiver(user_logged_in)
def log_login(sender, request, user, **kwargs):
    logger.info(f"{user.username} logged in from {request.META.get('REMOTE_ADDR')}")



refresh_token_used = Signal()

@receiver(refresh_token_used)
def log_refresh(sender, user, request, **kwargs):
    logger.info(f"{user.username} used refresh token from {request.META.get('REMOTE_ADDR')}")

secure_data_token_used = Signal()

@receiver(secure_data_token_used)
def secure_data_view(sender, request, **kwargs):
    logger.info(f"Secure data view accessed by {request.user.username} from {request.META.get('REMOTE_ADDR')}")