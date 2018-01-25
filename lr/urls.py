from django.conf.urls import url
from django.views.generic import TemplateView

from . import views

app_name = 'lr'
urlpatterns = [
    
    url(r'^$', views.index, name='index'),
    url(r'^money/$', views.money, name='moneys'),
    url(r'^new_money/$', views.new_money, name='new_money'),
    url(r'^edit_money/(?P<money_id>\d+)/$', views.edit_money, name='edit_money'),
    url(r'^search_money/$', views.search_money, name='search_money'),
    url(r'^search_money_result/(?P<money_id>\d+)/$', views.search_money_result, name='search_money_result'),
#    url(r'^t.html', TemplateView.as_view(template_name='lr/t.html'), name='t'),
]



