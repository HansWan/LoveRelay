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

    def clean_user(self):
        user = self.cleaned_data['user']
#        if str(user) != 'wanjun':
#            raise forms.ValidationError("Please input correct info.")
        return user

    def clean(self):
        form_data = self.cleaned_data
        if form_data['parentmoney'] != None and form_data['amount'] > form_data['parentmoney'].amount:
            self._errors["amount"] = ["Please input amount more then parentmoney."]
            del form_data['amount']
        return form_data
                
    class Meta:
        model = Money
        fields = ['amount', 'moneyinout', 'user', 'cashtype', 'parentmoney']
        labels = {'amount' : 'Amount', 'moneyinout': 'Money In/Out', 'user': 'User', 'cashtype': 'Cashtype', 'parentmoney': 'Parentmoney'}

class MoneydetailForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(MoneydetailForm, self).__init__(*args, **kwargs)
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
        fields = '__all__'
#        fields = ['id', 'amount', 'moneyinout', 'user', 'cashtype', 'parentmoney', 'test']
        labels = {'id': 'ID', 'amount': 'Amount', 'moneyinout': 'Money In/Out', 'user': 'User', 'cashtype': 'Cashtype', 'parentmoney': 'Parentmoney', 'test': 'Test'}

class MoneyFormNew(forms.Form):
    user = forms.CharField()
    amount = forms.IntegerField()
    
