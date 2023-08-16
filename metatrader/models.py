from django.db import models

# Create your models here.
class Pares(models.Model):
    id = models.BigIntegerField(primary_key=True)
    pares = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'pares'

class Datatrader1Mtemp(models.Model):
    date = models.TextField(db_column='Date', blank=True, null=True)  # Field name made lowercase.
    time = models.TextField(db_column='Time', blank=True, null=True)  # Field name made lowercase.
    open = models.FloatField(db_column='Open', blank=True, null=True)  # Field name made lowercase.
    high = models.FloatField(db_column='High', blank=True, null=True)  # Field name made lowercase.
    low = models.FloatField(db_column='Low', blank=True, null=True)  # Field name made lowercase.
    close = models.FloatField(db_column='Close', blank=True, null=True)  # Field name made lowercase.
    volume = models.BigIntegerField(db_column='Volume', blank=True, null=True)  # Field name made lowercase.
    par = models.ForeignKey(Pares, blank=True, null=True, on_delete=models.CASCADE)

    class Meta:
        db_table = 'DataTrader1mTemp'