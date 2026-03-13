from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    path('', views.order_list, name='order_list'),
    path('<int:order_id>/', views.order_detail, name='order_detail'),
    path('checkout/', views.checkout_view, name='checkout'),
    
    # PayPal URLs
    path('create-paypal-payment/<int:order_id>/', views.create_paypal_payment, name='create_paypal_payment'),
    path('payment-done/', views.payment_done, name='payment_done'),
    path('payment-cancelled/', views.payment_cancelled, name='payment_cancelled'),
]