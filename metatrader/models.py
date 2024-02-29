from django.db import models
from django.contrib.auth.models import User  

# Create your models here.
class Pares(models.Model):
    id = models.BigIntegerField(primary_key=True)
    pares = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'pares'

class Datatrader1Mtemp(models.Model):
    date = models.DateField(db_column='Date', blank=True, null=True)  
    time = models.TimeField(db_column='Time', blank=True, null=True)  
    open = models.FloatField(db_column='Open', blank=True, null=True)  
    high = models.FloatField(db_column='High', blank=True, null=True)  
    low = models.FloatField(db_column='Low', blank=True, null=True)  
    close = models.FloatField(db_column='Close', blank=True, null=True)  
    volume = models.BigIntegerField(db_column='Volume', blank=True, null=True)  
    par = models.ForeignKey(Pares, blank=True, null=True, on_delete=models.CASCADE)

    class Meta:
        db_table = 'DataTrader1mTemp'

class Datatrader1M(models.Model):
    date = models.DateField(db_column='Date', blank=True, null=True)  
    time = models.TimeField(db_column='Time', blank=True, null=True)  
    open = models.FloatField(db_column='Open', blank=True, null=True)  
    high = models.FloatField(db_column='High', blank=True, null=True)  
    low = models.FloatField(db_column='Low', blank=True, null=True)  
    close = models.FloatField(db_column='Close', blank=True, null=True)  
    volume = models.BigIntegerField(db_column='Volume', blank=True, null=True)  
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
    group = models.IntegerField(db_column='group', blank=True, null=True)
    
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
        
class ResumeIndicador(models.Model):
    par = models.ForeignKey(Pares, blank=True, null=True, on_delete=models.CASCADE)
    date = models.DateTimeField(db_column='Date', blank=True, null=True)
    pc1 = models.FloatField(db_column='PC1',blank=True, null=True)
    time_frame = models.IntegerField(db_column='time_frame', blank=True, null=True)

    class Meta:
        db_table = 'IndicadorResumen'
        
class UserFavAccounts(models.Model):
    id = models.BigIntegerField(primary_key=True)
    user = models.CharField(max_length=255)
    accounts = models.CharField(max_length=255)

    class Meta:
        db_table = 'UserFavAccounts'

class Events(models.Model): 
    orden = models.BigIntegerField(primary_key=True)
    hora = models.TimeField(db_column='hora', blank=True, null=True)
    fecha = models.DateField(db_column='fecha', blank=True, null=True)
    fecha_num = models.BigIntegerField(db_column='fecha_num', blank=True, null=True)
    tiempo_falta = models.CharField(db_column='tiempo_falta', max_length=40)
    moneda = models.CharField(db_column='moneda', max_length=40)
    evento = models.CharField(db_column='evento', max_length=40)
    periodo = models.CharField(db_column='periodo', max_length=40)
    periodo2 = models.CharField(db_column='periodo2', max_length=40)
    impacto = models.CharField(db_column='impacto', max_length=40)
    precedente = models.CharField(db_column='precedente', max_length=40)
    consenso = models.CharField(db_column='consenso', max_length=40)
    actual = models.CharField(db_column='actual', max_length=40)
    
    class Meta: 
        db_table = 'events'

class ParMoneda(models.Model):
    id = models.BigIntegerField(primary_key=True)
    par = models.CharField(db_column='par', max_length=40)
    moneda = models.CharField(db_column='moneda', max_length=40)
    
    class Meta: 
        db_table = 'par_moneda'

class Pips(models.Model): 
    orden = models.BigIntegerField(primary_key=True)
    fecha = models.DateField(db_column='fecha', blank=True, null=True)
    fecha_numero = models.BigIntegerField(db_column='fecha_numero', blank=True, null=True)
    simbolo = models.CharField(db_column='simbolo', max_length=40)
    price_open = models.FloatField(db_column='price_open', blank=True, null=True)
    price_close = models.FloatField(db_column='price_close', blank=True, null=True)
    diferencia = models.FloatField(db_column='diferencia', blank=True, null=True)
    pips = models.FloatField(db_column='pips', blank=True, null=True)
    
    class Meta: 
        db_table = 'pips'

class CortesIndicador(models.Model):
    par = models.ForeignKey(Pares, blank=True, null=True, on_delete=models.CASCADE)
    date = models.DateTimeField(db_column='Date',blank=True, null=True)
    corte_buy = models.FloatField(db_column='corte_buy',blank=True, null=True)
    corte_sell = models.FloatField(db_column='corte_sell', blank=True, null=True)
    time_frame = models.IntegerField(db_column='time_frame', blank=True, null=True)

    class Meta:
        db_table = 'CortesIndicador'
        
class AlertEvents(models.Model): 
    par = models.ForeignKey(Pares, blank=True, null=True, on_delete=models.CASCADE)
    par_name = models.CharField(db_column='par', max_length=25, blank=True, null=True)
    currency = models.CharField(db_column='currency', max_length=40)
    name = models.CharField(db_column='name', max_length=40)
    fecha = models.DateField(db_column='fecha', blank=True, null=True)
    pips_ant = models.FloatField(db_column='pips_ant', blank=True, null=True)
    count_events = models.BigIntegerField(db_column='count_events', blank=True, null=True)
    max_pips = models.FloatField(db_column='max_pips', blank=True, null=True)
    prom_pips = models.FloatField(db_column='prom_pips', blank=True, null=True)
    ult_event = models.DateField(db_column='ult_event', blank=True, null=True)
    
    class Meta:
        db_table = 'alert_events'

class DeviceToken(models.Model):
    user = models.CharField(max_length=255)
    token = models.CharField(max_length=255)

    class Meta:
        db_table = 'DeviceToken'