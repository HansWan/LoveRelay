from django.contrib import admin
from django.contrib.auth.models import User

# Register your models here.
from lr.models import Cashtype, Moneyinout, Purpose, Money, Inheritor, School, Userinfo, Userschoolinfo, Bank, Userbankinfo

#admin.site.register(User)
admin.site.register(Cashtype)
admin.site.register(Moneyinout)
admin.site.register(Purpose)
admin.site.register(Money)
admin.site.register(Inheritor)
admin.site.register(School)
admin.site.register(Userinfo)
admin.site.register(Userschoolinfo)
admin.site.register(Bank)
admin.site.register(Userbankinfo)


