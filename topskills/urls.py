from django.conf.urls import url
from . import views

urlpatterns = [
	url(r'^$', views.index),
	url(r'^results/$', views.results),
	url(r'^dictionary/add/$', views.dictionaryAdd),
	url(r'^dictionary/delete/$', views.dictionaryDelete),
	url(r'^dictionary/$', views.dictionary)
]