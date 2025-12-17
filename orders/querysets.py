from django.db import models

class OrderQuerySet(models.QuerySet):
    def get_by_user_id(self, user_id):
        return self.filter(user_id=user_id)

    def get_by_payment_id(self, payment_id):
        return self.filter(payment_id=payment_id)

    def get_by_status(self, status):
        return self.filter(status=status)

    def get_by_created_at(self, created_at):
        return self.filter(created_at=created_at)