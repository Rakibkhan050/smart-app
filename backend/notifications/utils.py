from pywebpush import webpush, WebPushException
from django.conf import settings

VAPID_CLAIMS = {
    'sub': 'mailto:admin@example.com'
}


def send_web_push(subscription_info, payload):
    try:
        webpush(
            subscription_info=subscription_info,
            data=payload,
            vapid_private_key=settings.VAPID_PRIVATE_KEY,
            vapid_public_key=settings.VAPID_PUBLIC_KEY,
            vapid_claims=VAPID_CLAIMS
        )
    except WebPushException as ex:
        # handle errors/log
        print('WebPush failed', ex)
