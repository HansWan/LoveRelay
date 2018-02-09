from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required

from .models import Money, Cashtype
from django.contrib.auth.models import User

from django.forms import inlineformset_factory

from .forms import MoneyForm, RequestForm, MoneydetailForm, MoneylistForm

# Create your views here.
def index(request):
    return render(request, 'lr/index.html')

@login_required
def money(request):
    moneys = Money.objects.filter(user=request.user).order_by('-amount')
    for money in moneys:
        money.candelete = not money.money_set.count()
        money.canrefund = (money.moneyinout.id == 2)
    context = {'moneys': moneys}
    return render(request, 'lr/moneys.html', context)

@login_required
def donation(request):
    if request.method != 'POST':
        form = MoneyForm(initial={'user': request.user})
    else:
        form = MoneyForm(request.POST)
        if form.is_valid():
            if validate_money(request, form):
                form.save()
                return HttpResponseRedirect(reverse('lr:moneys'))
    context =  {'form': form}
    return render(request, 'lr/donation.html', context)

@login_required
def request(request):
    if request.method != 'POST':
        form = RequestForm(initial={'user': request.user, 'moneyinout': 2})
    else:
        form = RequestForm(request.POST)
        if form.is_valid():
            if validate_money(request, form):
                form.save()
                return HttpResponseRedirect(reverse('lr:moneys'))
    context =  {'form': form}
    return render(request, 'lr/request.html', context)

@login_required
def refund(request, money_id):
    money = Money.objects.get(id=money_id)
    
    if money.moneyinout.id == 1:      #income, not allowed to refund
        context = {'msg': 'The # ' + str(money_id) + ' is an income item, and not allowed to refund.'}
        return render(request, 'lr/showmsg.html', context)
    if request.method != 'POST':
        form = MoneyForm(instance=money)
    else:
        form = MoneyForm(data={'amount': request.POST['amount'], 'moneyinout': 1, 'parentmoney': money_id, 'cashtype': 1, 'user': request.POST['user']})
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('lr:moneys'))
    context = {'money_id': money_id, 'form': form}
    return render(request, 'lr/refund.html', context)
        
def moneylist(request):
    cashtype = Cashtype.objects.get(id=2)
    
    MoneylistFormSet = inlineformset_factory(Cashtype, Money, fields=('amount','user', 'parentmoney',))
    if request.method == 'POST':
        formset = MoneylistFormSet(request.POST, request.FILES, instance=cashtype)
        if form.is_valid():
            pass
    else:
        formset = MoneylistFormSet(instance=cashtype)
    context = {'formset': formset}
    return render(request, 'lr/moneylist.html', context)

def new_money(request):
    if request.method != 'POST':
        form = MoneyForm()
    else:
        form = MoneyForm(request.POST)
        if form.is_valid():
            if validate_money(request, form):
                form.save()
                return HttpResponseRedirect(reverse('lr:moneys'))
    context =  {'form': form}
    return render(request, 'lr/new_money.html', context)
    
def edit_money(request, money_id):
    money = Money.objects.get(id=money_id)
    
    if request.method != 'POST':
        form = MoneyForm(instance=money)
    else:
        form = MoneyForm(instance=money, data=request.POST)
        if form.is_valid():
            if validate_money(request, form):
                form.save()
                return HttpResponseRedirect(reverse('lr:moneys'))
    context = {'money_id': money_id, 'form': form}
    return render(request, 'lr/edit_money.html', context)

def delete_money(request, money_id):
    try:
        money = Money.objects.get(id=money_id)
    except:    #money not found
        context = {'money_id': money_id, 'moneyexist': False, 'search_result': 'Money not found. Please try again.', 'parentmoneyexist': 'False'}
        return render(request, 'lr/search_money_result.html', context)
    form = MoneyForm(instance=money)
    money.candelete = not money.money_set.count()   #not a parentmoney
    if request.method != 'POST':
#        context = {'money_id': money_id, 'form': form, 'candelete': candelete}
        context = {'money_id': money_id, 'form': form, 'money': money, 'moneyexist': True, 'search_result': 'Money detail information:', 'parentmoneyexist': money.candelete}
#            context = {'money_id': money_id, 'form': form}
        return render(request, 'lr/delete_money.html', context)
    else:
        #check if money is referenced by another money as its parentmoney
        if money.candelete:   #not a parentmoney
            money.delete()
            return HttpResponseRedirect(reverse('lr:moneys'))
#        else:
#            context = {'money_id': money_id, 'form': form, 'candelete': candelete}
#            return render(request, 'lr/delete_money.html', context)
        
def validate_money(request, form):
    #must store amount, otherwise errors occur if use below value twice
    pass
#    new_amount = form.cleaned_data['amount']

    #outcome must have a parentmoney, and it must be less then parentmoney amount
#    if form.cleaned_data['moneyinout'].moneyinout == 'outcome':
#        if form.cleaned_data['parentmoney'] == None:
#            pass
#            form.add_error("parentmoney", "Please set a parentmoney if you use money!")
#        elif new_amount > form.cleaned_data['parentmoney'].amount:
#            form.add_error("amount", "Please don't put money bigger than its parent money!")

    #if income, set parentmoney blank
#    if form.cleaned_data['moneyinout'].moneyinout == 'income':
#        form.cleaned_data['parentmoney'] = ""
#        context = {'money_id': money_id, 'form': form}
#        render(request, 'lr/edit_money.html', context)
        
    #no need to check amount if income

    if form.errors:
        return False
    else:
        return True


def search_money(request):
    if request.method != 'POST':
        money = Money()
#        money = Money.objects.get(id=4)
        form = MoneydetailForm(instance=money)
        context = {'form': form}
        return render(request, 'lr/search_money.html', context)
#    else :
#    return render(request, 'lr/search_money.html')

def search_money_result(request, money_id):
    try:
        money = Money.objects.get(id=money_id)
#        if money:
#        if request.method != 'POST':
        form = MoneyForm(instance=money)
        context = {'money_id': money_id, 'form': form, 'search_result': 'Money found:'}
#        else:
    except:    #no corresponding id
        context = {'money_id': money_id, 'search_result': 'No money found! Please try again.'}
    return render(request, 'lr/search_money_result.html', context)
    
def test(request):
    image_data = open("lr/a.jpg", "rb").read()
    return HttpResponse(image_data, mimetype="image/jpg")   

def showobj(obj):
    f = open("c://temp//1.txt", "a+")
    for x in obj:
        f.write(str(x)+'\n')
        
    f.close()
        
        # import time
        # f0 = open("c://temp//1.txt", "a+")
        # f0.write(time.asctime(time.localtime(time.time()))+'\n')
        # ini = 'dict'
        # for k, v in self.instance.__dict__.items():
            # f0.write(ini+'_k: '+k+'   '+ini+'_v: '+str(v)+'\n')
        # f0.write(time.asctime(time.localtime(time.time()))+'\n')
        # f0.close()


