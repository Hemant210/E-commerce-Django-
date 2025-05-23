import json
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
from django.utils.decorators import method_decorator
from django.shortcuts import get_object_or_404
from .models import OrderPlaced
from django.conf import settings 
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib import messages
from django.http import HttpResponseBadRequest, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View
from django.core.mail import send_mail
from django.contrib.auth.views import LogoutView
import razorpay
from .models import Cart, Customer, OrderPlaced, Payment, Wishlist, product  
from django.contrib.auth.forms import PasswordResetForm
from django.urls import reverse_lazy
from . forms import CustomerProfileForm, CustomerRegistrationForm
from django.db.models import Q
import pandas as pd
from prophet import Prophet
from django.shortcuts import render
from .models import OrderPlaced 
import plotly.express as px
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.pyplot as plt
import io
import base64
import plotly.graph_objects as go
from .models import UserActivity, UserRecommendation  
from .models import product, MAIN_CATEGORIES, SUBCATEGORY_CHOICES, SUBCATEGORY_MAP

def hello(request):
    totalitem = 0
    wishitem = 0
    recommendations = []
    recent_views = []

    if request.user.is_authenticated:
        totalitem = Cart.objects.filter(user=request.user).count()
        wishitem = Wishlist.objects.filter(user=request.user).count()
        recommendations = generate_recommendations(request.user.id)
        recent_views = get_recently_viewed_products(request.user.id)

    return render(request, 'app/home.html', {
        'totalitem': totalitem,
        'wishitem': wishitem,
        'recommendations': recommendations,
        'recent_views': recent_views
    })

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

@login_required
@method_decorator(login_required, name='dispatch')
class checkout(View):
    def get(self, request):
        user = request.user
        add = Customer.objects.filter(user=user)
        cart_items = Cart.objects.filter(user=user)
        totalitem = Cart.objects.filter(user=user).count()
        wishitem = Wishlist.objects.filter(user=user).count()

        famount = sum(p.quantity * p.products.discounted_price for p in cart_items)
        totalamount = famount + 40
        razoramount = int(totalamount * 100)

        # Razorpay order create
        client = razorpay.Client(auth=(settings.RAZOR_KEY_ID, settings.RAZOR_KEY_SECRET))
        data = {"amount": razoramount, "currency": "INR", "receipt": "order_rcptid_11"}
        payment_response = client.order.create(data=data)

        order_id = payment_response['id']
        order_status = payment_response['status']

        if order_status == 'created':
            Payment.objects.create(
                user=user,
                amount=totalamount,
                razorpay_order_id=order_id,
                razorpay_payment_status=order_status
            )

        return render(request, 'app/checkout.html', {
            'add': add,
            'cart_items': cart_items,
            'totalamount': totalamount,
            'razoramount': razoramount,
            'order_id': order_id,
            'totalitem': totalitem,
            'wishitem': wishitem
        })

    def post(self, request):
        # This method won't do anything since Razorpay handles payment via JS
        return HttpResponse(status=204)


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
    if request.user.is_authenticated:
        totalitem = Cart.objects.filter(user=request.user).count()
        wishitem = Wishlist.objects.filter(user=request.user).count()

    if request.method == 'POST':
        user = request.user
        product_id = request.POST.get('product_id')
        action = request.POST.get('action')  # 'add' or 'buy'

        if product_id:
            try:
                product_instance = get_object_or_404(product, id=product_id)

                cart_item, created = Cart.objects.get_or_create(user=user, products=product_instance)
                if not created:
                    cart_item.quantity += 1
                    cart_item.save()

                if action == 'buy':
                    messages.success(request, "Product added to cart successfully!")
                    return redirect('showcart')  # Go to cart for checkout
                else:
                    return redirect('product-detail', pk=product_id)

            except Exception as e:
                messages.error(request, f"An error occurred: {e}")
                return redirect('product-detail', pk=product_id)

        messages.error(request, "Invalid or missing product ID.")
        return redirect(request.META.get("HTTP_REFERER", "/"))

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

@login_required
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

# 1. Collect Daily Sales Data
def get_daily_sales_data():
    orders = OrderPlaced.objects.filter(status='Delivered')
    data = []

    for order in orders:
        if order.total_cost:
            data.append({
                'date': order.ordered_date.date(),
                'total_price': order.total_cost
            })

    if not data:
        return None

    df = pd.DataFrame(data)
    df = df.groupby('date')['total_price'].sum().reset_index()
    df.columns = ['ds', 'y']
    df['ds'] = pd.to_datetime(df['ds'])
    df = df.dropna(subset=['y'])

    return df if not df.empty else None

# 2. Forecast Function 
def forecast_daily_sales(sales_df):
    if sales_df is None or sales_df.empty or len(sales_df) < 2:
        return None

    model = Prophet()
    model.fit(sales_df)

    future = model.make_future_dataframe(periods=14)
    forecast = model.predict(future)

    return forecast

# 3. Plot Conversion Helper
def convert_plot_to_base64():
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    image_png = buffer.getvalue()
    graphic = base64.b64encode(image_png).decode('utf-8')
    buffer.close()
    plt.close()
    return graphic

# 4. Generate Forecast Plots
def create_plot(forecast, actual_df):
    plots = {}

    # Forecast Plot
    plt.figure(figsize=(10, 5))
    plt.plot(forecast['ds'], forecast['yhat'], label='Predicted Sales', color='blue')
    plt.title("🔮 Forecasted Daily Sales")
    plt.xlabel('Date')
    plt.ylabel('Sales (₹)')
    plt.legend()
    plt.tight_layout()
    plots['forecast'] = convert_plot_to_base64()

    # Confidence Interval Plot
    plt.figure(figsize=(10, 5))
    plt.plot(forecast['ds'], forecast['yhat'], label='Prediction', color='blue')
    plt.fill_between(forecast['ds'], forecast['yhat_lower'], forecast['yhat_upper'], alpha=0.3, color='skyblue')
    plt.title("📉 Sales Confidence Interval (Next 14 Days)")
    plt.xlabel('Date')
    plt.ylabel('Sales Range (₹)')
    plt.legend()
    plt.tight_layout()
    plots['confidence'] = convert_plot_to_base64()

    # Actual vs Predicted Plot
    merged = pd.merge(actual_df, forecast, on='ds', how='inner')
    merged = merged.tail(7)

    plt.figure(figsize=(10, 5))
    plt.bar(merged['ds'], merged['y'], label='Actual', color='green', alpha=0.6)
    plt.plot(merged['ds'], merged['yhat'], label='Predicted', color='red', marker='o')
    plt.title("📊 Actual vs Predicted Sales (Last 7 Days)")
    plt.xlabel('Date')
    plt.ylabel('Sales (₹)')
    plt.legend()
    plt.tight_layout()
    plots['comparison'] = convert_plot_to_base64()

    return plots

# 5. Main Dashboard View
def daily_sales_dashboard(request):
    actual_sales_df = get_daily_sales_data()
    if actual_sales_df is None:
        return render(request, 'app/sales_dashboard.html', {'message': 'Not enough data to forecast.'})

    forecast = forecast_daily_sales(actual_sales_df)
    if forecast is None:
        return render(request, 'app/sales_dashboard.html', {'message': 'Forecasting failed due to insufficient data.'})

    plots = create_plot(forecast, actual_sales_df)

    return render(request, 'app/sales_dashboard.html', {
        'plot_forecast': plots['forecast'],
        'plot_confidence': plots['confidence'],
        'plot_comparison': plots['comparison'],
    })

# 6. CSV Download View
def download_forecast_csv(request):
    actual_sales_df = get_daily_sales_data()
    forecast = forecast_daily_sales(actual_sales_df)

    if forecast is None:
        return HttpResponse("No forecast data available.", content_type="text/plain")

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="sales_forecast.csv"'
    forecast.to_csv(path_or_buf=response, index=False)
    return response

# 7. AJAX JSON Endpoint for Chart.js or Live Polling
def forecast_json_api(request):
    actual_sales_df = get_daily_sales_data()
    forecast = forecast_daily_sales(actual_sales_df)

    if forecast is None:
        return JsonResponse({'status': 'error', 'message': 'Not enough data.'})

    forecast_data = forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].tail(14).to_dict('records')
    return JsonResponse({'status': 'ok', 'data': forecast_data})

#Viewd product data
def get_recently_viewed_products(user_id, limit=3):
    recent_views = (
        UserActivity.objects.filter(user_id=user_id)
        .order_by('-viewed_on')
        .values_list('product', flat=True)
        .distinct()
    )
    return product.objects.filter(id__in=recent_views)[:limit]

def generate_recommendations(user_id, limit=6):
    viewed_products = UserActivity.objects.filter(user_id=user_id).values_list('product', flat=True)
    recommendations = product.objects.exclude(id__in=viewed_products).order_by('?')[:limit]
    
    rec_obj, created = UserRecommendation.objects.get_or_create(user_id=user_id)
    rec_obj.recommended_products.set(recommendations)
    rec_obj.save()
    return recommendations

def chatbot(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        user_message = data.get('message', '')
        # Basic mock reply
        bot_reply = f"You said: {user_message}"
        return JsonResponse({'response': bot_reply})

# def run_stock_forecast_alert():
    data = OrderPlaced.objects.values('product_id', 'ordered_date', 'quantity')
    
    if not data:
        return "No historical data to forecast."

    df = pd.DataFrame(data)
    df['ordered_date'] = pd.to_datetime(df['ordered_date'])

    df = df.groupby(['product_id', 'ordered_date']).agg({'quantity': 'sum'}).reset_index()
    forecasts = {}
    alerts = []

    for pid in df['product_id'].unique():
        sub_df = df[df['product_id'] == pid][['ordered_date', 'quantity']].rename(columns={'ordered_date': 'ds', 'quantity': 'y'})

        if len(sub_df) < 2:
            continue  # Skip if not enough data to forecast

        model = Prophet()
        model.fit(sub_df)

        future = model.make_future_dataframe(periods=7)
        forecast = model.predict(future)
        forecasts[pid] = forecast

        predicted_demand = forecast['yhat'][-7:].sum()

        try:
            prod = product.objects.get(id=pid)
            if prod.stock < predicted_demand:
                alerts.append(f"[ML Alert] '{prod.title}' might go out of stock soon.\nStock: {prod.stock} | Predicted Demand: {int(predicted_demand)}")
        except product.DoesNotExist:
            continue

    if alerts:
        message = "\n\n".join(alerts)

        superusers = User.objects.filter(is_superuser=True)
        for admin in superusers:
            send_mail(
                subject='🧠 ML Stock Alert - Patil Mart',
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[admin.email],
                fail_silently=True,
            )
        return f"Sent alerts to {superusers.count()} admin(s)."
    return "All stocks are fine."