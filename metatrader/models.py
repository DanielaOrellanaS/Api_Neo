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

class Operation(models.Model): 
    date = models.DateTimeField(db_column='Date', blank=True, null=True) 
    ticket = models.BigIntegerField(db_column='Ticket', blank=True, null=True)
    symbol = models.CharField(db_column='Symbol', max_length=40) 
    lotes = models.FloatField(db_column='Lotes', blank=True, null=True)
    type = models.CharField(db_column='Type', max_length=40)
    dateOpen = models.DateTimeField(db_column='DateOpen', blank=True, null=True)
    dateClose = models.DateTimeField(db_column='DateClose', blank=True, null=True)
    openPrice = models.FloatField(db_column='Price', blank=True, null=True)
    closePrice = models.FloatField(db_column='ClosePrice', blank=True, null=True)
    magic = models.BigIntegerField(db_column='Magic', blank=True, null=True)
    sl = models.FloatField(db_column='SL', blank=True, null=True)
    tp = models.FloatField(db_column='TP', blank=True, null=True)
    profit = models.FloatField(db_column='Profit', blank=True, null=True)
    account = models.ForeignKey(Account, blank=True, null=True, on_delete=models.CASCADE)
    
    class Meta:
        db_table = 'Operation'