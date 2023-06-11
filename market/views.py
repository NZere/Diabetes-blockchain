import json

from django.db.models import Q
from django.utils import timezone
from django.db import transaction
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404, HttpResponseRedirect, JsonResponse, HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.views import View
from django.views.generic import DetailView

from market.models import Product, CartItem, Cart, Coupon
from users.models import Wallet
from users.views import get_user_first_name, get_user_money, encrypt, get_user_email, get_user_last_name

from django.contrib import messages

from django.contrib.auth.models import User

from django.forms.models import model_to_dict


def index(request):
    user_money = None
    if request.user.is_authenticated:
        user_money = get_user_money(request.user)

    new_products = [
        Product.objects.get(id=10),
        Product.objects.get(id=11),
        Product.objects.get(id=12),
        Product.objects.get(id=13),
    ]

    return render(request, 'shop.html', {"user_money": user_money, "new_products": new_products})


def product(request, slug):
    user_first_name = email = user_money = None
    if request.user.is_authenticated:
        user_first_name = get_user_first_name(request.user)
        email = get_user_email(request.user)
        user_money = get_user_money(request.user)
    products = Product.objects.get(slug=slug)
    comments = products.commentary_set.order_by('-id')[:10]
    new_products = [
        Product.objects.get(id=10),
        Product.objects.get(id=11),
        Product.objects.get(id=12),
        Product.objects.get(id=13),
    ]
    context = {
        "object": products,
        "comments": comments,
        "user_first_name": user_first_name,
        "email": email,
        "comments_count": comments.count(),
        "user_money": user_money,
        "new_products": new_products
    }

    return render(request, 'productSingle.html', context)


CHOICE_TYPE = {
    0: 'food',
    1: 'medicine',
    2: 'device',
    3: 'other'
}
CHOICE_PRICE = {
        "0-1K": (0, 1000),
        "1K-10K": (1000, 10000),
        "10K-50K": (10000, 50000),
        "50K+": (50000, 99999999),
        "50K ": (50000, 99999999),
    }


def get_all_products(request):
    user_money = None
    if request.user.is_authenticated:
        user_money = get_user_money(request.user)
    types = request.GET.getlist('type')
    sorting = request.GET.get('sorting')
    prices = request.GET.getlist('price')

    # print(types)
    products = Product.objects.all()

    match sorting:
        case 'asc':
            print('asc')
            products = products.order_by('price')
        case 'dsc':
            print('dsc')
            products = products.order_by('-price')
        case 'new':
            print('new')
            products = products.order_by('date')
        case 'asc-name':
            print('asc')
            products = products.order_by('name_product')
        case 'dsc-name':
            print('dsc')
            products = products.order_by('-name_product')

    pr = []
    print(prices)
    # for price in prices:
    #     pass
    filter_query = Q()
    if prices:
        for price in prices:

            min_price, max_price = CHOICE_PRICE[price]

            if max_price is None:
                filter_query |= Q(price__gte=min_price)
            else:
                filter_query |= Q(price__gte=min_price, price__lt=max_price)

    print("filter_query", filter_query)
    products = products.filter(filter_query)

    if not types:
        for pro in products:
            # print(type)
            pr.append(
                pro
            )
            print("all ", pr)
        return render(request, "products.html", {"pr": pr, "user_money": user_money})
    for pro in products:
        if CHOICE_TYPE[pro.type] in types:
            print("pro.type", pro.type)
            pr.append(
                pro
            )

    print("after filter ", pr)
    return render(request, "products.html", {"pr": pr, "user_money": user_money})


def get_all_products_filter(request):
    user_money = None
    if request.user.is_authenticated:
        user_money = get_user_money(request.user)
    type = request.GET.get('type')
    print(type)
    CHOICE_TYPE = {
        0: 'food',
        1: 'medicine',
        2: 'device',
        3: 'other'
    }
    products = Product.objects.all()
    pr = []
    for pro in products:
        print("------------------")
        print(pro.type)
        print(CHOICE_TYPE[pro.type])
        print(type)
        print("------------------")
        if CHOICE_TYPE[pro.type] == type:
            pr.append(
                pro
            )
    print(pr)
    # data = {
    #     'products': pr,
    #     'products': pr,
    #
    # }
    return render(request, "products.html", {"pr": pr, "user_money": user_money})


@login_required
def add_to_cart(request, slug):
    product_to_add = get_object_or_404(Product, slug=slug)
    order_item, created = CartItem.objects.get_or_create(
        product=product_to_add,
        user=request.user,
        is_ordered=False
    )
    order_qs = Cart.objects.filter(user=request.user, is_ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        # check if the order item is in the order
        if order.items.filter(product__slug=product_to_add.slug).exists():
            order_item.quantity += 1
            order_item.save()
            messages.info(request, "This item quantity was updated.")
            return redirect("market:order-summary")
        else:
            order.items.add(order_item)
            messages.info(request, "This item was added to your cart.")
            return redirect("market:order-summary")
    else:
        ordered_date = timezone.now()
        order = Cart.objects.create(
            user=request.user, ordered_date=ordered_date)
        order.items.add(order_item)
        messages.info(request, "This item was added to your cart.")
        return redirect("market:order-summary")


@login_required
def remove_from_cart(request, slug):
    item = get_object_or_404(Product, slug=slug)
    order_qs = Cart.objects.filter(
        user=request.user,
        is_ordered=False
    )
    if order_qs.exists():
        order = order_qs[0]
        # check if the order item is in the order
        if order.items.filter(product__slug=item.slug).exists():
            try:
                order_item = CartItem.objects.filter(
                    product=item,
                    user=request.user,
                    is_ordered=False
                ).first()

                order.items.remove(order_item)
                order.save()
                messages.info(request, "This item was removed from your cart.")
                return redirect("market:order-summary")
            except Exception as e:
                print("error", e)
        else:
            messages.info(request, "This item was not in your cart")
            return redirect("market:order-summary", slug=slug)
    else:
        messages.info(request, "You do not have an active order")
        return redirect("market:order-summary", slug=slug)


@login_required
def remove_single_item_from_cart(request, slug):
    product_to_remove = get_object_or_404(Product, slug=slug)
    order_qs = Cart.objects.filter(
        user=request.user,
        is_ordered=False
    )
    if order_qs.exists():
        order = order_qs[0]
        # check if the order item is in the order
        if order.items.filter(product__slug=product_to_remove.slug).exists():
            order_item = CartItem.objects.filter(
                product=product_to_remove,
                user=request.user,
                is_ordered=False
            )[0]
            if order_item.quantity > 1:
                order_item.quantity -= 1
                order_item.save()
            else:
                order.items.remove(order_item)
            messages.info(request, "This item quantity was updated.")
            return redirect("market:order-summary")
        else:
            messages.info(request, "This item was not in your cart")
            return redirect("market:order-summary", slug=slug)
    else:
        messages.info(request, "You do not have an active order")
        return redirect("market:order-summary", slug=slug)


@login_required
def comment(request, slug):
    try:
        product = Product.objects.get(slug=slug)
    except():
        raise Http404("ERROORRRRRR")
    if request.method == 'POST':
        comment = request.POST['comment']
        product.commentary_set.create(user_name=request.user, text=comment, product_id=product.id)
    return HttpResponseRedirect(reverse('market:product', args=(product.slug,)))


class OrderSummaryView(View):
    def get(self, *args, **kwargs):
        try:
            if not self.request.user.is_authenticated:
                raise ObjectDoesNotExist
            user_first_name = get_user_first_name(self.request.user)
            user_money = get_user_money(self.request.user)

            order = Cart.objects.get(user=self.request.user, is_ordered=False)
            context = {
                'object': order,
                'DISPLAY_COUPON_FORM': True,
                'user_first_name': user_first_name,
                'user_money': user_money
            }
            return render(self.request, 'shoppingCart.html', context)
        except ObjectDoesNotExist:
            messages.warning(self.request, "You do not have an active order")
            print("You do not have an active order")
            return redirect("/market")


class PaymentView(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        user_first_name = user_money = None
        if self.request.user.is_authenticated:
            user_first_name = get_user_first_name(self.request.user)
            user_money = get_user_money(self.request.user)

        try:
            order = Cart.objects.get(user_id=self.request.user.id, is_ordered=False)
            order_items = order.items.all()
            user = None
            if self.request.user.is_authenticated:
                user = self.request.user
            print(user.id)
            user_wallet = Wallet.get_purse_by_userid(user.id)
            purchase = 0
            main_admin = User.objects.get(id=1)
            main_admin_wallet = Wallet.get_purse_by_userid(1)

            with transaction.atomic():
                if user:
                    with transaction.atomic():
                        money = get_user_money(user)
                        if money >= order.get_total():
                            with transaction.atomic():
                                for order_item in order_items:
                                    money = money - order_item.get_final_price()
                                    print('order_item.get_final_price()', order_item.get_final_price())
                                    money_enc = (encrypt(user.id, str(money), user.username)).decode('ascii')
                                    user_wallet.money = money_enc
                                    user_wallet.save()
                            with transaction.atomic():
                                for order_item in order_items:
                                    purchase += order_item.get_final_price()
                                    main_admin_wallet.money = (
                                        encrypt(main_admin.id, str(main_admin_wallet.money), main_admin.username)). \
                                        decode('ascii')
                                    main_admin_wallet.save()
                        else:
                            error_message = 'Not enough money !!'
                            messages.warning(self.request, error_message)
                            return redirect("/market", {'user_first_name': user_first_name, 'user_money': user_money})
            messages.success(self.request, "Your order was successful!")
            return redirect("/market",
                            {'user_first_name': user_first_name, 'market': purchase, 'user_money': user_money})
        except():
            messages.warning(self.request, "Error")
            return redirect("/", {'user_first_name': user_first_name, 'user_money': user_money})


class AddCouponView(View):
    def post(self, request, *args, **kwargs):
        if request.method == "POST":
            try:
                code = request.POST.get('code', '')
                order = Cart.objects.get(
                    user=self.request.user, is_ordered=False)
                coupon = get_coupon(self.request, code)
                if not coupon:
                    return redirect("market:order-summary")
                order.coupon = coupon
                order.save()
                messages.success(self.request, "Successfully added coupon")
                return redirect("market:order-summary")
            except ObjectDoesNotExist:
                messages.info(self.request, "You do not have an active order")
                return redirect("market:order-summary")


def get_coupon(request, code):
    try:
        coupon = Coupon.objects.get(code=code)
        return coupon
    except ObjectDoesNotExist:
        messages.info(request, "This coupon does not exist")
        return None


class ItemDetailViewP(DetailView):
    model = Product
    template_name = "market/product.html"

# class WalletView(LoginRequiredMixin, View):
#     def get(self, request):
#         user_first_name = None
#         user_email = None
#         user_last_name = None
#         if self.request.user.is_authenticated:
#             user_first_name = get_user_first_name(self.request.user)
#
#         user = None
#         if request.user.is_authenticated:
#             user = request.user
#             user_email = get_user_email(user)
#             user_last_name = get_user_last_name(user)
#         purse = Wallet.get_purse_by_userid(user.id)
#
#         orders = Cart.objects.filter(user_id=user.id)
#         data = {'user': user, 'purse': purse, 'money': get_user_money(user), 'user_first_name': user_first_name,
#                 'user_last_name': user_last_name, 'user_email': user_email}
#
#         if not User.objects.filter(user=1).exists():
#             data['orders'] = orders
#         print('email', user_email)
#         return render(request, 'market/account.html', data)
