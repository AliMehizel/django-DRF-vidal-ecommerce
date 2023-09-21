from django.contrib import admin
from .models import *
# Register your models here.



admin.site.register(Product)
admin.site.register(Oreder)
admin.site.register(OrederItem)
admin.site.register(ShippingAddress)