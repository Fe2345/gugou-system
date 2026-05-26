from django.contrib import admin

from .models import Address, Division


@admin.register(Division)
class DivisionAdmin(admin.ModelAdmin):
    list_display = ["code", "name", "level", "parent_code"]
    list_filter = ["level"]
    search_fields = ["name", "code"]

    @admin.display(description="上级 code")
    def parent_code(self, obj):
        return obj.parent.code if obj.parent else "-"


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ["user", "receiver_name", "receiver_phone", "detail", "is_default"]
    list_filter = ["is_default"]
