from django.contrib import admin
from .models import *
 



admin.site.register(User)
admin.site.register(Company)
admin.site.register(Permission)
admin.site.register(Subscription)
admin.site.register(Subscribers)
