from django.conf.urls import url

from . import views

app_name = 'lr'
urlpatterns = [
    
    url(r'^$', views.index, name='index'),
    url(r'^money/$', views.money, name='moneys'),
    url(r'^new_money/$', views.new_money, name='new_money'),
    url(r'^edit_money/(?P<money_id>\d+)/$', views.edit_money, name='edit_money'),
]
