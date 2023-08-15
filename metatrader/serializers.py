from rest_framework import serializers
from rest_framework.fields import empty
from metatrader.models import *

class ParesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pares
        fields = '__all__'

class MonedaSerializer(serializers.ModelSerializer):
    par = serializers.PrimaryKeyRelatedField(queryset=Pares.objects.using('postgres').all())
    class Meta:
        model = Datatrader1Mtemp
        fields = '__all__'
