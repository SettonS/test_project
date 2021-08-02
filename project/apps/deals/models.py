from django.db import models


class Customer(models.Model):
    username = models.CharField(max_length=100, unique=True)
    spent_money = models.IntegerField(default=0)
    objects = models.Model


class Item(models.Model):
    name = models.CharField(max_length=100, unique=True)
    customers = models.ManyToManyField(
        'Customer', related_name='items', db_table='Customers_Items'
    )


class Deal(models.Model):
    customer = models.ForeignKey('Customer', related_name='deals', on_delete=models.CASCADE)
    item = models.ForeignKey('Item', related_name='deals', on_delete=models.CASCADE)
    quantity = models.IntegerField(blank=False)
    total = models.IntegerField(blank=False)
    date = models.DateTimeField(blank=False)
