from django.db import models

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
    
    def __str__(self):
        return f"{self.client.name} : {self.value} - {self.date}"

class Teacher(models.Model):
    name = models.CharField(max_length=200)
    dept = models.FloatField(default=0)
    def __str__(self):
        return f"{self.name}"

class Lesson(models.Model):
    teacher = models.ForeignKey(Teacher,on_delete=models.CASCADE)
    name = models.CharField(max_length=200,default = "")
    clients = models.ManyToManyField(Client)
    date = models.DateField()
    price = models.FloatField(default=0)

    def __str__(self):
        return f"{self.name} - {self.teacher} : {len(self.clients.all())} учеников - {self.date} - {self.price}"

class Phone(models.Model):
    note = models.CharField(max_length=200)
    client = models.ForeignKey(Client,on_delete=models.CASCADE)
    phone = models.BigIntegerField()
    def __str__(self):
        return f"{self.client}:{self.phone}-{self.note}"
