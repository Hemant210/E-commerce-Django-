from django.db import models
from django.contrib.auth.models import User

MAIN_CATEGORIES = [
    ('DA', 'Dairy'),
    ('EL', 'Electronics'),
    ('GR', 'Groceries'),
    ('WF', "Women's Fashion"),
    ('MF', "Men's Fashion"),
    ('FT', "Footwear"),
    ('BK', "Books"),
]

SUBCATEGORY_CHOICES = [
    ('ML', 'Milk'), ('LS', 'Lassi'), ('GH', 'Ghee'), ('CR', 'Curd'),
    ('PN', 'Paneer'), ('CZ', 'Cheese'), ('IC', 'Ice-cream'), ('CH', 'Chocolate'), ('MS', 'Milkshake'),
    ('MB', 'Mobile'), ('TV', 'TV'), ('LP', 'Laptop'),
    ('FR', 'Fruits'), ('VG', 'Vegetables'), ('GRI', 'Grains'), ('SP', 'Spices'),
    ('WSR', 'Sarees'), ('WDR', 'Dresses'), ('WJE', 'Jeans'),
    ('MSH', 'Shirts'), ('MTS', 'T-Shirts'), ('MTR', 'Trousers'),
    ('MSL', "Men's Slippers"), ('WSN', "Women's Sneakers"),
    ('FIC', 'Fiction'), ('NFC', 'Non-fiction'), ('EDU', 'Educational'), ('COM', 'Comics'), ('BIO', 'Biographies'),
]

SUBCATEGORY_MAP = {
    'DA': [('ML', 'Milk'), ('LS', 'Lassi'), ('GH', 'Ghee'), ('CR', 'Curd'),
           ('PN', 'Paneer'), ('CZ', 'Cheese'), ('IC', 'Ice-cream'), ('CH', 'Chocolate'), ('MS', 'Milkshake')],
    'EL': [('MB', 'Mobile'), ('TV', 'TV'), ('LP', 'Laptop')],
    'GR': [('FR', 'Fruits'), ('VG', 'Vegetables'), ('GRI', 'Grains'), ('SP', 'Spices')],
    'WF': [('WSR', 'Sarees'), ('WDR', 'Dresses'), ('WJE', 'Jeans')],
    'MF': [('MSH', 'Shirts'), ('MTS', 'T-Shirts'), ('MTR', 'Trousers')],
    'FT': [('MSL', "Men's Slippers"), ('WSN', "Women's Sneakers")],
    'BK': [('FIC', 'Fiction'), ('NFC', 'Non-fiction'), ('EDU', 'Educational'), ('COM', 'Comics'), ('BIO', 'Biographies')],
}

class product(models.Model):
    title = models.CharField(max_length=100)
    selling_price = models.FloatField()
    discounted_price = models.FloatField()
    description = models.TextField()
    composition = models.TextField(default='', blank=True)
    prodapp = models.TextField(default='', blank=True)
    main_category = models.CharField(choices=MAIN_CATEGORIES, max_length=3, default='DA')
    sub_category = models.CharField(choices=SUBCATEGORY_CHOICES, max_length=4, default='ML')
    brand = models.CharField(max_length=100, default='', blank=True)
    product_image = models.ImageField(upload_to='product')

    def __str__(self):
        return self.title

class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    locality = models.CharField(max_length=200)
    city = models.CharField(max_length=200)
    mobile = models.CharField(max_length=10)  # Use CharField for length restriction
    zipcode = models.CharField(max_length=10)

    def __str__(self):
        return self.name
    
class Cart(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    products = models.ForeignKey(product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    @property
    def total_cost(self):
        return self.quantity * self.product.discounted_price
    
STATUS_CHOICES = (
    ('Accepted','Accepted'),
    ('Packed','Packed'),
    ('On The-way','On The-way'),
    ('Delivered','Delivered'),
    ('Cancel','Cancel'),
    ('Pending','Pending'),
)

class Payment(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    amount = models.FloatField()
    razorpay_order_id = models.CharField(max_length=100,blank=True,null=True)
    razorpay_payment_status =models.CharField(max_length=100,blank=True,null=True)
    razorpay_payment_id = models.CharField(max_length=100,blank=True,null=True)
    paid = models.BooleanField(default=False)

class OrderPlaced(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    product = models.ForeignKey(product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    ordered_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=50,choices=STATUS_CHOICES, default='Pending')
    payment = models.ForeignKey(Payment,on_delete=models.CASCADE,default="")
    @property
    def total_cost(self):
        return self.quantity * self.product.discounted_price

class Wishlist(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    product = models.ForeignKey(product, on_delete=models.CASCADE)