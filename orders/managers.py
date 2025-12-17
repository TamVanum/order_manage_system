from django.db import models
from .querysets import OrderQuerySet

class OrderManager(models.Manager):
    def get_queryset(self):
        return OrderQuerySet(self.model, using=self._db)

    def get_by_user_id(self, user_id):
        return self.get_queryset().get_by_user_id(user_id)

    def get_by_payment_id(self, payment_id):
        return self.get_queryset().get_by_payment_id(payment_id)

    def get_by_status(self, status):
        return self.get_queryset().get_by_status(status)

    def get_by_created_at(self, created_at):
        return self.get_queryset().get_by_created_at(created_at)