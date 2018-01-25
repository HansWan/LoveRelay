from django import forms
from .models import Money

class MoneyForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(MoneyForm, self).__init__(*args, **kwargs)
        if self.initial['moneyinout']==1:
            self.initial['parentmoney']=""
        self.fields['parentmoney'].queryset = Money.objects.filter(amount__gt=self.initial['amount']).order_by('-amount')
    class Meta:
        model = Money
        fields = ['amount', 'moneyinout', 'user', 'cashtype', 'parentmoney']
        labels = {'amount' : 'Amount', 'moneyinout': 'Money In/Out', 'user': 'User', 'cashtype': 'cashtype', 'parentmoney': 'parentmoney'}
