from django.db import models
from django.utils import timezone

from engine.choices import OrderChoices
from engine import constants


class Products(models.Model):
    production_date = models.DateTimeField()
    name = models.CharField(max_length=64)
    price = models.FloatField()


class Order(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)
    status = models.CharField(max_length=32, choices=OrderChoices.choices(), default=OrderChoices.ACTIVE)
    product = models.ForeignKey(Products, on_delete=models.CASCADE, related_name='orders')

    def complete(self):
        self.status = OrderChoices.COMPLETED
        self.save()

    def pay(self):
        self.status = OrderChoices.PAID
        self.save()

    @property
    def is_discounted(self):
        """
            Method returns True if more than a month has passed from the date of production of the product
            in the order to the date of placing the order else False
            return: boolean
        """
        return (self.created_at - self.product.production_date).days > 30

    @property
    def total_price(self):
        """
            Method returns price of an product with or without a discount(depends by product production date)
            return: float
        """
        if self.is_discounted:
            return round(self.product.price / 100 * constants.DISCOUNT_AMOUNT, 2)
        return round(self.product.price, 2)
