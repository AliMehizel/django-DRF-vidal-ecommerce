from django.db import models
from django.contrib.auth.models import User

product_category = [
    ('WOMEN','WOMEN'),
    ('MEN','MEN'),
    ('JEWELERY','JEWELERY'),
    ('KIDS','KIDS')
]

product_color = [
    ('WHITE','WHITE'),
    ('BLACK','BLACK'),
    ('GRAY','GRAY'),
]

product_size = [
    ('T-SHIRT',(
		('S','S'),
        ('M','M'),
        ('L','L'),
        ('XL','XL'),
        ('2XL','2XL'),
        ('3XL','3XL')
	)),
    ('SHOES',(
		('EU 39','EU 39'),
        ('EU 40','EU 40'),
        ('EU 41','EU 41'),
        ('EU 42','EU 42'),
        ('EU 43','EU 43'),
        ('EU 44','EU 44')
	))
]





class Product(models.Model):
    name = models.CharField(max_length=200)
    description = models.CharField(max_length=600)
    category = models.CharField(choices=product_category,default='WOMEN', max_length=50)
    price = models.DecimalField(max_digits=7, decimal_places=2)
    digital = models.BooleanField(default=False,null=True, blank=True)
    image = models.ImageField(upload_to='images',null=True, blank=True)
    
    
    def __str__(self):
        return self.name

    @property #get image by using url
    def imageURL(self):
        try:
            url = self.image.url
        except:
            url = ''
        return url

class Oreder(models.Model):
	customer = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
	date_ordred = models.DateTimeField(auto_now_add=True)
	paypal_oreder_id = models.CharField(max_length=80, null=True)
	stripe_oreder_id = models.CharField(max_length=200, null=True)
	total = models.FloatField(max_length=300,null=True)
	complete = models.BooleanField(default=False)


	def __str__(self):
		return str(self.id)


  		
	@property
	def shipping(self):
		shipping = False
		orderitems = self.orederitem_set.all()
		for i in orderitems:
			if i.product.digital == False:
				shipping = True
		return shipping

		
	@property #get the total of all products in oreder
	def get_cart_total(self):
		orderitems = self.orederitem_set.all()
		total = sum([item.get_total for item in orderitems])

		return total 

	@property #get all quatity
	def get_cart_items(self):
		orderitems = self.orederitem_set.all()
		total = sum([item.quantity for item in orderitems])
        
		return total 

class OrederItem(models.Model):
	product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
	oreder = models.ForeignKey(Oreder, on_delete=models.SET_NULL, null=True)
	quantity = models.IntegerField(default=1, null=True, blank=True)
	size = models.CharField(choices=product_size,max_length=50,default='S')
	color = models.CharField(choices=product_color,max_length=50,default='WHITE')
	date_added = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return str(self.id)

	@property #get the total of each item in list individually
	def get_total(self):
		total = self.product.price * self.quantity
		return total

class ShippingAddress(models.Model):
	customer = models.ForeignKey(User,  on_delete=models.SET_NULL, null=True)
	oreder = models.ForeignKey(Oreder, on_delete=models.SET_NULL, null=True)
	address = models.CharField(max_length=200, null=False)
	city = models.CharField(max_length=200, null=False)
	state = models.CharField(max_length=200, null=False)
	zipcode = models.CharField(max_length=200, null=False)
	phone = models.CharField(max_length=200, null=False)
	date_added = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return self.address