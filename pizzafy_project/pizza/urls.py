from django.urls import path
from .views import PizzaViewSet

urlpatterns = [
    path('', PizzaViewSet.as_view({'get': 'list', 'post': 'create'}), name='pizza-list-create'),
    path('<int:pk>/', PizzaViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}), name='pizza-detail'),

    # Custom actions
    path('<int:pk>/update_stock/', PizzaViewSet.as_view({'patch': 'update_stock'}), name='pizza-update-stock'),
    path('<int:pk>/delete/', PizzaViewSet.as_view({'delete': 'delete_pizza'}), name='pizza-custom-delete'),
]