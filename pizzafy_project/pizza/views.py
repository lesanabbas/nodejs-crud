from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Pizza
from .serializers import PizzaSerializer
from core.permissions import IsAdmin
# from rest_framework.permissions import IsAdminUser
from rest_framework import status

# Create your views here.
class PizzaViewSet(viewsets.ModelViewSet):
    queryset = Pizza.objects.all()
    serializer_class = PizzaSerializer
    permission_classes = [IsAdmin]  # Use Django's admin permission check

    # PATCH /pizzas/<pk>/update_stock/
    @action(detail=True, methods=['patch'], url_path='update_stock')
    def update_stock(self, request, pk=None):
        pizza = self.get_object()
        stock = request.data.get('stock')
        if stock is not None:
            pizza.stock = stock
            pizza.save()
            return Response({"status": "stock updated"}, status=status.HTTP_200_OK)
        return Response({"error": "stock is required"}, status=status.HTTP_400_BAD_REQUEST)

    # DELETE /pizzas/<pk>/delete/
    @action(detail=True, methods=['delete'], url_path='delete')
    def delete_pizza(self, request, pk=None):
        pizza = self.get_object()
        pizza.delete()
        return Response({"status": "pizza deleted"}, status=status.HTTP_204_NO_CONTENT)