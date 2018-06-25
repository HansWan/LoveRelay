from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.http import HttpResponse
import json
from django.core import serializers
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.db import connection
import hashlib
from lxml import etree
from django.utils.encoding import smart_str
#below line shoud be removed after test
from django.views.decorators.csrf import csrf_exempt
from wechat_sdk import WechatBasic
from wechat_sdk.exceptions import ParseError
from wechat_sdk.messages import TextMessage

import numpy as np
import matplotlib
matplotlib.use('Agg')    #without this line not possible to draw a picture in linux
import matplotlib.pyplot as plt
#plt.rcParams['font.sas-serif']=['simhei'] #用来正常显示中文标签
#plt.rcParams['axes.unicode_minus']=False #用来正常显示负号

from pylab import *  
#mpl.rcParams['font.sans-serif'] = ['SimHei'] 

from io import BytesIO
import pygal
import random
import base64        #used to encode plt picture data to base64 and transfer them to template

from .models import Money, Cashtype, Moneynode, Wechatreplymsg
from django.contrib.auth.models import User
#from django.forms import inlineformset_factory
from .forms import MoneyForm, RequestForm, MoneydetailForm, MoneylistForm

# Create your views here.
@csrf_exempt
def index(request):
    WECHAT_TOKEN = 'myweixinpassword'
    AppID = 'wx3370960315272e32'
    AppSecret = 'e6d6b879a09b13d5b19f8fda241adc6c'
    MAX_REPLY_LENGTH = 630    #每次回复的文本最大长度
    # 实例化 WechatBasic
    wechat_instance = WechatBasic(
        token=WECHAT_TOKEN,
        appid=AppID,
        appsecret=AppSecret
    )   
    
    if request.method == 'GET':
        try:
            signature = request.GET.get('signature', None)
        except:
            pass
        if signature == None:           #正常的L访问
            return render(request, 'lr/index.html')
        # 下面是微信公众号发来的验证本机的消息    
        # 检验合法性
        # 从 request 中提取基本信息 (signature, timestamp, nonce, xml)
        signature = request.GET.get('signature')
        timestamp = request.GET.get('timestamp')
        nonce = request.GET.get('nonce')
        if not wechat_instance.check_signature(signature=signature, timestamp=timestamp, nonce=nonce):
            return HttpResponseBadRequest('Verify Failed')
        return HttpResponse(request.GET.get('echostr', ''), content_type="text/plain")
    # 解析本次请求的 XML 数据
    try:
        wechat_instance.parse_data(data=request.body)
    except ParseError:
        return HttpResponseBadRequest('Invalid XML Data')
    # 获取解析好的微信请求信息
    message = wechat_instance.get_message()
    # 关注事件以及不匹配时的默认回复
    if isinstance(message, TextMessage):
        # 当前会话内容
        content = message.content.strip()
        if content == "news":
            response = wechat_instance.response_news([
                {
                    'title': u'新闻标题',
                    'description': u'新闻描述',
                    'picurl': u"https://ss1.bdstatic.com/70cFuXSh_Q1YnxGkpoWK1HF6hhy/it/u=1187077172,2563639533&amp;fm=200&amp;gp=0.jpg",
                    'url': u'http://www.baidu.com/',
                }
            ])

        elif content.endswith("新闻"):
            response = wechat_instance.response_text(content='去看看头条新闻吧，https://www.toutiao.com/ch/news_hot/')

        elif content.endswith("图片"):
            urls = []
            rooturl = 'http://www.ivsky.com/tupian'
            keywords = [content.strip('图片')]
            #if no keywords input then give random keywords
            if not content.strip('图片'):
                keywords = [random.choice(['动物', '风光', '花卉', '海洋', '城市', '节日', '艺术'])]
            urls = get_urls_by_keywords(rooturl, keywords)
            if not urls:
                reply_text = "没找到你要的图片，过一会儿再说吧？/::)"
                response = wechat_instance.response_text(content=reply_text)
            else:
                #find contents from urls
                contents = []
                contents = get_contents_from_urls(urls)
                if not contents:
                    reply_text = "没找到你要的图片，过一会儿再说吧？/::)"
                    response = wechat_instance.response_text(content=reply_text)
                else:
                    picture = random.choice(contents)
                    response = wechat_instance.response_news([
                        {
                            'title': picture['title'],
                            'picurl': picture['picurl'],
                        }
                    ])
            
        elif content == "笑话":
            reply_text = ""        
            rooturl = 'http://xiaohua.zol.com.cn/new/' + str(random.choice(range(2,5000))) + '.html'
            urls = [rooturl]
            #find contents from urls
            contents = []
            contents = get_contents_from_urls(urls)
            if not contents:
                reply_text = "没找到你要的笑话，过一会儿再说吧？/::)"
                response = wechat_instance.response_text(content=reply_text)
            else:
                #从列表里面随机挑一个，把网址发给函数取正文
                url = random.choice(contents)['url']
                joke = get_detail_from_url(url)
                if len(joke) > MAX_REPLY_LENGTH:
                    reply_text = joke[0:MAX_REPLY_LENGTH] + "..." + "\n\n" + "【内容太长，没有完全显示，点这里看全文：" + url + "】"
                else:
                    reply_text = joke
                if not reply_text:
                    reply_text = "没找到你要的笑话，过一会儿再说吧？/::)"
                response = wechat_instance.response_text(content=reply_text)

        elif content == "天气":
            import urllib.request
            from bs4 import BeautifulSoup
            from lxml import etree
            url = 'http://www.weather.com.cn/weather/101200101.shtml'
            headers = {'User-Agent':'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:52.0) Gecko/20100101 Firefox/52.0'}
            req=urllib.request.Request(url=url,headers=headers)
            resp = urllib.request.urlopen(req)
            html = resp.read()
            selector = etree.HTML(html)
            day1_date = selector.xpath('//*[@id="7d"]/ul/li[1]/h1/text()')[0]
            day1_weather = selector.xpath('//*[@id="7d"]/ul/li[1]/p[1]/text()')[0]
            if selector.xpath('//*[@id="7d"]/ul/li[1]/p[2]/span/text()'):  
                day1_temp_h = selector.xpath('//*[@id="7d"]/ul/li[1]/p[2]/span/text()')[0] + '/'
            else:
                day1_temp_h = ""
            day1_temp_l = selector.xpath('//*[@id="7d"]/ul/li[1]/p[2]/i/text()')[0]
            day1_wind = selector.xpath('//*[@id="7d"]/ul/li[1]/p[3]/i/text()')[0]
            day1_text = day1_date + day1_weather + ", " + day1_temp_h + day1_temp_l + ", 风力" + day1_wind

            day2_date = selector.xpath('//*[@id="7d"]/ul/li[2]/h1/text()')[0]
            day2_weather = selector.xpath('//*[@id="7d"]/ul/li[2]/p[1]/text()')[0]
            day2_temp_h = selector.xpath('//*[@id="7d"]/ul/li[2]/p[2]/span/text()')[0]
            day2_temp_l = selector.xpath('//*[@id="7d"]/ul/li[2]/p[2]/i/text()')[0]
            day2_wind = selector.xpath('//*[@id="7d"]/ul/li[2]/p[3]/i/text()')[0]
            day2_text = day2_date + day2_weather + ", " + day2_temp_h + "/" + day2_temp_l + ", 风力" + day2_wind

            day3_date = selector.xpath('//*[@id="7d"]/ul/li[3]/h1/text()')[0]
            day3_weather = selector.xpath('//*[@id="7d"]/ul/li[3]/p[1]/text()')[0]
            day3_temp_h = selector.xpath('//*[@id="7d"]/ul/li[3]/p[2]/span/text()')[0]
            day3_temp_l = selector.xpath('//*[@id="7d"]/ul/li[3]/p[2]/i/text()')[0]
            day3_wind = selector.xpath('//*[@id="7d"]/ul/li[3]/p[3]/i/text()')[0]
            day3_text = day3_date + day3_weather + ", " + day3_temp_h + "/" + day3_temp_l + ", 风力" + day3_wind

            day4_date = selector.xpath('//*[@id="7d"]/ul/li[4]/h1/text()')[0]
            day4_weather = selector.xpath('//*[@id="7d"]/ul/li[4]/p[1]/text()')[0]
            day4_temp_h = selector.xpath('//*[@id="7d"]/ul/li[4]/p[2]/span/text()')[0]
            day4_temp_l = selector.xpath('//*[@id="7d"]/ul/li[4]/p[2]/i/text()')[0]
            day4_wind = selector.xpath('//*[@id="7d"]/ul/li[4]/p[3]/i/text()')[0]
            day4_text = day4_date + day4_weather + ", " + day4_temp_h + "/" + day4_temp_l + ", 风力" + day4_wind

            reply_text = day1_text + '\n' + day2_text + '\n' + day3_text + '\n' + day4_text + '\n'
            response = wechat_instance.response_text(content=reply_text)
            
        elif content == "故事":
            reply_text = ""        
            rooturl = 'https://www.jianshu.com'
            keywords = [
                '故事',
            ]

            urls = get_urls_by_keywords(rooturl, keywords)


        ##################################################################

#            if len(urls):
#                reply_text = urls[1]
#            else:
#                reply_text = "没找到你要的故事，过一会儿再说吧？/::)"
#            reply_text = len(urls)
#            response = wechat_instance.response_text(content=reply_text)
#            return HttpResponse(response, content_type="application/xml")

        ##################################################################






            if not urls:
                reply_text = "没找到你要的故事，过一会儿再说吧？/::)"
                response = wechat_instance.response_text(content=reply_text)
            else:
                #find contents from urls
                contents = []
                contents = get_contents_from_urls(urls)
                if not contents:
                    reply_text = "没找到你要的故事，过一会儿再说吧？/::)"
                    response = wechat_instance.response_text(content=reply_text)
                else:
                    #从列表里面随机挑一个，把网址发给函数取正文
                    url = random.choice(contents)['url']
                    story = get_detail_from_url(url)
                    if len(story) > MAX_REPLY_LENGTH:
                        reply_text = story[0:MAX_REPLY_LENGTH] + "..." + "\n\n" + "【内容太长，没有完全显示，点这里看全文：" + url + "】"
        #                reply_text = story[0:500] + "..." + "\n\n" + "<a href=" + "'" + rooturl+nodes[story_i] + "'" + ">点这里看完整的故事</a>"
                    else:
                        reply_text = story
                    if not reply_text:
                        reply_text = "没找到你要的故事，过一会儿再说吧？/::)"
                    response = wechat_instance.response_text(content=reply_text)
            
        else:
            reply_text = getwechatreplymsg(content)
            if not reply_text:
                reply_text = '功能还在完善中，稍候哈。。。/::)'
            #if content == '功能':
            #elif content.endswith('万俊'):
                #reply_text = (
                        #'目前支持的功能：\n1. 输入姓名查手机号，\n'
                        #'2. 回复任意词语，查天气，陪聊天，讲故事，无所不能！\n'
                        #'还有更多功能正在开发中哦 ^_^\n'
                        #'\n【<a href="http://loverelay.51vip.biz">爱心接力站</a>】'
                    #)
            response = wechat_instance.response_text(content=reply_text)
    elif isinstance(message, ImageMessage):
        content = message.content
    else:
        response = wechat_instance.response_text(
            content = (
                '感谢关注！\n回复【功能】两个字查看支持的功能，还可以回复任意内容开始聊天。。。/::)'
                ))

    return HttpResponse(response, content_type="application/xml")

def getwechatreplymsg(keyword):
    #find a reply msg from mysql db and return
    wechatreplymsgs = Wechatreplymsg.objects.filter(keyword=keyword)
    msg = ""
    for wechatreplymsg in wechatreplymsgs:
        msg = msg + wechatreplymsg.keyword + ": \n" + wechatreplymsg.replymsg + "\n"
    return msg
    
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
    hist.add("", x)
#    hist.x_title = '捐赠ID'
#    hist.y_title = '捐赠金额'
    hist.x_title = 'ID'
    hist.y_title = 'amount'
#    picture_data = hist.render_data_uri()     #document里面是这样用，但是在IE里显示成黑块，firefox什么都不显示
    picture_data = base64.b64encode(hist.render_to_png()).decode(encoding='utf-8')
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
#    plt.xlabel('捐赠ID')
#    plt.ylabel('捐赠金额')
    plt.xlabel('ID')
    plt.ylabel('amount')
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

def get_urls_by_keywords(url, keywords):
    import urllib.request
    from bs4 import BeautifulSoup
    from lxml import etree
    headers = {'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:23.0) Gecko/20100101 Firefox/23.0'}  
    req = urllib.request.Request(url=url, headers=headers)  
    resp = urllib.request.urlopen(req)
    html = resp.read()
    selector = etree.HTML(html)
    urls = []
    #图片天堂
    if 'www.ivsky.com' in url:
        rooturl = 'http://www.ivsky.com'
        node_tpmenu = []
        node_sline = []
        for kw in keywords:
            node_tpmenu = selector.xpath("//ul[@class='tpmenu']/descendant::a[contains(text(), $kw)]/@href", kw=kw)
            node_sline = selector.xpath("//div[@class='sline']/descendant::a[contains(text(), $kw)]/@href", kw=kw)
            for node in node_tpmenu:
                if rooturl+node not in urls:
                    urls.append(rooturl+node)
            for node in node_sline:
                if rooturl+node not in urls:
                    urls.append(rooturl+node)
    #jianshu story
    elif 'www.jianshu.com' in url:
        rooturl = 'https://www.jianshu.com'
        #story
        for kw in keywords:
#            nodes = selector.xpath('//div[text()=$kw]/@href', kw=kw)
            nodes = selector.xpath('//a[contains(string(), $kw)]/@href', kw=kw)
        for node in nodes:
            if rooturl+node not in urls:
                urls.append(rooturl+node)
    return urls

def get_contents_from_urls(urls):
    import urllib.request
    from bs4 import BeautifulSoup
    from lxml import etree
    headers = {'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:23.0) Gecko/20100101 Firefox/23.0'}  
    contents = []
    for url in urls:
        #图片天堂
        if 'www.ivsky.com' in url:
            req = urllib.request.Request(url=url, headers=headers)  
            resp = urllib.request.urlopen(req)
            html = resp.read()
            selector = etree.HTML(html)
            nodes = selector.xpath("//div[@class='il_img']/descendant::img")
            for i in range(0, len(nodes)):
                print(i)
                node_title = selector.xpath("//div[@class='il_img']/descendant::img/@alt")[i] + "【转自ivsky.com】"
                node_link = selector.xpath("//div[@class='il_img']/descendant::img/@src")[i]
                content = {}
                content['title'] = node_title
                content['picurl'] = node_link
                contents.append(content)
        #jianshu story
        elif 'www.jianshu.com' in url:
            rooturl = 'https://www.jianshu.com'
            req = urllib.request.Request(url=url, headers=headers)  
            resp = urllib.request.urlopen(req)
            html = resp.read()
            selector = etree.HTML(html)
            nodes = selector.xpath("//a[@class='title']")
            for i in range(0, len(nodes)):
                node_title = selector.xpath("//a[@class='title']/text()")[i] + "【转自jianshu.com】"
                node_link = selector.xpath("//a[@class='title']/@href")[i]
                content = {}
                content['title'] = node_title
                content['url'] = rooturl + node_link
                contents.append(content)
        #joke
        elif 'xiaohua.zol.com.cn' in url:
            rooturl = 'http://xiaohua.zol.com.cn'
            req = urllib.request.Request(url=url, headers=headers)  
            resp = urllib.request.urlopen(req)
            html = resp.read()
            selector = etree.HTML(html)
            nodes = selector.xpath("//span[@class='article-title']/a")
            for i in range(0, len(nodes)):
                node_title = selector.xpath("//span[@class='article-title']/a/text()")[i] + "【转自zol.com.cn】"
                node_link = selector.xpath("//span[@class='article-title']/a/@href")[i]
                content = {}
                content['title'] = node_title
                content['url'] = rooturl + node_link
                contents.append(content)
    return contents

def get_detail_from_url(url):
    import urllib.request
    from bs4 import BeautifulSoup
    from lxml import etree
    headers = {'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:23.0) Gecko/20100101 Firefox/23.0'}  
    detail = ''
#    for url in urls:
    #jianshu story
    if 'www.jianshu.com' in url:
        req = urllib.request.Request(url=url, headers=headers)  
        resp = urllib.request.urlopen(req)
        html = resp.read()
        selector = etree.HTML(html)
        title = selector.xpath("//h1[@class='title']/text()")[0] + "【摘录自简书】"
        xpath = "//p/text()"
        nodes = selector.xpath(xpath)
        detail = title
        for node in nodes:
            detail = detail + "\n" + node
    elif 'xiaohua.zol.com.cn' in url:
        req = urllib.request.Request(url=url, headers=headers)  
        resp = urllib.request.urlopen(req)
        html = resp.read()
        selector = etree.HTML(html)
        xpath = "//h1[@class='article-title']/text()"
        title = selector.xpath(xpath)[0] + "【摘录自笑话大全】"
        xpath = "//div[@class='article-text']/descendant-or-self::*/text()"
        nodes = selector.xpath(xpath)
        detail = title
        for node in nodes:
            detail = detail + "\n" + node
    return detail

def getword(request, word):
    import urllib.request
    from lxml import etree
    url = 'http://www.iciba.com/' + word
    headers = {'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:23.0) Gecko/20100101 Firefox/23.0'}  
    req = urllib.request.Request(url=url, headers=headers)  
    resp = urllib.request.urlopen(req)
    html = resp.read()
    selector = etree.HTML(html)
    phonetic_symbols = selector.xpath("//div[@class='base-speak']//span/text()")
    phonetic_symbol = ''
    for i in range(len(phonetic_symbols)):
        if ('[' in phonetic_symbols[i]):
            phonetic_symbol = phonetic_symbol + phonetic_symbols[i] + "   "
    word_cn = {}
    cn = []
    cns = selector.xpath("//ul[@class='base-list switch_part']/li")
    for i in range(1, len(cns)+1):
        cn_class = selector.xpath("//ul[@class='base-list switch_part']/li["+str(i)+"]/span/text()")[0]              #词性
        cn_cns = selector.xpath("//ul[@class='base-list switch_part']/li["+str(i)+"]/p//span/text()")              #词义
        cn_cn = ""
        for j in range(0, len(cn_cns)):
            cn_cn = cn_cn + selector.xpath("//ul[@class='base-list switch_part']/li["+str(i)+"]/p//span/text()")[j]
        cn.append(cn_class + ' ' + cn_cn)
    word_cn['en'] = word
    word_cn['phonetic_symbol'] = phonetic_symbol
    word_cn['cn'] = cn
    return HttpResponse(json.dumps(word_cn), content_type="application/json")    

def getwordslib(request, lib_id):
    words = []
    with open("/usr/local/itl/python/LoveRelay/static/wordslibs.txt", 'r', encoding='UTF-8') as wordslibsfile:  
        for line in wordslibsfile:  
            (libid, libname, wordsquantity, ready) = line.strip().split('\t') 
            if libid == lib_id: 
                libfilename = "/usr/local/itl/python/LoveRelay/static/" + str(libid) + "）.txt"
                with open(libfilename, 'r', encoding='UTF-8') as wordsfile:  
                    for line in wordsfile:  
                        (en, phonetic_symbol, cn) = line.strip().split('\t')  
                        dict = {}
                        dict['English'] = en.strip(' ').strip('\xa0')
                        dict['Phonetic_symbol'] = phonetic_symbol.strip(' ').strip('\xa0')
                        dict['Chinese'] = cn.strip(' ').strip('\xa0')
                        words.append(dict) 
                data = words
                return HttpResponse(json.dumps(data), content_type="application/json")

def getwordslibs(request):
    wordslibs = []
    with open("/usr/local/itl/python/LoveRelay/static/wordslibs.txt", 'r', encoding='UTF-8') as wordslibsfile:  
        for line in wordslibsfile:  
            (libid, libname, wordsquantity, ready) = line.strip().split('\t') 
            if ready: 
                dict = {}
                dict['libid'] = libid.strip(' ').strip('\xa0')
                dict['libname'] = libname.strip(' ').strip('\xa0')
                dict['wordsquantity'] = wordsquantity.strip(' ').strip('\xa0')
                wordslibs.append(dict) 
    data = wordslibs
    return HttpResponse(json.dumps(data), content_type="application/json")
                
def test(request):
    from selenium import webdriver
    url='http://www.weather.com.cn/weather/101200101.shtml'
#            browser = webdriver.Chrome()
#    browser = webdriver.Firefox()
    browser = webdriver.Firefox(log_path="/tmp/1.txt")
    #browser.get(url)
    #today_date = browser.find_element_by_xpath('//*[@id="7d"]/ul/li[1]/h1').text
    #today_weather = browser.find_element_by_xpath('//*[@id="7d"]/ul/li[1]/p[1]').text
    #today_temp = browser.find_element_by_xpath('//*[@id="7d"]/ul/li[1]/p[2]/i').text
    #today_wind = browser.find_element_by_xpath('//*[@id="7d"]/ul/li[1]/p[3]/i').text
    #reply_text = today_date + today_weather + ", " + today_temp + ", 风力" + today_wind
    #response = wechat_instance.response_text("content=reply_text")

##################################################################
    import time
    f0 = open("/tmp/1.txt", "a+")
    f0.write(time.asctime(time.localtime(time.time()))+'\n')
    ini = 'tfname'
#    f0.write(ini+': '+str(picture_html)+'\n')
    f0.write(time.asctime(time.localtime(time.time()))+'\n')
    f0.close()
##################################################################
    return HttpResponse('test ok')

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

