from django.contrib import admin

# Register your models here.
from django.contrib import admin


from django.contrib import admin
from .models import Order, OrderItem

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "email", "mobile", "total_price", "created_at")
    inlines = [OrderItemInline]

