from django.conf.urls import url
from .views import EmployeeRudview, EmployeeAPIview
urlpatterns = [
    url(r'^newemp/(?P<emp_id>\d+)/(?P<salary>\d+)/(?P<bonus>\d+)/$', EmployeeAPIview.new_employee, name='post-create'),
    url(r'^editbonus/(?P<emp_id>\d+)/(?P<bonus>\d+)/$',EmployeeAPIview.update_bonus),
    url(r'^getdata$',EmployeeAPIview.get_dates),
    url(r'^delete/(?P<emp_id>\d+)/$',EmployeeAPIview.delete_employee)

]
