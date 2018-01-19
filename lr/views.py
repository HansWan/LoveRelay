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
    context = {'moneys': moneys}
    return render(request, 'lr/moneys.html', context)
    
def new_money(request):
    if request.method != 'POST':
        form = MoneyForm()
    else:
        form = MoneyForm(request.POST)
        if form.is_valid():
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
            form.save()
            return HttpResponseRedirect(reverse('lr:moneys'))
    context = {'money_id': money_id, 'form': form}
    return render(request, 'lr/edit_money.html', context)
        
