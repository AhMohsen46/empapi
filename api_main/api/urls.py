from django.conf.urls import url
from . import views
urlpatterns = [
    url(r'^newemp/$', views.new_employee, name='post-create'),
    url(r'^editbonus/$',views.update_bonus),
    url(r'^getdata/$',views.getreport),
    url(r'^delete/$',views.delete_employee),
    url(r'^empdetails/$',views.empdetails)

]
