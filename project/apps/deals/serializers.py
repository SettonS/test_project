from rest_framework import serializers


class ViewCustomerSerializer(serializers.Serializer):
    username = serializers.CharField()
    spent_money = serializers.IntegerField()
    gems = serializers.ListField()
