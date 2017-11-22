from django.contrib import admin

from .models import CityDict, CourseOrg, Teacher


class CityDictAdmin(admin.ModelAdmin):
    list_display = ['name', 'desc']


class CourseOrgAdmin(admin.ModelAdmin):
    list_display = ['name','category', 'city']
    list_filter = ['name', 'city', 'category','add_time']
    search_fields = ['name', 'city', 'add_time']


class TeacherAdmin(admin.ModelAdmin):
    list_display = ['name', 'org', 'click_nums']
    list_filter = ['name', 'org','work_company', 'click_nums']
    search_fields = ['name', 'org', 'click_nums']

admin.site.register(CityDict, CityDictAdmin)
admin.site.register(CourseOrg, CourseOrgAdmin)
admin.site.register(Teacher, TeacherAdmin)