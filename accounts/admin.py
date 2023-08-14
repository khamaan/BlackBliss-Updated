from django.contrib import admin
from .models import Account, UserProfile,NewsletterSubscriber
# Register your models here.
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['id','user']
class NewsletterSubscriberAdmin(admin.ModelAdmin):
    list_display = ['id','user','subscription_date']
admin.site.register(UserProfile, UserProfileAdmin)  
admin.site.register(Account)
admin.site.register(NewsletterSubscriber, NewsletterSubscriberAdmin)