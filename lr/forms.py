from django import forms
from django.contrib.auth.models import User
from .models import Money

class MoneyForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(MoneyForm, self).__init__(*args, **kwargs)
#        self.initial['amount']=888
#        self.initial['moneyinout']=""
#        self.initial['user']=""
#        self.initial['cashtype']=""
#        self.initial['parentmoney']=""
#            if self.initial['moneyinout']==1:
#                self.initial['parentmoney']=""
        
     #set user unchangable
#        try:
        if self.data.get('user') != None:
            self.fields['user'].queryset = User.objects.filter(id=self.data.get('user'))
        else:
            if type(self.initial.get('user')) == int:
                self.fields['user'].queryset = User.objects.filter(id=self.initial.get('user'))
            else:
                self.fields['user'].queryset = User.objects.filter(username=self.initial.get('user'))
#        except:
#            pass

#     #set parentmoney.amount > new amount
#        try:
#            if self.initial['amount'] != None:
#                self.fields['parentmoney'].queryset = Money.objects.filter(amount__gt=self.initial['amount']).order_by('-amount')
#        except:
#            pass
#

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
        fields = ['id', 'amount', 'purpose', 'user', 'cashtype', 'beneficiarydesignated', 'parentmoney']
        labels = {'amount' : 'Amount', 'purpose': 'Purpose', 'user': 'User', 'cashtype': 'Cashtype', 'beneficiarydesignated': 'Beneficiary Designated', 'parentmoney': 'Parentmoney'}

class RequestForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(RequestForm, self).__init__(*args, **kwargs)
        if self.data.get('user') != None:
            self.fields['user'].queryset = User.objects.filter(id=self.data.get('user'))
        else:
            if type(self.initial.get('user')) == int:
                self.fields['user'].queryset = User.objects.filter(id=self.initial.get('user'))
            else:
                self.fields['user'].queryset = User.objects.filter(username=self.initial.get('user'))
        self.fields['parentmoney'].queryset = Money.objects.filter(purpose=1).order_by('-amount')

    def clean(self):
        form_data = self.cleaned_data
        if form_data['parentmoney'] != None and form_data['amount'] > form_data['parentmoney'].amount:
            self._errors["amount"] = ["Please input amount more then parentmoney."]
            del form_data['amount']
        return form_data
                
    class Meta:
        model = Money
        fields = ['amount', 'purpose', 'user', 'cashtype', 'donatordesignated', 'parentmoney']
        labels = {'amount' : 'Amount', 'purpose': 'Purpose', 'user': 'User', 'cashtype': 'Cashtype', 'donatordesignated': 'Donator Designated', 'parentmoney': 'Parentmoney'}

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
        labels = {'id': 'ID', 'amount': 'Amount', 'purpose': 'Purpose', 'user': 'User', 'cashtype': 'Cashtype', 'parentmoney': 'Parentmoney', 'test': 'Test'}

class MoneylistForm(forms.Form):
    amount = forms.IntegerField()
    purpose = forms.IntegerField()
    user = forms.CharField()
    cashtype = forms.IntegerField()
    parentmoney = forms.IntegerField()
    
