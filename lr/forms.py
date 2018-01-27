from django import forms
from .models import Money

class MoneyForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(MoneyForm, self).__init__(*args, **kwargs)
#        self.initial['amount']=888
#        self.initial['moneyinout']=""
#        self.initial['user']=""
#        self.initial['cashtype']=""
#        self.initial['parentmoney']=""
        try:
#            if self.initial['moneyinout']==1:
#                self.initial['parentmoney']=""
            if self.initial['amount'] != None:
                self.fields['parentmoney'].queryset = Money.objects.filter(amount__gt=self.initial['amount']).order_by('-amount')
        except:
            pass
            
    class Meta:
        model = Money
        fields = ['amount', 'moneyinout', 'user', 'cashtype', 'parentmoney']
        labels = {'amount' : 'Amount', 'moneyinout': 'Money In/Out', 'user': 'User', 'cashtype': 'cashtype', 'parentmoney': 'parentmoney'}
