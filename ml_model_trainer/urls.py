from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.MLModelView.as_view()),
    url(r'^(?P<model_id>[0-9]+)/experiment/$',views.ExperimentView.as_view()),
    url(r'^(?P<model_id>[0-9]+)/image/$',views.UploadImageView.as_view()),
    url(r'^(?P<model_id>[0-9]+)/test/$',views.TestView.as_view())
]
