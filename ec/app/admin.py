from django.contrib import admin
from .models import product, Customer, Cart, Payment, OrderPlaced, Wishlist
from django.utils.html import format_html
from django.urls import reverse
from django.contrib.auth.models import Group
# Register your models here.

@admin.register(product)
class ProductModelAdmin(admin.ModelAdmin):
       list_display = [
        'id', 'title', 'main_category', 'sub_category', 'discounted_price', 'product_image'
    ]
    
@admin.register(Customer)
class CustomerModelAdmin(admin.ModelAdmin):
    list_display = ['id', 'users', 'locality', 'city', 'zipcode']
    def users(self, obj):
        if hasattr(obj, 'user') and obj.user:  # Ensure the user exists
            link = reverse("admin:auth_user_change", args=[obj.user.pk])  # Adjust app_label and model_name if needed
            return format_html('<a href="{}">{}</a>', link, obj.user.username)  # Use a valid field like username or email
        return "No user"

    users.short_description = "User"

@admin.register(Cart)
class CartModelAdmin(admin.ModelAdmin):
    list_display = ['id', 'users', 'products', 'quantity'] 
    def users(self, obj):
        if hasattr(obj, 'user') and obj.user:  # Ensure the user exists
            link = reverse("admin:auth_user_change", args=[obj.user.pk])  # Adjust app_label and model_name if needed
            return format_html('<a href="{}">{}</a>', link, obj.user.username)  # Use a valid field like username or email
        return "No user"

    users.short_description = "User"
         
@admin.register(Payment)
class PaymentModelAdmin(admin.ModelAdmin):
    list_display = ['id', 'users', 'amount', 'razorpay_order_id', 'razorpay_payment_status', 'razorpay_payment_id', 'paid']
    def users(self, obj):
        if hasattr(obj, 'user') and obj.user:  # Ensure the user exists
            link = reverse("admin:auth_user_change", args=[obj.user.pk])  # Adjust app_label and model_name if needed
            return format_html('<a href="{}">{}</a>', link, obj.user.username)  # Use a valid field like username or email
        return "No user"

    users.short_description = "User"
     
@admin.register(OrderPlaced)
class OrderPlacedModelAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'customers', 'products', 'ordered_date', 'status', 'payments']

    def customers(self, obj):
          link = reverse("admin:app_customer_change", args=[obj.customer.pk])
          return format_html('<a href="{}">{}</a>', link, obj.customer.name)
    
    def products(self, obj):
          link = reverse("admin:app_product_change", args=[obj.product.pk])
          return format_html('<a href="{}">{}</a>', link, obj.product.title)

    def payments(self, obj):
          link = reverse("admin:app_payment_change", args=[obj.payment.pk])
          return format_html('<a href="{}">{}</a>', link, obj.payment.razorpay_payment_id)
    
@admin.register(Wishlist)
class WishlistModelAdmin(admin.ModelAdmin):
     list_display = ['id', 'users', 'products']

     def users(self, obj):
        if hasattr(obj, 'user') and obj.user:  # Ensure the user exists
            link = reverse("admin:auth_user_change", args=[obj.user.pk])  # Adjust app_label and model_name if needed
            return format_html('<a href="{}">{}</a>', link, obj.user.username)  # Use a valid field like username or email
        return "No user"

     users.short_description = "User"
     
     def products(self, obj):
          link = reverse("admin:app_product_change", args=[obj.product.pk])
          return format_html('<a href="{}">{}</a>', link, obj.product.title)

admin.site.unregister(Group)