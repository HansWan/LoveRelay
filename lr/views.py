from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.urls import reverse
#from django.core.urlresolvers import reverse    #removed

from .models import Money
from .forms import MoneyForm

# Create your views here.
def index(request):
    return render(request, 'lr/index.html')

def money(request):
    moneys = Money.objects.order_by('-amount')
    for money in moneys:
        money.candelete = not money.money_set.count()
    context = {'moneys': moneys}
    return render(request, 'lr/moneys.html', context)
    
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
#    context = {'money_id': money_id, 'form': form, 'search_result': 'Parent money. Not allowed to delete.'}
#    return render(request, 'lr/search_money_result.html', context)
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

    new_amount = form.cleaned_data['amount']

    #outcome must have a parentmoney, and it must be less then parentmoney amount
    if form.cleaned_data['moneyinout'].moneyinout == 'outcome':
        if form.cleaned_data['parentmoney'] == None:
            form.add_error("parentmoney", "Please set a parentmoney if you use money!")
        elif new_amount > form.cleaned_data['parentmoney'].amount:
            form.add_error("amount", "Please don't put money bigger than its parent money!")

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
    return render(request, 'lr/search_money.html')

def search_money_result(request, money_id):
    try:
        money = Money.objects.get(id=money_id)
#        if money:
#        if request.method != 'POST':
        form = MoneyForm(instance=money)
        context = {'money_id': money_id, 'form': form, 'search_result': 'Money found:'}
#        else:
    except:    #no corresponding id
        context = {'money_id': money_id, 'search_result': 'No money found. Please try again.'}
    return render(request, 'lr/search_money_result.html', context)
    
    
