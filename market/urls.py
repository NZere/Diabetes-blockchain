from django.contrib import admin
from django.urls import path
from market import views
from market.views import PaymentView

app_name = 'market'
urlpatterns = [

    path('', views.index, name='index'),
    path('product/<slug>/', views.product, name='product'),
    path('products/', views.get_all_products, name='products'),
    path('add-to-cart/<slug>/', views.add_to_cart, name='add-to-cart'),
    path('add-coupon/', views.AddCouponView.as_view(), name='add-coupon'),
    path('remove-from-cart/<slug>/', views.remove_from_cart, name='remove-from-cart'),
    path('remove-item-from-cart/<slug>/', views.remove_single_item_from_cart,
         name='remove-single-item-from-cart-p'),
    path('order-summary/', views.OrderSummaryView.as_view(), name='order-summary'),
    path('payment/', PaymentView.as_view(), name='payment'),

    path('get_all_products/', views.get_all_products, name='get_all_products'),
    path('get_all_products_filter/', views.get_all_products_filter, name='get_all_products_filter'),

    path('comment/<slug>/', views.comment, name='comment'),
]