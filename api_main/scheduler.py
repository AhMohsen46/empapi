import logging

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.executors.pool import ProcessPoolExecutor, ThreadPoolExecutor
from django_apscheduler.jobstores import register_events, register_job
from api_main.models import Employee
from django.conf import settings
from django.db.models import Sum


# Create scheduler to run in a thread inside the application process
scheduler = BackgroundScheduler(settings.SCHEDULER_CONFIG)
from apscheduler.schedulers.background import BackgroundScheduler
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
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

def scheduling_emails():
    global fromaddr,toaddr,password,sched
    current_month = datetime.datetime.now().month
    current_year = datetime.datetime.now().year
    salary_day = get_salary_day(current_year,current_month)-2
    bonus_day = get_bonus_day(current_year,current_month)-2
    sched.add_job(sending_email,'cron',[fromaddr,toaddr,password,"salary"],month = str(current_month), day = str(salary_day), hour = '12',minute = '0', second=0)
    sched.add_job(sending_email,'cron',[fromaddr,toaddr,password,"bonus"],month = str(current_month), day = str(bonus_day), hour = '12',minute = '0', second=0)

def sending_email(fromaddr, toaddr, password,pay_type):
    month_name = calendar.month_abbr[datetime.datetime.now().month]
    total_sal = Employee.objects.aggregate(Sum('salary'))['salary__sum']
    bonus_total = 0
    for emp in Employee.objects.values_list():
        bonus_total += emp[1]*emp[2]/100

    fromaddr = fromaddr
    toaddr = toaddr
    body = "%s Payment remember for month %s"%(pay_type,month_name)
    if pay_type == 'bonus':
        body += "with amount %s"%(bonus_total)
    else:
        body += "with amount %s"%(total_sal)
    msg = MIMEMultipart()
    
    msg['From'] = fromaddr
    msg['To'] = toaddr
    msg['Subject'] = "Payment remember"
    
    msg.attach(MIMEText(body, 'plain'))
     
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(fromaddr, password)
    text = msg.as_string()
    server.sendmail(fromaddr, toaddr, text)
    server.quit()


def start():
    if settings.DEBUG:
      	# Hook into the apscheduler logger
        logging.basicConfig()
        logging.getLogger('apscheduler').setLevel(logging.DEBUG)
    sched.add_job(scheduling_emails, 'cron', month='*', day='1', hour='1', minute='0', second=0)

    sched.start()


sched = BackgroundScheduler()
fromaddr = "" #user email address
toaddr = "" #receiver "to whom we report" email address
password = "" #user email password
