# generic
from rest_framework import generics, mixins

from api_main.models import Employee
from django.core import serializers

from .serializers import EmployeeSerializer
from django.views.decorators.csrf import csrf_exempt

from django.http import HttpResponse
from django.db.models import Sum
from apscheduler.schedulers.blocking import BlockingScheduler
import requests
import datetime
import calendar
import json

def get_days_of_month(year):
    return [calendar.monthrange(year,month)[1] for month in range(1,13)]

def get_week_date(year, month, day):
    return datetime.date(year, month, day).weekday()

def get_salary_day(year,month):
    days = get_days_of_month(year)
    last_day_of_month = days[month-1]
    last_day = get_week_date(year, month, last_day_of_month)
    if last_day in [4,5]:
        return last_day_of_month - (last_day - 3)
    else:
        return last_day_of_month


def get_bonus_day(year,month):
    bonus_day = 15
    last_day = get_week_date(year, month, bonus_day)
    if last_day in [4,5]:
        return bonus_day + (6 - last_day)
    else:
        return bonus_day

def getreport(request):
    if request.method=="GET":
        year = datetime.datetime.now().year
        data = ""
        for month in range(datetime.datetime.now().month,13):
            month_name = calendar.month_abbr[month]
            total_sal = Employee.objects.aggregate(Sum('salary'))['salary__sum']
            bonus_total = 0
            for emp in Employee.objects.values_list():
                bonus_total += emp[1]*emp[2]/100
            total_paid = total_sal+bonus_total
            salaries_day = get_salary_day(year,month)
            bonus_day = get_bonus_day(year,month)
            data += """"%s":{"Salaries_payment_day": %s,"Bonus_payment_day": %s,"Salaries_total": "$%s","Bonus_total": "$%s","Payments_total": "$%s"},"""%(month_name,salaries_day,bonus_day,int(total_sal),int(bonus_total),int(total_paid))
        #print(json.loads("""{
         #                   %s
          #                  }"""%(data[:-1].strip())))
        return HttpResponse("""{
                            %s
                            }"""%(data[:-1].strip()))
    else:
        return HttpResponse(status = 405)

@csrf_exempt 
def empdetails(request):
    if request.method=="POST":
        request_data= json.loads(request.body)
        emp_id= request_data.get("emp_id")
        if Employee.objects.filter(emp_id = emp_id).all():
            x = serializers.serialize("json", Employee.objects.filter(emp_id = emp_id).all())
            x = json.loads(x)   
            x = json.dumps(x[0]['fields'])     
            return HttpResponse(x)
        else:
            return HttpResponse("Employee id not available")
    else:
        return HttpResponse(status = 405)


@csrf_exempt 
def update_bonus(request):
    if request.method == "POST":
        request_data= json.loads(request.body)
        emp_id= request_data.get("emp_id")
        bonus= request_data.get("new_bonus")
        if Employee.objects.filter(emp_id = emp_id):
            old_bonus = Employee.objects.filter(emp_id = emp_id).values('bonus').get()['bonus']
            Employee.objects.filter(emp_id = emp_id).update(bonus = bonus)
            return HttpResponse("employee %s bonus was changed from %s to %s"%(emp_id,old_bonus,float(bonus)))
        else:
            return HttpResponse("No Employee with id %s"%(emp_id))

    else:
        return HttpResponse(status = 405)

@csrf_exempt 
def new_employee(request):
    
    if request.method == "POST":
        request_data= json.loads(request.body)
        emp_id= request_data.get("emp_id")
        salary = request_data.get("salary")
        bonus= request_data.get("bonus")
    
        if Employee.objects.filter(emp_id = emp_id):
            return HttpResponse("this id was used before")

        else:
            q = Employee(emp_id = emp_id, salary = salary, bonus = bonus)
            q.save()
            return HttpResponse("new employee added was added successfully with id:%s, salary:%s, bonus:%s"%(emp_id,salary,bonus))
    else:
        return HttpResponse(status = 405)

@csrf_exempt 
def delete_employee(request):

    if request.method == "POST":
        request_data= json.loads(request.body)
        print(request_data)
        emp_id = request_data.get("emp_id")

        if Employee.objects.filter(emp_id = emp_id):
            Employee.objects.filter(emp_id = emp_id).delete()
            print('emp deleted')
            return HttpResponse("Employee deleted")
        else:
            return HttpResponse("Employee id not available")
    else:
        return HttpResponse(status = 405)

        
class EmployeeRudview(generics.RetrieveUpdateDestroyAPIView): #detailView

    lookup_field = 'emp_id'
    # queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer

    def get_queryset(self):
        return Employee.objects.all()

    def get_object(self):
        emp_id = self.kwargs.get("emp_id")
        return Employee.objects.get(emp_id = emp_id)