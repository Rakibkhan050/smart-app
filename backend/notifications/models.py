from django.db import models
from django.conf import settings


class Notification(models.Model):
    CHANNEL_CHOICES = [
        ('email', 'Email'),
        ('in_app', 'In App'),
        ('web_push', 'Web Push'),
    ]

    recipient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=255)
    body = models.TextField(blank=True)
    data = models.JSONField(blank=True, null=True)
    read = models.BooleanField(default=False)
    channel = models.CharField(max_length=20, choices=CHANNEL_CHOICES, default='in_app')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Notification to {self.recipient} - {self.title}"


class Subscription(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='push_subscriptions')
    endpoint = models.URLField()
    keys = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'endpoint')

    def __str__(self):
        return f"Subscription for {self.user} - {self.endpoint[:40]}"
