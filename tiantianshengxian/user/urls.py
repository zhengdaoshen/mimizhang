from django.conf.urls import include, url
from django.contrib import admin
from user import views
from  django.contrib.auth.decorators import login_required

urlpatterns = [
    url(r"^$", views.index, name='index'),
    url(r"^register$", views.RegisterView.as_view(), name='register'),
    url(r"^login$", views.LoginView.as_view(), name='login'),
    url(r"^active/(?P<token>.*)$", views.ActiveView.as_view(), name='active'),
    url(r'^validate_code$', views.validate_code, name="validate_code"),
    url(r'^checkusername', views.checkusername, name="checkusername"),

    # url(r'^info$', login_required(views.InfoView.as_view()), name="info"),
    # url(r'^order$', login_required(views.OrderView.as_view()), name="order"),
    # url(r'^address$', login_required(views.AddressView.as_view()), name="address"),


    url(r'^info$', views.InfoView.as_view(), name="info"),
    url(r'^order$', views.OrderView.as_view(), name="order"),
    url(r'^address$', views.AddressView.as_view(), name="address"),
]

