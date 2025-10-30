from django.contrib import admin
from project.models import UserInfo, Category

@admin.register(UserInfo)
class UserInfoAdminPage(admin.ModelAdmin):
    list_display= ('id',"user",'phone', 'profile', 'address')
    search_fields= ('user__username', 'phone', 'address')

@admin.register(Category)
class CategoryAdminPage(admin.ModelAdmin):
    list_display= ('id', "name", "slug")
    search_fields = ("name",)