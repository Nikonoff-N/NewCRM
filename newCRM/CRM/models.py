from django.db import models

def getDefaultTeacher():
    return Teacher.objects.all()[0].pk
def getDefaultGroup():
    return Group.objects.all()[0].pk

# Create your models here.
class Client(models.Model):
    name = models.CharField(max_length=200)
    money = models.FloatField(default=0)
    active = models.BooleanField(default=True)
    def __str__(self):
        return self.name

class Payment(models.Model):
    client = models.ForeignKey(Client,on_delete=models.CASCADE)
    date = models.DateField()
    value = models.FloatField(default=0)
    note = models.CharField(max_length=200,default="")
    def __str__(self):
        return f"{self.client.name} : {self.value} - {self.date} {self.note}"

class Teacher(models.Model):
    name = models.CharField(max_length=200)
    dept = models.FloatField(default=0)
    def __str__(self):
        return f"{self.name}"



class Phone(models.Model):
    note = models.CharField(max_length=200)
    client = models.ForeignKey(Client,on_delete=models.CASCADE)
    phone = models.BigIntegerField()
    def __str__(self):
        return f"{self.client}:{self.phone}-{self.note}"

class Group(models.Model):
    name = models.CharField(max_length=200)
    clients = models.ManyToManyField(Client)
    schedule = models.CharField(max_length=200)
    teacher = models.ForeignKey(Teacher,on_delete=models.PROTECT,default=getDefaultTeacher)
    archive = models.BooleanField(default= False)
    def __str__(self):
        return f"{self.name} : {len(self.clients.all())} учеников"

class Lesson(models.Model):
    teacher = models.ForeignKey(Teacher,on_delete=models.CASCADE)
    name = models.CharField(max_length=200,default = "")
    clients = models.ManyToManyField(Client)
    date = models.DateField()
    price = models.FloatField(default=0)
    group = models.ForeignKey(Group,on_delete=models.PROTECT,default=getDefaultGroup)
    def __str__(self):
        return f"{self.name} - {self.teacher} : {len(self.clients.all())} учеников - {self.date} - {self.price}"

class Salary(models.Model):
    teacher = models.ForeignKey(Teacher,on_delete=models.PROTECT,default=getDefaultTeacher)
    date = models.DateField()
    value = models.FloatField(default=0)
    note = models.CharField(max_length=200,default="")
    def __str__(self):
        return f"{self.teacher.name} : {self.value} - {self.date} {self.note}"