import csv
from io import StringIO

from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.db import IntegrityError
from django.db.models import QuerySet

from .models import Customer, Item, Deal


def process_and_save_deals_from_csv(csv_strings: StringIO) -> dict:
    """
        Обрабатывает сделки и сохраняеи их в бд,
        так же создает покупателей и предметы
        если они не встречались ранее,
        возвращает dict с найденными ошибками
    """

    reader = csv.DictReader(csv_strings)
    errors = {}

    if reader.fieldnames != ['customer', 'item', 'total', 'quantity', 'date']:
        raise ValidationError('Файл должен содержать поля customer, item, total, quantity, date')

    for row, deal in enumerate(reader):
        customer = get_or_create_customer(deal['customer'])
        item = get_or_create_item(deal['item'])
        try:
            process_and_save_deal(customer, item, deal['quantity'],
                                  deal['total'], deal['date'])
        except ValueError as exc:
            errors['row ' + str(row)] = exc.__str__()
        except ValidationError as exc:
            errors['row ' + str(row)] = exc.__str__()
        except IntegrityError as exc:
            errors['row ' + str(row)] = exc.__str__()

    return errors


def get_or_create_customer(username: str) -> Customer:
    try:
        return Customer.objects.get(username=username)
    except ObjectDoesNotExist:
        return Customer.objects.create(username=username)


def get_or_create_item(item_name: str) -> Item:
    try:
        return Item.objects.get(name=item_name)
    except ObjectDoesNotExist:
        return Item.objects.create(name=item_name)


def process_and_save_deal(customer: Customer, item: Item, quantity: str,
                          total: str, date: str) -> (Deal, Customer):
    """
        Сохраняет сделку, а так же обновляет объект Customer
    """
    try:
        deal = Deal.objects.create(
            customer=customer,
            item=item,
            quantity=quantity,
            total=total,
            date=date
        )

        customer.spent_money += int(total)
        customer.save()
        customer.items.add(item)

        return deal

    except ValueError as exc:
        raise exc


def find_duplicate_items_from_customers(customers: QuerySet):
    """ Находит предметы которые есть у двух и более покупателей"""
    duplicate_items = {}

    for customer in customers:
        for item in customer.items.all():
            try:
                duplicate_items[item.name] += 1
            except KeyError:
                duplicate_items[item.name] = 1

    for key, value in list(duplicate_items.items()):
        if value < 2:
            del duplicate_items[key]

    return duplicate_items


def add_gems_to_customers(customers):
    """Добавляет атрибут gems к покупателям не сохраняя изменения в бд"""

    duplicate_items = find_duplicate_items_from_customers(customers)
    for customer in customers:
        customer.gems = []
        for item in customer.items.all():
            if item.name in duplicate_items.keys():
                     customer.gems.append(item.name)
    return customers
