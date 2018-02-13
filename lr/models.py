from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Cashtype(models.Model):
    cashtype = models.CharField(max_length=10, blank=True)
    country = models.CharField(max_length=50, blank=True)
        
    def __str__(self):
        return self.cashtype

class Moneyinout(models.Model):               #income/outcome
    moneyinout = models.CharField(max_length=10, blank=True)
    
    def __str__(self):
        return self.moneyinout

class Purpose(models.Model):
    purpose = models.CharField(max_length=20, blank=True)
    moneyinout = models.ForeignKey(Moneyinout, on_delete=models.DO_NOTHING, default=1)

    def __str__(self):
        return self.purpose
            
class Money(models.Model):
#    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    amount = models.DecimalField(max_digits=20, decimal_places=4)
    cashtype = models.ForeignKey(Cashtype, on_delete=models.DO_NOTHING, default=1)
    createddatetime = models.DateTimeField(auto_now_add=True)
    beneficiarydesignated = models.BooleanField(default=False)
    donatordesignated = models.BooleanField(default=False)
    purpose = models.ForeignKey(Purpose, on_delete=models.DO_NOTHING, blank=True, null=True, default=1)  #define the purpose of money: donation, refund, request, etc.
#    moneyinout = models.ForeignKey(Moneyinout, on_delete=models.DO_NOTHING)
#    moneyinout = models.ForeignKey(Moneyinout, on_delete=models.DO_NOTHING, default=1)
#    parentmoney = models.ForeignKey('self', limit_choices_to={'amount__gt': Money__amount}, blank=True, null=True, on_delete=models.DO_NOTHING)
    parentmoney = models.ForeignKey('self', blank=True, null=True, on_delete=models.DO_NOTHING)
    comment = models.CharField(max_length=50, blank=True)

    def __str__(self):
        return u'%+15s %+20s %+10s' % (self.amount, self.user, self.cashtype)
        
    def __setitem__(self, k, v):
        self.k = v

class Inheritor(models.Model):
    first_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=150, blank=True)
    socialid = models.CharField(max_length=18, blank=True)

    def __str__(self):
        return u'%s %s' % (self.first_name, self.last_name)

class School(models.Model):
    name = models.CharField(max_length=150, blank=True)
    address = models.CharField(max_length=150, blank=True)

    def __str__(self):
        return self.name

class Userinfo(models.Model):
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    socialid = models.CharField(max_length=18, blank=True)
    inheritor = models.ForeignKey(Inheritor, on_delete=models.DO_NOTHING, blank=True)
    age = models.IntegerField(default=0)
    qq = models.CharField(max_length=20, blank=True)
    weixin = models.CharField(max_length=50, blank=True)
    email = models.EmailField(blank=True, verbose_name='E-mail')
    mobile = models.CharField(max_length=20, blank=True)

    def __str__(self):
        return u'%s' % (self.user)
            
class Userschoolinfo(models.Model):
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    school = models.ForeignKey(School, blank=True, null=True, on_delete=models.DO_NOTHING)
    enrollmentdate = models.DateField(blank=True)
    graduatedata = models.DateField(blank=True)
    department = models.CharField(max_length=150, blank=True)
    major = models.CharField(max_length=150, blank=True)

    def __str__(self):
        return u'%s %s' % (self.user, self.school)
  
class Bank(models.Model):
    name = models.CharField(max_length=150, blank=True)
    address = models.CharField(max_length=150, blank=True)
    country = models.CharField(max_length=50, blank=True)    

    def __str__(self):
        return self.name
            
class Userbankinfo(models.Model):
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    bank = models.ForeignKey(Bank, blank=True, null=True, on_delete=models.DO_NOTHING)
    bankaccount = models.CharField(max_length=50, blank=True)
    
    def __str__(self):
        return u'%s %s' % (self.user, self.bank)


