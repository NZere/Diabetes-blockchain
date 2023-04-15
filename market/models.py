import datetime
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.conf import settings


class Product(models.Model):
    CHOICE_TYPE = (
        ('0', 'food'),
        ('1', 'medicine'),
        ('2', 'other')
    )

    name_product = models.CharField(max_length=100)
    count = models.IntegerField(default=0)
    price = models.FloatField(default=0)
    type = models.IntegerField(default=2, choices=CHOICE_TYPE)
    prom = models.FloatField(default=0)
    date = models.DateTimeField(default=timezone.now)
    image = models.ImageField(upload_to="media/product_images", blank=True)
    slug = models.SlugField(default=name_product)

    def __str__(self):
        return self.name_product

    def is_prom_0(self):
        if self.prom == 0:
            return True
        else:
            return False

    def price_with_prom(self):
        price = self.price-self.price / 100 * self.prom
        return price

    def get_absolute_url(self):
        return reverse("market:product", kwargs={
            'slug': self.slug
        })

    def get_add_to_cart_url(self):
        return reverse("market:add-to-cart", kwargs={
            'slug': self.slug
        })

    def get_product(self):
        return reverse("market:product", kwargs={
            'slug': self.slug
        })

    def leave_comment(self):
        return reverse("market:comment", kwargs={
            'slug': self.slug
        })

    def get_remove_from_cart_url(self):
        return reverse("market:remove-from-cart", kwargs={
            'slug': self.slug
        })

    def was_published_recently(self):
        return self.date >= (timezone.now() - datetime.timedelta(days=14))


class CartItem(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    is_ordered = models.BooleanField(default=False)

    def get_total_item_price(self):
        return self.quantity * self.product.price

    def get_total_discount_item_price(self):
        return self.quantity * self.product.price_with_prom()

    def get_amount_saved(self):
        return self.get_total_item_price() - self.get_total_discount_item_price()

    def get_final_price(self):
        return self.get_total_discount_item_price()

    def __unicode__(self):
        return "Cart item for product " + self.product.name_product


class Cart(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, default=1)
    items = models.ManyToManyField(CartItem)
    start_date = models.DateTimeField(auto_now_add=True)  # auto_now_add=True,
    ordered_date = models.DateTimeField()
    is_ordered = models.BooleanField(default=False)

    def get_total(self):
        total = 0
        for order_item in self.items.all():
            a = order_item.product.price - (order_item.product.prom / 100 * order_item.product.price)
            b = order_item.quantity * a
            total += b
        return total


class Commentary(models.Model):
    user_name = models.CharField('Author', max_length=100)
    text = models.TextField('Text')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    def get_add_to_cart_url(self):
        return reverse("main:comment", kwargs={
            'slug': self.product.slug
        })


