from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.utils import timezone

class CustomUser(AbstractUser):
    groups = models.ManyToManyField(
        Group,
        related_name='customuser_groups',
        blank=True,
        help_text='The groups this user belongs to.',
        verbose_name='groups',
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name='customuser_permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions',
    )

class Transaction(models.Model):
    sender = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='transactions_sent')
    receiver = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='transactions_received')
    data = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='proof/', blank=True)
    acknowledged_at = models.DateTimeField()

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Transaction from {self.sender.username} to {self.receiver.username}"

class Notification(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='notifications')
    message = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Notification for {self.user.username}: {self.message}"

class Acknowledgement(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
    ]

    from_user = models.ForeignKey(CustomUser,on_delete=models.CASCADE,related_name='acknowledgements_sent')
    to_user = models.ForeignKey(CustomUser,on_delete=models.CASCADE,related_name='acknowledgements_received')
    data = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='ack/', blank=True, null=True)
    acknowledged_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    accepted_at = models.DateTimeField(null=True, blank=True)

    def accept(self):
        if self.status != 'pending':
            return  # prevent double-processing

        self.status = 'accepted'
        self.accepted_at = timezone.now()
        self.save()

        # Create transaction
        Transaction.objects.create(
            sender=self.from_user,
            receiver=self.to_user,
            acknowledged_at=self.acknowledged_at
        )

    def reject(self):
        if self.status != 'pending':
            return  # prevent double-processing

        self.status = 'rejected'
        self.save()

        # Create notification for the sender
        Notification.objects.create(
            user=self.from_user,
            message=f"Acknowledgement to {self.to_user.username} was rejected."
        )


    def __str__(self):
        return f"Acknowledgement from {self.from_user.username} to {self.to_user.username} [{self.status}]"
