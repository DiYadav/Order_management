from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Customer



@admin.register(Customer)
class CustomerAdmin(UserAdmin):
    model=Customer
    list_display=(
        "id","email","first_name","last_name","is_staff","is_active",
    )
    ordering=("id",)
    search_fields=("email", "first_name", "last_name")
    fieldsets=((None, {"fields":("email", "password")}),
               ("Personal Information",{
                   "fields":("first_name","last_name","phone_number")
               }),
                       ("Permissions", {
            "fields": (
                "is_active",
                "is_staff",
                "is_superuser",
                "groups",
                "user_permissions",
            )
        }),
        ("Important Dates", {
            "fields": ("last_login", "date_joined")
        }),
    )
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("email", "password1", "password2"),
        }),
    )
    filter_horizontal = ("groups", "user_permissions"
               )
