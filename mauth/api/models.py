from django.db import models
from django.utils import timezone



class PhoneNumber(models.Model):
    number = models.CharField(max_length=10,unique=True)
    iccid = models.CharField(max_length=6,unique=True,null=False)
    firstName = models.CharField(max_length=20,default="")
    lastName = models.CharField(max_length=20,default="")
    nationalId = models.CharField(max_length=8,unique=True,default="")
    statement = models.CharField(max_length=50,default="")
    answer = models.CharField(max_length=50,default="")

class User(models.Model):     
    password = models.CharField(max_length=20)
    incorrectPasswordTrials = models.CharField(max_length=4,default="4")
    phoneNumber = models.OneToOneField(PhoneNumber,on_delete=models.CASCADE)  
    email = models.CharField(max_length=50,default="NONE")
    secondaryPhoneNumber = models.CharField(max_length=15,default="NONE")
    avatar = models.CharField(default="NONE",max_length=1000)
    otp = models.CharField(default="_",max_length=6)
    iccid = models.CharField(max_length=6,default="NONE")
    average_transaction = models.CharField(max_length=10000000,default="20000")
    balance = models.CharField(max_length=100000000,default="20000")
    currentDevice = models.CharField(max_length=10000000,default="")



class Tower(models.Model):
    name = models.CharField(max_length=20,blank=True,null=True)
    state = models.CharField(max_length=20,blank=True,null=True)
    
class Transactions(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    amount = models.CharField(max_length=100,blank=True,null=True)
    type = models.CharField(max_length=20,blank=True,null=True)
    time = models.CharField(max_length=100,default=timezone.now())
    _from = models.CharField(max_length=100,default="")
    to = models.CharField(max_length=100,default="")
    
