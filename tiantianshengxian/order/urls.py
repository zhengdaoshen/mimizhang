from django.conf.urls import include, url
from django.contrib import admin
from order import views
from  django.contrib.auth.decorators import login_required

urlpatterns = [

    url(r'^place$', views.OrderPlaceView.as_view(), name="place"),
    url(r'^commit$', views.OrderCommitView.as_view(), name="commit"),

]
