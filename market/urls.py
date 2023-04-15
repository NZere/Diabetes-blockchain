from django.contrib import admin
from django.urls import path
from market import views

urlpatterns = [
    path('market/market/<slug>/', views.product, name='product'),
    path('market/add-to-cart/people/<slug>/', add_to_cart, name='add-to-cart-p'),
    path('market/add-coupon/', AddCouponView.as_view(), name='add-coupon'),
    path('market/remove-from-cart/<slug>/', remove_from_cart_p, name='remove-from-cart-p'),
    path('market/remove-item-from-cart/<slug>/', remove_single_item_from_cart_p,
         name='remove-single-item-from-cart-p'),
]