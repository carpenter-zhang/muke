from django.contrib import admin

from .models import UserProfile, EmailVerifyRecode, Banner


class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['id', 'nick_name', 'gender', 'mobile']
    list_filter = ['id', 'nick_name', 'gender', 'mobile']
    search_fields = ['id', 'nick_name', 'gender', 'mobile']


class EmailVerifyRecodeAdmin(admin.ModelAdmin):
    list_display = ['email', 'send_type', 'send_time']
    list_filter = ['email', 'send_type', 'send_time']
    search_fields = ['email', 'send_type', 'send_time']


class BannerAdmin(admin.ModelAdmin):
    list_display = ['title', 'index']
    list_filter = ['title', 'index']
    search_fields = ['title', 'index']


admin.site.register(UserProfile, UserProfileAdmin)
admin.site.register(EmailVerifyRecode, EmailVerifyRecodeAdmin)
admin.site.register(Banner, BannerAdmin)