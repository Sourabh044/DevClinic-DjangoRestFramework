from django.contrib import admin
from .models import *
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
# Register your models here.

class UserAdmin(BaseUserAdmin):
    # The forms to add and change user instances
    # The fields to be used in displaying the User model.
    # These override the definitions on the base UserAdmin
    # that reference specific fields on auth.User.
    list_display = ('email', 'name', 'is_admin','is_verified')
    list_filter = ('is_admin','is_verified')
    readonly_fields=('updated_at',)
    fieldsets = (
        (None, {'fields': ('email', 'password','updated_at')}),
        ('Personal info', {'fields': ('name',)}),
        ('Permissions', {'fields': ('is_admin','is_verified')}),
    )
    # add_fieldsets is not a standard ModelAdmin attribute. UserAdmin
    # overrides get_fieldsets to use this attribute when creating a user.
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'name', 'password'),
        }),
    )
    search_fields = ('email',)
    ordering = ('email',)
    filter_horizontal = ()


# Now register the new UserAdmin...
admin.site.register(User, UserAdmin)



# overriding the User class to make the password field readonly
# class UserAdmin(admin.ModelAdmin):
#         readonly_fields = ('password',)
admin.site.register(Patient)
admin.site.register(Appointment)