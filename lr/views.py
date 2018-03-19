from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.http import HttpResponse
import json
from django.core import serializers
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.db import connection

import numpy as np
import matplotlib
matplotlib.use('Agg')    #without this line not possible to draw a picture in linux
import matplotlib.pyplot as plt
from io import BytesIO
import pygal
import random
import base64        #used to encode plt picture data to base64 and transfer them to template

from .models import Money, Cashtype, Moneynode
from django.contrib.auth.models import User

from django.forms import inlineformset_factory

from .forms import MoneyForm, RequestForm, MoneydetailForm, MoneylistForm

# Create your views here.
def index(request):
    return render(request, 'lr/index.html')

@login_required
def money(request):
    moneys = Money.objects.filter(user=request.user, parentmoney=None).order_by('-amount')
    hist = pygal.Bar(width=200, height=150)
    x = []
    for money in moneys:
        money.candelete = not money.money_set.count()
        money.haschild = money.money_set.count()
        money.hasparent = money.parentmoney
        money.canrefund = (money.purpose.id == 4)
        x.append(money.amount)
    hist.add('n', x)
    picture_data = base64.b64encode(hist.render()).decode(encoding='utf-8')
    context = {'moneys': moneys, 'picture_data': picture_data}
    return render(request, 'lr/moneys.html', context)

@login_required
def donation(request):
    if request.method != 'POST':
        form = MoneyForm(initial={'user': request.user, 'purpose': 1})
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
        form = RequestForm(initial={'user': request.user, 'purpose': 2})
    else:
        form = RequestForm(request.POST)
        if form.is_valid():
            if validate_money(request, form):
                form.save()
                return HttpResponseRedirect(reverse('lr:moneys'))
    context =  {'form': form}
    return render(request, 'lr/request.html', context)

@login_required
def loan(request):
    if request.method != 'POST':
        form = RequestForm(initial={'user': request.user, 'purpose': 4})
    else:
        form = RequestForm(request.POST)
        if form.is_valid():
            if validate_money(request, form):
                form.save()
                return HttpResponseRedirect(reverse('lr:moneys'))
    context =  {'form': form}
    return render(request, 'lr/loan.html', context)

@login_required
def refund(request, money_id):
    money = Money.objects.get(id=money_id)
    
    if money.purpose.id != 4:      #income, not allowed to refund
        context = {'msg': 'The # ' + str(money_id) + ' is not a load item, and not allowed to refund.'}
        return render(request, 'lr/showmsg.html', context)
    if request.method != 'POST':
        form = MoneyForm(instance=money)
    else:
        form = MoneyForm(data={'amount': request.POST['amount'], 'purpose': 3, 'parentmoney': money_id, 'cashtype': 1, 'user': request.POST['user']})
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

def moneytrack(request, money_id):
    moneys = Money.objects.filter(id=money_id)
    if not moneys:
        context = {'msg': 'The # ' + str(money_id) + ' does not exist, please try again.'}
        return render(request, 'lr/showmsg.html', context)
    #get child records
    cursor = connection.cursor()
    cursor.execute("call listchild(%s, @p1)", (str(money_id),))
    cur2 = connection.cursor()
    cur2.execute("select @p1")
    sessionid0 = cur2.fetchone()
    moneys = Moneynode.objects.filter(sessionid=str(sessionid0[0], encoding='utf8'))
    x_values = []
    for money in moneys:
        m = Money.objects.filter(id=money.money_id)[0]
        money.candelete = not m.money_set.count()
        money.haschild = m.money_set.count()
        money.hasparent = m.parentmoney
        money.canrefund = (money.purpose.id == 4)
        x_values.append(m.amount)
    #create a picture
    plt.plot(x_values)
    canvas = plt.get_current_fig_manager().canvas
    buffer = BytesIO()
    canvas.print_png(buffer)
    picture_data = base64.b64encode(buffer.getvalue()).decode(encoding='utf-8')
    buffer.close()
    plt.close('all')
    context = {'moneys': moneys, 'picture_data': picture_data}
    return render(request, 'lr/moneytrack.html', context)
    
def query(request, money_id):
    moneys = Money.objects.filter(id=money_id)
    if not moneys:
        context = {'msg': 'The # ' + str(money_id) + ' does not exist, please try again.'}
        return render(request, 'lr/showmsg.html', context)
    
    cursor = connection.cursor()
    cursor.execute("call listchild(%s, @p1)", (str(money_id),))
    cur2 = connection.cursor()
    cur2.execute("select @p1")
    sessionid0 = cur2.fetchone()
    moneys = Moneynode.objects.filter(sessionid=str(sessionid0[0], encoding='utf8'))
    for money in moneys:
        m = Money.objects.filter(id=money.money_id)[0]
        money.candelete = not m.money_set.count()
        money.haschild = m.money_set.count()
        money.hasparent = m.parentmoney
        money.canrefund = (money.purpose.id == 4)
    context = {'moneys': moneys}
    data = serializers.serialize("json", moneys)
#    return render(request, 'lr/moneytrack.html', context)
#    return HttpResponse(moneys)
#    return HttpResponse(json.dumps(data))
    return HttpResponse(data)
    
def findchildmoney(money_id, seq):
    childmoneyset = Money.objects.filter(parentmoney=money_id)
    if not childmoneyset:
        return childmoneyset

    import time
    f0 = open("c://temp//1.txt", "a+")
    f0.write(time.asctime(time.localtime(time.time()))+'\n')
    ini = 'childmoneyset count'
    f0.write(ini+'_: '+str(childmoneyset.count())+'\n')
    ini = 'childmoneyset id'
    f0.write(ini+'_: '+str(id(childmoneyset))+'\n')
    f0.write(time.asctime(time.localtime(time.time()))+'\n')
    f0.close()


    for cm in childmoneyset:
        cmset = Money.objects.filter(id=cm.id)
        seq += 1
        for money in cmset:
            money.seq = seq


        import time
        f0 = open("c://temp//1.txt", "a+")
        f0.write(time.asctime(time.localtime(time.time()))+'\n')
        ini = 'before inner return seq'
        f0.write('cm.id:  '+str(cm.id)+'\n')
        f0.write(ini+'_: '+str(seq)+'\n')
        f0.write(time.asctime(time.localtime(time.time()))+'\n')
        f0.close()


        yield cmset | findchildmoney(cm.id, seq)


    
        # moneys = moneys.union(cmset)

        # import time
        # f0 = open("c://temp//1.txt", "a+")
        # f0.write(time.asctime(time.localtime(time.time()))+'\n')
        # ini = 'after combile moneys.count()'
        # f0.write(ini+'_: '+str(id(moneys))+':     '+str(moneys.count())+'\n')
        # f0.write(time.asctime(time.localtime(time.time()))+'\n')
        # f0.close()
    
        # findallmoney(cm.id, moneys)

    # import time
    # f0 = open("c://temp//1.txt", "a+")
    # f0.write(time.asctime(time.localtime(time.time()))+'\n')
    # ini = 'moneys.count(), before return'
    # f0.write(ini+'_: '+str(id(moneys))+':     '+str(moneys.count())+'\n')
    # f0.write(time.asctime(time.localtime(time.time()))+'\n')
    # f0.close()

    # return moneys
    
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
#                return HttpResponseRedirect(reverse('lr:moneys'))
                return HttpResponseRedirect(reverse('lr:moneytrack', kwargs={"money_id": money_id}))
                
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

def makegraph(request, money_id, rand):
    data = makepicture(int(money_id))
    return HttpResponse(data, content_type="Image/png")

def makepicture(money_id):
    x_values = []
    for i in range(money_id):
        x_values.append(i*i)
    plt.plot(x_values)
    canvas = plt.get_current_fig_manager().canvas
    buffer = BytesIO()
    canvas.print_png(buffer)
    picture_data = buffer.getvalue()
    buffer.close()
    plt.close('all')
    return picture_data

def makebar(request):
    x = [3,5,2,9,6]
    hist = pygal.Bar(width=200, height=150)
    hist.add('n', x)
    data = hist.render()
    return HttpResponse(data, content_type="Image/svg+xml")

def track(request, money_id, add):
    money_id = int(money_id) + int(add)
    moneys = Money.objects.filter(id=money_id)
    if not moneys:
        context = {'msg': 'The # ' + str(money_id) + ' does not exist, please try again.'}
        return render(request, 'lr/showmsg.html', context)
    
    cursor = connection.cursor()
    cursor.execute("call listchild(%s, @p1)", (str(money_id),))
    cur2 = connection.cursor()
    cur2.execute("select @p1")
    sessionid0 = cur2.fetchone()
    moneys = Moneynode.objects.filter(sessionid=str(sessionid0[0], encoding='utf8'))
    for money in moneys:
        m = Money.objects.filter(id=money.money_id)[0]
        money.candelete = not m.money_set.count()
        money.haschild = m.money_set.count()
        money.hasparent = m.parentmoney
        money.canrefund = (money.purpose.id == 4)
    context = {'moneys': moneys}
    return render(request, 'lr/moneytrack.html', context)
            
def test(request):
    import base64
    x = [0, 1, 2, 3, 4]
    y = [0, 1, 4, 9, 16]
    plt.scatter(x, y)
    canvas = plt.get_current_fig_manager().canvas
    buffer = BytesIO()
    canvas.print_png(buffer)
    picture_data = base64.b64encode(buffer.getvalue()).decode(encoding='utf-8')
    buffer.close()
    picture_html = picture_data
#    picture_html = "iVBORw0KGgoAAAANSUhEUgAAAAkAAAAJAQMAAADaX5RTAAAAA3NCSVQICAjb4U/gAAAABlBMVEX///+ZmZmOUEqyAAAAAnRSTlMA/1uRIrUAAAAJcEhZcwAACusAAArrAYKLDVoAAAAWdEVYdENyZWF0aW9uIFRpbWUAMDkvMjAvMTIGkKG+AAAAHHRFWHRTb2Z0d2FyZQBBZG9iZSBGaXJld29ya3MgQ1M26LyyjAAAAB1JREFUCJljONjA8LiBoZyBwY6BQQZMAtlAkYMNAF1fBs/zPvcnAAAAAElFTkSuQmCC"


##################################################################
    import time
    f0 = open("/tmp/1.txt", "a+")
    f0.write(time.asctime(time.localtime(time.time()))+'\n')
    ini = 'tfname'
    f0.write(ini+': '+str(picture_html)+'\n')
    f0.write(time.asctime(time.localtime(time.time()))+'\n')
    f0.close()
##################################################################



    plt.close('all')
#    context = {'picture_filename': tf.name}
#    context = {'picture_html': picture_html}
    return render(request, 'lr/testpicsrc.html', {'picture_html': picture_html})

def showobj(obj):
    f = open("c://temp//1.txt", "a+")
    for x in obj:
        f.write(str(x)+'\n')
        
    f.close()
        
##################################################################
        # import time
        # f0 = open("c://temp//1.txt", "a+")
        # f0.write(time.asctime(time.localtime(time.time()))+'\n')
        # ini = 'dict'
        # for k, v in self.instance.__dict__.items():
            # f0.write(ini+'_k: '+k+'   '+ini+'_v: '+str(v)+'\n')
        # f0.write(time.asctime(time.localtime(time.time()))+'\n')
        # f0.close()
##################################################################
##################################################################
    # import time
    # f0 = open("c://temp//1.txt", "a+")
    # f0.write(time.asctime(time.localtime(time.time()))+'\n')
    # ini = 'type of response'
    # f0.write(ini+': '+str(type(response))+'\n')
    # f0.write(time.asctime(time.localtime(time.time()))+'\n')
    # f0.close()
##################################################################
##################################################################
    import time
    f0 = open("/tmp/1.txt", "a+")
    f0.write(time.asctime(time.localtime(time.time()))+'\n')
    ini = 'tfname'
    f0.write(ini+': '+tf.name+'\n')
    f0.write(time.asctime(time.localtime(time.time()))+'\n')
    f0.close()
##################################################################

