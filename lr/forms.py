from django import forms
from .models import Money

class MoneyForm(forms.ModelForm):
    class Meta:
        model = Money
        fields = ['amount', 'moneyinout', 'user', 'cashtype', 'parentmoney']
        labels = {'amount' : 'Amount', 'moneyinout': 'Money In/Out', 'user': 'User', 'cashtype': 'cashtype', 'parentmoney': 'parentmoney'}
