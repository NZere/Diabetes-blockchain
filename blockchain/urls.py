from django.urls import path
from . import views

urlpatterns = [
    path(r'block/mine', views.mine, name='mine'),
    path(r'block/transactions/new/', views.new_transaction, name='transactions'),
    path(r'block/chain/', views.full_chain, name='chain'),
    path(r'block/chains/', views.chains, name='chains'),
    path(r'block/connect', views.connect_node, name='connect-node'),
    path(r'block/replace', views.replace_chain, name='replace'),
]