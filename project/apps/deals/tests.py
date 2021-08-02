from io import StringIO

from django.test import TestCase, TransactionTestCase
from django.db import transaction
from django.db.models import QuerySet

from .services import *
from .models import *


class TestDealsServices(TestCase):

    def setUp(self):
        self.deal_data = {
            'customer': 'Fred',
            'item': 'Сапфир',
            'quantity': '3',
            'total': '759',
            'date': '2018-12-14 08:29:52.506166'
        }

    def test_get_or_create_customer(self):
        customer_username = 'Fred'
        created_customer = get_or_create_customer(customer_username)

        self.assertEqual(created_customer.username, customer_username)
        self.assertEqual(created_customer.spent_money, 0)
        self.assertEqual(len(created_customer.items.all()), 0)

        customer = get_or_create_customer(customer_username)

        self.assertEqual(customer.id, created_customer.id)

    def test_get_or_create_item(self):
        item_name = 'Сапфир'
        created_item = get_or_create_item(item_name)

        self.assertEqual(created_item.name, item_name)
        self.assertEqual(len(created_item.customers.all()), 0)

        getting_item = get_or_create_item(item_name)

        self.assertEqual(getting_item.id, created_item.id)

    def test_process_and_save_deal(self):
        customer = Customer.objects.create(username='Tom')
        item = Item.objects.create(name='Рубин')
        deal = process_and_save_deal(
            customer=customer,
            item=item,
            quantity=self.deal_data['quantity'],
            total=self.deal_data['total'],
            date=self.deal_data['date']
        )
        self.assertEqual(deal.customer, customer)
        self.assertEqual(deal.item.name, item.name)
        self.assertEqual(deal.quantity, self.deal_data['quantity'])
        self.assertEqual(deal.total, self.deal_data['total'])
        self.assertEqual(deal.date, self.deal_data['date'])

        try:
            customer.items.get(name='Рубин')
        except ObjectDoesNotExist:
            assert 'Имя предмета отличается от исходного'

        if not len(customer.items.all()) != 1:
            assert 'После сделки покупатель получил более одного предмета'


class TestServices2(TransactionTestCase):
    def setUp(self):
        self.csv_strings = """customer,item,total,quantity,date
        resplendent,Сапфир,8502,6,2018-12-14 14:43:45.883282
        buckaroo,Рубин,342,2,2018-12-15 15:00:59.858739
        zygote4id3n,Яшма,264,3,2018-12-16 00:01:13.013713
        turophile,Рубин,628,4,2018-12-21 10:58:04.572541
        bellwether,Цаворит,972,9,2018-12-22 11:30:12.946770
        uvulaperfly117,Аметрин,2376,9,2018-12-22 20:13:11.289213
        snookered,Аметрин,1360,5,2018-12-23 18:45:37.696171
        viperliamk0125,Аметрин, 587,3,2018-12-24 03:09:09.722070"""
        self.errors = process_and_save_deals_from_csv(StringIO(self.csv_strings))

    def test_process_and_save_deals_from_csv(self):
        reader = csv.DictReader(StringIO(self.csv_strings))
        for raw_deal in reader:
            deal = Deal.objects.get(
                date=raw_deal['date']
            )
            self.assertEqual(deal.customer.spent_money, deal.total)
            self.assertEqual(len(deal.customer.items.all()), 1)

    def test_find_duplicate_item_from_customers(self):
        duplicate_items = find_duplicate_items_from_customers(
            Customer.objects.all()
        )
        self.assertEqual(
            duplicate_items,
            {'Рубин': 2, 'Аметрин': 3}
        )
