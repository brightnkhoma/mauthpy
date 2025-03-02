from django.contrib import admin
from .models import User,PhoneNumber,Transactions

admin.site.register(User)
admin.site.register(PhoneNumber)
admin.site.register(Transactions)

# Register your models here.
