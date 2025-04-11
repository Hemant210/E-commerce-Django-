import json
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
from django.shortcuts import get_object_or_404
from .models import OrderPlaced
from django.conf import settings 
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib import messages
from django.http import HttpResponseBadRequest, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View
from django.contrib.auth.views import LogoutView
import razorpay
from .models import Cart, Customer, OrderPlaced, Payment, Wishlist, product  
from django.contrib.auth.forms import PasswordResetForm
from django.urls import reverse_lazy
from . forms import CustomerProfileForm, CustomerRegistrationForm
from django.db.models import Q
from .models import product, MAIN_CATEGORIES, SUBCATEGORY_CHOICES, SUBCATEGORY_MAP


def hello(request):
    totalitem = 0
    wishitem = 0
    if request.user.is_authenticated:
        totalitem = len(Cart.objects.filter(user=request.user))
        wishitem = len(Wishlist.objects.filter(user=request.user))
    return render(request, 'app/home.html',locals())

def about(request):
    totalitem = 0
    wishitem = 0
    if request.user.is_authenticated:
        totalitem = len(Cart.objects.filter(user=request.user))
        wishitem = len(Wishlist.objects.filter(user=request.user))
    return render(request, 'app/about.html',locals())

def contact(request):
    totalitem = 0
    wishitem = 0
    if request.user.is_authenticated:
        totalitem = len(Cart.objects.filter(user=request.user))
        wishitem = len(Wishlist.objects.filter(user=request.user))
        return render(request, 'app/contact.html',locals())

class CategoryView(View):
    def get(self, request, val):
        from .models import product, Cart, Wishlist
        from .models import SUBCATEGORY_CHOICES, MAIN_CATEGORIES, SUBCATEGORY_MAP

        MAIN_DICT = dict(MAIN_CATEGORIES)
        SUB_DICT = dict(SUBCATEGORY_CHOICES)

        # First assume it's a subcategory
        products = product.objects.filter(sub_category=val)
        category_label = SUB_DICT.get(val)
        main_category_code = None

        if not products.exists():
            # Try as main category instead
            products = product.objects.filter(main_category=val)
            category_label = MAIN_DICT.get(val)
            main_category_code = val
        else:
            # If it's subcategory, find its parent main category
            for key, sub_list in SUBCATEGORY_MAP.items():
                if any(code == val for code, _ in sub_list):
                    subcategories = sub_list
                    main_category_code = key
                    break

        # Fallback to show relevant subcategories
        subcategories = SUBCATEGORY_MAP.get(main_category_code, [])

        totalitem = Cart.objects.filter(user=request.user).count() if request.user.is_authenticated else 0
        wishitem = Wishlist.objects.filter(user=request.user).count() if request.user.is_authenticated else 0

        return render(request, "app/category.html", {
            "products": products,
            "category_name": category_label,
            "subcategories": subcategories,
            "main_category_code": main_category_code,
            "totalitem": totalitem,
            "wishitem": wishitem
        })

# class CategoryView(View):
#     def get(self, request, val):
#         from .models import product, Cart, Wishlist
#         from .models import SUBCATEGORY_CHOICES, MAIN_CATEGORIES, SUBCATEGORY_MAP

#         MAIN_DICT = dict(MAIN_CATEGORIES)
#         SUB_DICT = dict(SUBCATEGORY_CHOICES)

#         # Try matching subcategory first
#         products = product.objects.filter(sub_category=val)
#         category_label = SUB_DICT.get(val)

#         if not products.exists():
#             # Then try as main_category
#             products = product.objects.filter(main_category=val)
#             category_label = MAIN_DICT.get(val)

#         # Fallback label
#         if not category_label:
#             category_label = "Category"

#         # Get corresponding subcategories
#         subcategories = SUBCATEGORY_MAP.get(val, [])
#         if not subcategories:
#             # If viewing sub_category, find its main category
#             for key, sub_list in SUBCATEGORY_MAP.items():
#                 for code, name in sub_list:
#                     if code == val:
#                         subcategories = sub_list
#                         break

#         totalitem = Cart.objects.filter(user=request.user).count() if request.user.is_authenticated else 0
#         wishitem = Wishlist.objects.filter(user=request.user).count() if request.user.is_authenticated else 0

#         return render(request, "app/category.html", {
#             "products": products,
#             "category_name": category_label,
#             "subcategories": subcategories,
#             "totalitem": totalitem,
#             "wishitem": wishitem
#         })

class CategoryTitle(View):
    def get(self, request, val):
        products = product.objects.filter(title=val)
        title = product.objects.filter(main_category=products[0].main_category).values('title')
        totalitem = 0
        wishitem = 0
        if request.user.is_authenticated:
           totalitem = len(Cart.objects.filter(user=request.user))
           wishitem = len(Wishlist.objects.filter(user=request.user))
    
        return render(request, "app/category.html", locals())
        
class ProductDetail(View):
    def get(self, request, pk):
        products = product.objects.get(pk=pk)

        wishlist = None  # or [] if you plan to loop in template

        # ✅ check if user is logged in before querying
        if request.user.is_authenticated:
            wishlist = Wishlist.objects.filter(Q(product=products) & Q(user=request.user)).exists()

        totalitem = Cart.objects.filter(user=request.user).count() if request.user.is_authenticated else 0
        wishitem = Wishlist.objects.filter(user=request.user).count() if request.user.is_authenticated else 0

        return render(request, "app/productdetails.html", {
            'products': products,
            'wishlist': wishlist,
            'totalitem': totalitem,
            'wishitem': wishitem
        })

class CustomerRegistrationView(View):
    def get(self, request):
        form = CustomerRegistrationForm()
        return render(request, "app/customerregistration.html", {'form': form})

    def post(self, request):
        form = CustomerRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Congratulations! User registered successfully.")
            return redirect('customerregistration') 
        else:
            messages.error(request, "Failed to register user, please correct the errors below.")
            return render(request, "app/customerregistration.html", {'form': form})

class ProfilevView(View):
    def get(self, request):
        totalitem = 0
        wishitem = 0
        if request.user.is_authenticated:
           totalitem = len(Cart.objects.filter(user=request.user))
           wishitem = len(Wishlist.objects.filter(user=request.user))
        form = CustomerProfileForm()
        return render(request, "app/profile.html", {'form': form})

    def post(self, request):
        form = CustomerProfileForm(request.POST)
        totalitem = 0
        wishitem = 0
        if request.user.is_authenticated:
           totalitem = len(Cart.objects.filter(user=request.user))
           wishitem = len(Wishlist.objects.filter(user=request.user))
        if form.is_valid():
            user = request.user
            name = form.cleaned_data['name']
            locality = form.cleaned_data['locality']
            city = form.cleaned_data['city']
            mobile = form.cleaned_data['mobile']
            zipcode = form.cleaned_data['zipcode']

            customer, created = Customer.objects.update_or_create(
                user=user,
                defaults={
                    'name': name,
                    'locality': locality,
                    'city': city,
                    'mobile': mobile,
                    'zipcode': zipcode,
                }
            )

            if created:
                messages.success(request, "Congratulations! Profile data inserted successfully.")
            else:
                messages.success(request, "Profile data updated successfully.")
        else:
            messages.error(request, "Failed to save profile data, please correct the errors below.")
        
        return render(request, "app/profile.html", {'form': form})

@login_required
def address(request):
    totalitem = 0
    wishitem = 0
    if request.user.is_authenticated:
           totalitem = len(Cart.objects.filter(user=request.user))
           wishitem = len(Wishlist.objects.filter(user=request.user))
       
    addresses = Customer.objects.filter(user=request.user) 
    return render(request, "app/address.html", {'add': addresses}) 


class UpdateAddress(View):
    def get(self, request, pk):
        totalitem = 0
        wishitem = 0
        if request.user.is_authenticated:
            totalitem = len(Cart.objects.filter(user=request.user))
            wishitem = len(Wishlist.objects.filter(user=request.user))
        try:
            add = Customer.objects.get(pk=pk)
            form = CustomerProfileForm(instance=add)
            return render(request, "app/updateAddress.html", {'form': form, 'address': add})
        except Customer.DoesNotExist:
            messages.error(request, "Address not found.")
            return redirect('address')

    def post(self, request, pk):
        try:
            add = Customer.objects.get(pk=pk)
            form = CustomerProfileForm(request.POST, instance=add)
            
            if form.is_valid():
                form.save()  # Save the updated address
                messages.success(request, "Address updated successfully.")
                return redirect('address')
            else:
                messages.error(request, "Failed to update address. Please correct the errors below.")
                return render(request, 'app/updateAddress.html', {'form': form, 'address': add})
        except Customer.DoesNotExist:
            messages.error(request, "Address not found.")
            return redirect('address')

class CustomLogoutView(LogoutView):
    def get(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)

    next_page = reverse_lazy('login')

def add_to_cart(request):
    totalitem = 0
    wishitem = 0
    if request.user.is_authenticated:
           totalitem = len(Cart.objects.filter(user=request.user))
           wishitem = len(Wishlist.objects.filter(user=request.user))
    if request.method == 'POST':
        user = request.user
        product_id = request.POST.get('product_id')

        if product_id:
            try:
                product_instance = get_object_or_404(product, id=product_id)
                Cart.objects.create(user=user, products=product_instance)
                messages.success(request, "Product added to cart successfully!")
                return redirect('showcart')
            except Exception as e:
                messages.error(request, f"An error occurred: {e}")
                return redirect('/')
        else:
            messages.error(request, "Invalid or missing product ID.")
            return redirect('/')
    return redirect('/')

@login_required
def show_cart(request):
    totalitem = 0
    wishitem = 0
    if request.user.is_authenticated:
           totalitem = len(Cart.objects.filter(user=request.user))
           wishitem = len(Wishlist.objects.filter(user=request.user))
       
    user=request.user
    cart = Cart.objects.filter(user=user)
    amount = 0
    for p in cart:
        value = p.quantity * p.products.discounted_price
        amount = amount + value
    totalamount = amount + 40
    
    return render(request, 'app/addtocart.html', locals())

class checkout(View):
    def get(self,request):
     totalitem = 0
     wishitem = 0
     if request.user.is_authenticated:
           totalitem = len(Cart.objects.filter(user=request.user))
           wishitem = len(Wishlist.objects.filter(user=request.user))
       
     user=request.user
     add=Customer.objects.filter(user=user)
     cart_items=Cart.objects.filter(user=user)
     famount = 0
     for p in cart_items:
          value = p.quantity * p.products.discounted_price
          famount = famount + value
     totalamount = famount + 40
     razoramount = int(totalamount * 100)
     client = razorpay.Client(auth=(settings.RAZOR_KEY_ID, settings.RAZOR_KEY_SECRET))
     data = { "amount":razoramount, "currency":"INR","receipt":"Order_rcptid_12"}
     payment_response = client.order.create(data=data)
     print(payment_response)
     order_id = payment_response['id']
     order_status = payment_response['status']
     if order_status == 'created':
         payment= Payment(
             user=user,
             amount=totalamount,
             razorpay_order_id =order_id,
             razorpay_payment_status = order_status
         )
         payment.save()
     return render(request, 'app/checkout.html', locals())

@login_required
def payment_done(request):
    order_id = request.GET.get('order_id')
    payment_id = request.GET.get('payment_id')
    cust_id = request.GET.get('cust_id')

    print(f"Received parameters: order_id={order_id}, payment_id={payment_id}, cust_id={cust_id}")

    if not (order_id and payment_id and cust_id):
        return HttpResponseBadRequest("Missing order_id, payment_id, or cust_id.")

    try:
        cust_id = int(cust_id)
    except ValueError:
        return HttpResponseBadRequest("Invalid customer ID format. Expected a number.")

    try:
        user = request.user
        if not user.is_authenticated:
            return HttpResponseBadRequest("User not authenticated.")

        print(f"Fetching Customer with ID: {cust_id}")
        customer = Customer.objects.get(id=cust_id)

        print(f"Fetching Payment with order ID: {order_id}")
        payment = Payment.objects.get(razorpay_order_id=order_id)

        payment.paid = True
        payment.razorpay_payment_id = payment_id
        payment.save()

        cart = Cart.objects.filter(user=user)
        for c in cart:
            print(f"Placing order for product {c.products}")
            OrderPlaced(user=user, customer=customer, product=c.products, quantity=c.quantity, payment=payment).save()
            c.delete()

        return redirect("orders")
    except Customer.DoesNotExist:
        return HttpResponseBadRequest("Invalid customer ID. Customer does not exist.")
    except Payment.DoesNotExist:
        return HttpResponseBadRequest("Invalid order ID. Payment record does not exist.")
    except Exception as e:
        return HttpResponseBadRequest(f"An error occurred: {str(e)}")

def orders(request):
    totalitem = 0
    wishitem = 0
    if request.user.is_authenticated:
           totalitem = len(Cart.objects.filter(user=request.user))
           wishitem = len(Wishlist.objects.filter(user=request.user))
    order_placed=OrderPlaced.objects.filter(user=request.user)
    return render(request, 'app/orders.html',locals())

@login_required
def plus_cart(request):
    if request.method == "GET":
        prod_id = request.GET.get('prod_id')

        # Get cart item for this product and user
        cart_item = Cart.objects.filter(products__id=prod_id, user=request.user).first()
        if not cart_item:
            return JsonResponse({'error': 'Cart item not found'}, status=404)

        cart_item.quantity += 1
        cart_item.save()

        cart = Cart.objects.filter(user=request.user)
        amount = sum(item.quantity * item.products.discounted_price for item in cart)
        totalamount = amount + 40  # fixed shipping

        return JsonResponse({
            'quantity': cart_item.quantity,
            'amount': amount,
            'totalamount': totalamount
        })

@login_required
def minus_cart(request):
    if request.method == "GET":
        prod_id = request.GET.get('prod_id')
        cart_item = Cart.objects.filter(products__id=prod_id, user=request.user).first()

        if not cart_item:
            return JsonResponse({'error': 'Cart item not found'}, status=404)

        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            cart_item.save()
        else:
            cart_item.delete()

        cart = Cart.objects.filter(user=request.user)
        amount = sum(item.quantity * item.products.discounted_price for item in cart)
        totalamount = amount + 40

        return JsonResponse({
            'quantity': cart_item.quantity if cart_item.quantity > 0 else 0,
            'amount': amount,
            'totalamount': totalamount
        })

@login_required
def remove_cart(request):
    if request.method == "GET":
        prod_id = request.GET.get('prod_id')
        cart_item = Cart.objects.filter(products__id=prod_id, user=request.user).first()

        if not cart_item:
            return JsonResponse({'error': 'Cart item not found'}, status=404)

        cart_item.delete()

        cart = Cart.objects.filter(user=request.user)
        amount = sum(item.quantity * item.products.discounted_price for item in cart)
        totalamount = amount + 40

        return JsonResponse({
            'amount': amount,
            'totalamount': totalamount,
            'message': 'Item removed from cart successfully'
        })

@login_required
def plus_wishlist(request):
    prod_id = request.GET.get('prod_id')

    if not prod_id:
        return HttpResponseBadRequest("Product ID is missing.")

    try:
        products = get_object_or_404(product, id=prod_id)
        user = request.user

        # Prevent duplicate wishlist entries
        Wishlist.objects.get_or_create(user=user, product=products)

        return JsonResponse({'message': 'Wishlist added successfully'})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@login_required
def minus_wishlist(request):
    prod_id = request.GET.get('prod_id')

    if not prod_id:
        return HttpResponseBadRequest("Product ID is missing.")

    try:
        products = get_object_or_404(product, id=prod_id)
        user = request.user
        Wishlist.objects.filter(user=user, product=products).delete()

        return JsonResponse({'message': 'Wishlist removed successfully'})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@login_required
def generate_invoice(request, order_id):
    # Fetch order details, or return 404 if not found
    order = get_object_or_404(OrderPlaced, id=order_id)

    # Define the context for the template
    context = {
        "order": order,
        "user": order.user,
        "customers": order.customer,
        "products": order.products if isinstance(order.product, list) else [order.product],  # Ensure list format
        "ordered_date": order.ordered_date,
        "razorpay_order_id": order.payment.razorpay_order_id,
        "razorpay_payment_id": order.payment.razorpay_payment_id,
        "razorpay_payment_status": order.payment.razorpay_payment_status,
        "amount": order.total_cost,
    }

    # Load and render the template
    try:
        template = get_template("app/invoice_template.html")
        html = template.render(context)
    except Exception as e:
        return HttpResponse(f"Template Error: {e}", status=500)

    # Create a PDF response
    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = f'inline; filename="invoice_{order_id}.pdf"'

    # Generate PDF
    pisa_status = pisa.CreatePDF(html, dest=response)

    # Check for errors
    if pisa_status.err:
        return HttpResponse("Error generating PDF", status=500)

    return response


def search(request):
    query = request.GET.get('search', '')  # Safely get the search query
    totalitem = 0
    wishitem = 0

    if request.user.is_authenticated:
        totalitem = Cart.objects.filter(user=request.user).count()
        wishitem = Wishlist.objects.filter(user=request.user).count()

    # Filter products based on the search query
    products = product.objects.filter(Q(title__icontains=query)) if query else []

    context = {
        'products': products,
        'query': query,
        'totalitem': totalitem,
        'wishitem': wishitem,
    }

    return render(request, 'app/search.html', context)