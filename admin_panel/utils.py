import firebase_admin
from firebase_admin import messaging
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

# Initialize Firebase app (call once)
if not firebase_admin._apps:
    firebase_admin.initialize_app(credential=firebase_admin.credentials.Certificate(settings.GOOGLE_APPLICATION_CREDENTIALS))

def send_notification_to_topic(title, message):
    try:
        message = messaging.Message(
            notification=messaging.Notification(
                title=title,
                body=message
            ),
            topic='all_users'
        )
        response = messaging.send(message)
        logger.info(f"FCM push notification sent: {title} - Message ID: {response}")
        return {'message_id': response}
    except Exception as e:
        logger.error(f"FCM push notification failed: {title} - Error: {str(e)}")
        return {'error': str(e)}