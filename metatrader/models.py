from django.db import models

# Create your models here.
class Pares(models.Model):
    id = models.BigIntegerField(primary_key=True)
    pares = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'pares'

class Datatrader1Mtemp(models.Model):
    date = models.DateField(db_column='Date', blank=True, null=True)  # Field name made lowercase.
    time = models.TimeField(db_column='Time', blank=True, null=True)  # Field name made lowercase.
    open = models.FloatField(db_column='Open', blank=True, null=True)  # Field name made lowercase.
    high = models.FloatField(db_column='High', blank=True, null=True)  # Field name made lowercase.
    low = models.FloatField(db_column='Low', blank=True, null=True)  # Field name made lowercase.
    close = models.FloatField(db_column='Close', blank=True, null=True)  # Field name made lowercase.
    volume = models.BigIntegerField(db_column='Volume', blank=True, null=True)  # Field name made lowercase.
    par = models.ForeignKey(Pares, blank=True, null=True, on_delete=models.CASCADE)

    class Meta:
        db_table = 'DataTrader1mTemp'

class Datatrader1M(models.Model):
    date = models.DateField(db_column='Date', blank=True, null=True)  # Field name made lowercase.
    time = models.TimeField(db_column='Time', blank=True, null=True)  # Field name made lowercase.
    open = models.FloatField(db_column='Open', blank=True, null=True)  # Field name made lowercase.
    high = models.FloatField(db_column='High', blank=True, null=True)  # Field name made lowercase.
    low = models.FloatField(db_column='Low', blank=True, null=True)  # Field name made lowercase.
    close = models.FloatField(db_column='Close', blank=True, null=True)  # Field name made lowercase.
    volume = models.BigIntegerField(db_column='Volume', blank=True, null=True)  # Field name made lowercase.
    par = models.ForeignKey(Pares, blank=True, null=True, on_delete=models.CASCADE)

    class Meta:
        db_table = 'DataTrader1m'

class AccountType(models.Model): 
    description = models.CharField(max_length=40) 
    
    class Meta:
        db_table = 'AccountType'
        
class Account(models.Model): 
    id = models.BigIntegerField(primary_key=True)
    accountType = models.ForeignKey(AccountType, on_delete=models.CASCADE, blank=True, null=True)
    alias = models.CharField(max_length=40) 
    
    class Meta:
        db_table = 'Account'

class DetailBalance(models.Model): 
    date = models.DateField(db_column='Date', blank=True, null=True) 
    time = models.TimeField(db_column='Time', blank=True, null=True)
    balance = models.FloatField(db_column='Balance', blank=True, null=True)
    equity = models.FloatField(db_column='Equity', blank=True, null=True)
    freemargin = models.FloatField(db_column='FreeMargin', blank=True, null=True)
    freemarginmode = models.FloatField(db_column='FreeMarginMode', blank=True, null=True)
    fracemareq = models.FloatField(db_column='Fracemareq', blank=True, null=True)
    flotante = models.FloatField(db_column='Flotante', blank=True, null=True)
    operations = models.IntegerField(db_column='Operations', blank=True, null=True)
    fracflotante = models.FloatField(db_column='FracFlotante', blank=True, null=True)
    account = models.ForeignKey(Account, blank=True, null=True, on_delete=models.CASCADE)
    
    class Meta:
        db_table = 'DetailBalance'