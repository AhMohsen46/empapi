# generic
from rest_framework import generics, mixins

from api_main.models import Employee

from .serializers import EmployeeSerializer

from django.http import HttpResponse
from django.db.models import Sum
from apscheduler.schedulers.blocking import BlockingScheduler

import datetime
import calendar

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
class EmployeeRudview(generics.RetrieveUpdateDestroyAPIView): #detailView

    lookup_field = 'emp_id'
    # queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer

    def get_queryset(self):
        return Employee.objects.all()

    def get_object(self):
        emp_id = self.kwargs.get("emp_id")
        return Employee.objects.get(emp_id = emp_id)

class EmployeeAPIview(generics.CreateAPIView): #detailView

    lookup_field = 'emp_id'
    serializer_class = EmployeeSerializer
    def new_employee(self,emp_id,salary,bonus):
        if Employee.objects.filter(emp_id = emp_id):
            return HttpResponse("this id was used before")

        else:
            q = Employee(emp_id = emp_id, salary = salary, bonus = bonus)
            q.save()

            return HttpResponse("new employee added with id:%s, salary:%s, bonus:%s"%(emp_id,salary,bonus))

    def update_bonus(self,emp_id,bonus):
        if Employee.objects.filter(emp_id = emp_id):
            old_bonus = Employee.objects.filter(emp_id = emp_id).values('bonus').get()['bonus']
            Employee.objects.filter(emp_id = emp_id).update(bonus = bonus)
            return HttpResponse("employee %s bonus was changed from %s to %s"%(emp_id,old_bonus,float(bonus)))
        else:
            return HttpResponse("No Employee with id %s"%(emp_id))

    def get_dates(self):
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
            data += """{
            Month: %s,
            Salaries_payment_day: %s,
            Bonus_payment_day: %s,
            Salaries_total: $%s,
            Bonus_total: $%s,
            Payments_total: $%s
            },
            """%(month_name,salaries_day,bonus_day,int(total_sal),int(bonus_total),int(total_paid))

        return HttpResponse("""{
        %s
        }"""%(data))

    def delete_employee(self,emp_id):
        if Employee.objects.filter(emp_id = emp_id):
            Employee.objects.filter(emp_id = emp_id).delete()
            return HttpResponse("Employee deleted")

        else:
            return HttpResponse("Employee data not available")

    def perform_create(self, serializer):
        serializer.save()
