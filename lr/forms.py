from django import forms
from django.db import connection

from django.contrib.auth.models import User
from .models import Money, Moneynode

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

    def clean_parentmoney(self):
        if self.initial.get('id') != None and self.cleaned_data['parentmoney'] != None:    #need to check if recursive reference exists
            cursor = connection.cursor()
            cursor.execute("call ischild(%s, %s, @p1)", (str(self.cleaned_data['parentmoney'].id), str(self.initial.get('id')),))
            cur2 = connection.cursor()
            cur2.execute("select @p1")
            ischild = cur2.fetchone()[0]
            if ischild == 1:
                self._errors["parentmoney"] = ["父记录被循环引用，请选择另一条父记录。"]
        return self.cleaned_data['parentmoney']
            
        # if self.cleaned_data['parentmoney'] != None:
            # parentmoney = self.cleaned_data['parentmoney']
# #        if str(user) != 'wanjun':
# #            raise forms.ValidationError("Please input correct info.")
            # parentmoney0 = Money.objects.get(id=parentmoney.money_id)
            # return parentmoney0
        # else:
            # return None

    def clean(self):
        form_data = self.cleaned_data
#        if form_data['amount'] > form_data['parentmoney'].amount:
        if form_data['parentmoney'] != None and form_data['amount'] > form_data['parentmoney'].amount:
            self._errors["amount"] = ["请输入低于父记录的金额。"]
            del form_data['amount']
        return form_data
                
    class Meta:
        model = Money
        fields = ['id', 'amount', 'purpose', 'user', 'cashtype', 'beneficiarydesignated', 'parentmoney']
        labels = {'amount' : '金额', 'purpose': '类别', 'user': '用户', 'cashtype': '币种', 'beneficiarydesignated': '指定受益人', 'parentmoney': '父记录'}

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
            self._errors["amount"] = ["请输入低于父记录的金额。"]
            del form_data['amount']
        return form_data
                
    class Meta:
        model = Money
        fields = ['amount', 'purpose', 'user', 'cashtype', 'donatordesignated', 'parentmoney']
        labels = {'amount' : '金额', 'purpose': '类别', 'user': '用户', 'cashtype': '币种', 'donatordesignated': '指定捐赠人', 'parentmoney': '父记录'}

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
        labels = {'id': 'ID', 'amount': '金额', 'purpose': '类别', 'user': '用户', 'cashtype': '币种', 'parentmoney': '父记录', 'test': 'Test'}

class MoneylistForm(forms.Form):
    amount = forms.IntegerField()
    purpose = forms.IntegerField()
    user = forms.CharField()
    cashtype = forms.IntegerField()
    parentmoney = forms.IntegerField()
    
