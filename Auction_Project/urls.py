from django.conf.urls import url, include
from django.contrib import admin
from rest_framework.urlpatterns import format_suffix_patterns
# from django.conf.urls.i18n import i18n_patterns
from netstore.views import *

urlpatterns = [

    url(r'^admin/', admin.site.urls),
    url(r'^$', IndexView.as_view(), name='index'),
    url(r'^create_user/$', CreateUser.as_view(), name='create_user'),
    url(r'^edit_user/$', edit_user, name='edit_user'),
    url(r'^login/$', Login.as_view(), name='login'),
    url(r'^logout/$', logout_view, name='logout'),
    url(r'^change_pw/$', change_pw, name='change_pw'),
    url(r'^(?P<pk>[0-9]+)/$', auction_detail, name='auction_detail'),
    # url(r'^(?P<pk>[0-9]+)/$', DetailView.as_view(), name='auction_detail'),
    url(r'^create_auction/$', create_auction, name='create_auction'),
    url(r'^confirm_auction/$', confirm_auction),
    url(r'^edit_auction/(?P<id>[0-9]+)', edit_auction, name='edit_auction'),
    url(r'^search/$', search_auction, name='search_auction'),
    url(r'^bidding/(?P<pk>[0-9]+)', bidding, name='bidding'),
    url(r'^ban_auction/(?P<id>[0-9]+)', ban_auction, name='ban_auction'),
    url(r'^auction_api/$', AuctionAPI.as_view(), name='auction_api'),
    url(r'^search_api/$', SearchAPIView.as_view(), name='search_api'),
    url(r'^i18n/', include('django.conf.urls.i18n')),

]

urlpatterns = format_suffix_patterns(urlpatterns)


# urlpatterns += i18n_patterns(url(r'^i18n/', include('django.conf.urls.i18n')),)
