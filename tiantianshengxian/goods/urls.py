from django.conf.urls import include, url
from django.contrib import admin
from goods import views
from  django.contrib.auth.decorators import login_required
from goods.views import IndexView

urlpatterns = [

    url(r'^index$', views.IndexView.as_view(), name="index"),

]
