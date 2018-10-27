from django.conf.urls import include, url
from django.contrib import admin
from user import views
from  django.contrib.auth.decorators import login_required

urlpatterns = [
    url(r"^$", views.index, name='index'),
    url(r"^register$", views.RegisterView.as_view(), name='register'),
    url(r"^login$", views.LoginView.as_view(), name='login'),
    url(r"^logout$", views.LogoutView.as_view(), name='logout'),
    url(r"^active/(?P<token>.*)$", views.ActiveView.as_view(), name='active'),
    url(r'^validate_code$', views.validate_code, name="validate_code"),
    url(r'^checkusername', views.checkusername, name="checkusername"),

    # url(r'^info$', login_required(views.InfoView.as_view()), name="info"),
    # url(r'^order$', login_required(views.OrderView.as_view()), name="order"),
    # url(r'^address$', login_required(views.AddressView.as_view()), name="address"),


    url(r'^info$', views.InfoView.as_view(), name="info"),
    url(r'^order/(?P<page>\d+)$', views.OrderView.as_view(), name="order"),
    url(r'^address$', views.AddressView.as_view(), name="address"),

    url(r'^show$', views.show, name='show'),
    url(r'^get_all_province$', views.get_all_province, name='get_all_province'),
    url(r'^get_city_by_pid$', views.get_city_by_pid, name='get_city_by_pid'),
    url(r'^get_area_by_cid$', views.get_area_by_cid, name='get_area_by_cid'),
]
