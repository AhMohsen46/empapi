from rest_framework import serializers

from api_main.models import Employee

class EmployeeSerializer(serializers.ModelSerializer): #forms.ModelForm
    class Meta:
        model = Employee
        fields = [
        'emp_id',
        'salary',
        'bonus',
        ]
    def validate_id(self, value):
        qs = Employee.objects.filter(title__iexact = value)
        if self.instance:
            qs = qs,exclude(id=self.instance.id)
        if qs.exists():
            raise serializers.ValidationError("this id has been used before")
