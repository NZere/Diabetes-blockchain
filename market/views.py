from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.views import View

from market.models import Product
from users.views import get_user_first_name


def product(request, slug):
    user_first_name = None
    if request.user.is_authenticated:
        user_first_name = get_user_first_name(request.user)
    products = Product.objects.get(slug=slug)
    comments = products.commentary_set.order_by('-id')[:10]
    context = {
        "object": products,
        "comments": comments,
        "user_first_name": user_first_name
    }
    return render(request, 'market/product.html', context)


@login_required
def add_to_cart(request, slug):
    product = get_object_or_404(Clothes, slug=slug)
    order_item, created = CartItemP.objects.get_or_create(
        product=product,
        user=request.user,
        ordered=False,
        shop=product.shop
    )
    order_qs = CartP.objects.filter(user=request.user, ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        # check if the order item is in the order
        if order.items.filter(product__slug=product.slug).exists():
            order_item.quantity += 1
            order_item.save()
            messages.info(request, "This item quantity was updated.")
            messages.info(request, "This item quantity was updated.")
            return redirect("clothesL:order-summary")
        else:
            order.items.add(order_item)
            messages.info(request, "This item was added to your cart.")
            return redirect("clothesL:order-summary")
    else:
        ordered_date = timezone.now()
        order = CartP.objects.create(
            user=request.user, ordered_date=ordered_date)
        order.items.add(order_item)
        messages.info(request, "This item was added to your cart.")
        return redirect("clothesL:order-summary")


@login_required
def remove_from_cart_p(request, slug):
    item = get_object_or_404(Clothes, slug=slug)
    order_qs = CartP.objects.filter(
        user=request.user,
        ordered=False
    )
    if order_qs.exists():
        order = order_qs[0]
        # check if the order item is in the order
        if order.items.filter(product__slug=item.slug).exists():
            order_item = CartItemP.objects.filter(
                product=item,
                user=request.user,
                ordered=False
            )[0]
            order.items.remove(order_item)
            messages.info(request, "This item was removed from your cart.")
            return redirect("clothesL:order-summary")
        else:
            messages.info(request, "This item was not in your cart")
            return redirect("clothesL:order-summary", slug=slug)
    else:
        messages.info(request, "You do not have an active order")
        return redirect("clothesL:order-summary", slug=slug)


@login_required
def remove_single_item_from_cart_p(request, slug):
    product = get_object_or_404(Clothes, slug=slug)
    order_qs = CartP.objects.filter(
        user=request.user,
        ordered=False
    )
    if order_qs.exists():
        order = order_qs[0]
        # check if the order item is in the order
        if order.items.filter(product__slug=product.slug).exists():
            order_item = CartItemP.objects.filter(
                product=product,
                user=request.user,
                ordered=False,
                shop=product.shop
            )[0]
            if order_item.quantity > 1:
                order_item.quantity -= 1
                order_item.save()
            else:
                order.items.remove(order_item)
            messages.info(request, "This item quantity was updated.")
            return redirect("clothesL:order-summary")
        else:
            messages.info(request, "This item was not in your cart")
            return redirect("clothesL:order-summary", slug=slug)
    else:
        messages.info(request, "You do not have an active order")
        return redirect("clothesL:order-summary", slug=slug)


@login_required
def comment(request, slug):
    try:
        a = Product.objects.get(slug=slug)
    except():
        raise Http404("ERROORRRRRR")
    if request.method == 'POST':
        text1 = request.POST['text']
        a.commentary_set.create(author=request.user, text=text1, clothes_id=a.id)
    return HttpResponseRedirect(reverse('market:product', args=(a.slug,)))

#
# class OrderSummaryView(LoginRequiredMixin, View):
#     def get(self, *args, **kwargs):
#         user_first_name = None
#         if self.request.user.is_authenticated:
#             user_first_name = get_user_first_name(self.request.user)
#         try:
#             order = Cart.objects.get(user=self.request.user, ordered=False)
#             context = {
#                 'object': order,
#                 'couponform': CouponForm(),
#                 'DISPLAY_COUPON_FORM': True,
#                 'user_first_name': user_first_name
#             }
#             return render(self.request, 'market/order_summary.html', context)
#         except ObjectDoesNotExist:
#             messages.warning(self.request, "You do not have an active order")
#             print("You do not have an active order")
#             return redirect("/")


# def get_coupon(request, code):
#     try:
#         coupon = Coupon.objects.get(code=code)
#         return coupon
#     except ObjectDoesNotExist:
#         messages.info(request, "This coupon does not exist")
#         return redirect("core:checkout")


# class CheckSales(LoginRequiredMixin, View):
#     def get(self, request):
#         user_first_name = None
#         if self.request.user.is_authenticated:
#             user_first_name = get_user_first_name(self.request.user)
#         user = self.request.user
#         shoptouser = ShopToUser.objects.get(user=user.id)
#         shop_id = shoptouser.shop.id
#         shop = Shops.objects.get(id=shop_id)
#
#         all = CartItemP.objects.all()
#         not_all = []
#         for al in all:
#             if al.shop.id == shop_id:
#                 not_all.append(al)
#         return render(request, 'clothesL/checksales.html',
#                       {'all': not_all, 'shop': shop, 'user_first_name': user_first_name})


class PaymentView(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        user_first_name = None
        if self.request.user.is_authenticated:
            user_first_name = get_user_first_name(self.request.user)
        try:
            print("kirdi")
            order = CartP.objects.get(user=self.request.user, ordered=False)
            shop_order = {}
            # shops= set()
            # for i in range order
            print("in try")
            print(order)
            order_items = order.items.all()
            print('order.get_totl()', order.get_total())

            user = None
            if self.request.user.is_authenticated:
                user = self.request.user
            print(user.id)
            user_purse = Purse.get_purse_by_userid(user.id)
            shop1 = ShopToUser.get_purse_by_shop_id(1)
            shop2 = ShopToUser.get_purse_by_shop_id(2)
            print(shop1.user.id)
            shop1_purse = Purse.get_purse_by_userid(shop1.user.id)
            shop2_purse = Purse.get_purse_by_userid(shop2.user.id)
            print(shop1_purse, 'shop1')
            print(shop2_purse, 'shop2')

            shop1_money = get_user_money(shop1.user)
            print(shop2.user.username)
            shop2_money = get_user_money(shop2.user)

            added_money_shop1 = 0
            added_money_shop2 = 0
            error_message = None
            print('error', 'hello')
            with transaction.atomic():
                if user:
                    with transaction.atomic():
                        money = get_user_money(user)
                        print('shop1 money', shop1_money)
                        print('shop2 money', shop2_money)
                        print('user money', money)
                        print('money', money)
                        print('total:', order.get_total())
                        if money >= order.get_total():
                            with transaction.atomic():
                                print(order_items)
                                for order_item in order_items:
                                    # print(order_item.toString())
                                    money = money - order_item.get_final_price()
                                    print('order_item.get_final_price()', order_item.get_final_price())
                                    money_enc = (encrypt(user.id, str(money), user.username)).decode('ascii')
                                    user_purse.money = money_enc
                                    user_purse.save()
                            with transaction.atomic():
                                for order_item in order_items:
                                    if order_item.shop.id == 1:
                                        added_money_shop1 += order_item.get_final_price()
                                        shop1_money += order_item.get_final_price()
                                        print('updated shop 1', shop1_money)
                                        shop1_purse.money = (
                                            encrypt(shop1.user.id, str(shop1_money), shop1.user.username)).decode(
                                            'ascii')
                                        shop1_purse.save()
                                    elif order_item.shop.id == 2:
                                        added_money_shop2 += order_item.get_final_price()
                                        shop2_money = shop2_money + order_item.get_final_price()
                                        print('updated shop 2', shop2_money)
                                        shop2_purse.money = (
                                            encrypt(shop2.user.id, str(shop2_money), shop2.user.username)).decode(
                                            'ascii')

                                        shop2_purse.save()
                            error_message = 'Successfully transfered !!'
                        else:
                            error_message = 'Not enough money !!'
                            messages.warning(self.request, error_message)
                            return redirect("/", {'user_first_name': user_first_name})

                else:
                    error_message = 'There is no user with this email !!'

                print(error_message)

            messages.success(self.request, "Your order was successful!")
            return redirect("/main/block/transactions/new",
                            {'user_first_name': user_first_name, 'added_money_shop1': added_money_shop1,
                             'added_money_shop2': added_money_shop2})
            # return redirect("block:transactions", {'order': order})
        except:
            print("oshibka")
            messages.warning(self.request, "Yoshiibka")
            return redirect("/", {'user_first_name': user_first_name})


class AddCouponView(View):
    def post(self, *args, **kwargs):
        form = CouponForm(self.request.POST or None)
        if form.is_valid():
            try:
                code = form.cleaned_data.get('code')
                order = CartP.objects.get(
                    user=self.request.user, ordered=False)
                order.coupon = get_coupon(self.request, code)
                order.save()
                messages.success(self.request, "Successfully added coupon")
                return redirect("clothesL:order-summary")
            except ObjectDoesNotExist:
                messages.info(self.request, "You do not have an active order")
                return redirect("clothesL:order-summary")


class ItemDetailViewP(DetailView):
    model = Clothes
    template_name = "clothesL/product.html"


class PurseView(LoginRequiredMixin, View):
    def get(self, request):
        user_first_name = None
        user_email = None
        user_last_name = None
        if self.request.user.is_authenticated:
            user_first_name = get_user_first_name(self.request.user)

        user = None
        if request.user.is_authenticated:
            user = request.user
            user_email = get_user_email(user)
            user_last_name = get_user_last_name(user)
        purse = Purse.get_purse_by_userid(user.id)

        orders = CartP.objects.filter(user_id=user.id)
        data = {}
        data['user'] = user
        data['purse'] = purse
        data['money'] = get_user_money(user)
        data['user_first_name'] = user_first_name
        data['user_last_name'] = user_last_name
        data['user_email'] = user_email

        if not ShopToUser.objects.filter(user=request.user.id).exists():
            data['orders'] = orders
        print('email', user_email)
        return render(request, 'clothesL/account.html', data)
