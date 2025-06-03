from django.urls import path, include
from . import views

urlpatterns = [
    path('checkouts/', views.CheckoutView.as_view(), name='checkouts'),
    path('checkouts/<int:checkout_id>/', views.CheckoutView.as_view(), name='checkout-detail'),
    path('create-checkout/', views.CreateCheckoutView.as_view(), name='create-checkout'),
    path('update-checkout/<int:checkout_id>/', views.UpdateCheckoutView.as_view(), name='update-checkout'),
    path('payment/', include('payment.urls')),
    path('complete-checkout/', views.CompleteCheckoutView.as_view(), name='complete-checkout'),
    path('update-order-status/<int:order_id>/', views.UpdateOrderStatusView.as_view(), name='update-order-status'),
    path('my-orders/', views.CustomerOrderHistoryView.as_view(), name='customer-order-history'),
]