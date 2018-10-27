from django.conf.urls import include, url
from django.contrib import admin
from cart import views
from  django.contrib.auth.decorators import login_required

urlpatterns = [

    url(r'^add$', views.CartView.as_view(), name="add"),
    url(r'^count$', views.CartCountView.as_view(), name="count"),
    url(r'^info$', views.CartInfoView.as_view(), name="info"),
    url(r'^update$', views.CartUpdateView.as_view(), name="update"),
    url(r'^delete$', views.CartDeleteView.as_view(), name="delete"),

]
