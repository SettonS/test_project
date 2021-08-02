import io
import threading

from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator
from django.core.cache import cache
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.core.exceptions import ValidationError

from rest_framework.views import APIView, Response
from rest_framework.status import HTTP_200_OK

from .models import Customer
from .serializers import ViewCustomerSerializer
from .services import process_and_save_deals_from_csv, add_gems_to_customers


class Deals(APIView):

    @method_decorator(cache_page(3))
    def get(self, request):
        customers = Customer.objects.all().order_by('-spent_money')[:5]
        serializer = ViewCustomerSerializer(data=add_gems_to_customers(customers), many=True)
        serializer.is_valid()
        data = {'response': serializer.data}
        return Response(status=HTTP_200_OK, data=data)

    def post(self, request):
        try:
            request.data['deals']
        except KeyError:
            return Response(status=400, data='Запрос должен иметь аргумент "deals"')

        if type(request.data['deals']) != InMemoryUploadedFile:
            return Response(status=400, data='Аргумент deals должен содержать файл')

        if request.data['deals'].name != 'deals.csv':
            return Response(status=400, data='Неправильное имя файла')

        csv_strings = io.StringIO(request.data['deals'].read().decode(), newline='')
        threading.Lock()
        try:
            errors = process_and_save_deals_from_csv(csv_strings)
        except ValidationError as exc:
            return Response(status=400, data=exc)
        cache.clear()

        return Response(status=HTTP_200_OK, data='Файл был обработан без критических ошибок')
