import logging
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Order, OrderLine, Checkout, CheckoutLine, Review
from payment.models import Payment
from core.models import User as CustomUser
from pizza.models import Pizza
from .serializers import OrderSerializer, CheckoutSerializer
from core.permissions import IsAdmin, IsCustomer
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError

log = logging.getLogger(__name__)


class UpdateOrderStatusView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, order_id):
        user = request.user
        new_status = request.data.get("status")
        comment = request.data.get("comment")

        # Validate comment
        if not comment:
            return Response({"error": "Comment is required to update the status"}, status=status.HTTP_400_BAD_REQUEST)

        # Fetch the order
        try:
            order = Order.objects.get(id=order_id)
        except Order.DoesNotExist:
            return Response({"error": "Order not found"}, status=status.HTTP_404_NOT_FOUND)

        # Prevent status change if already canceled
        if order.status == "Cancel":
            return Response({"error": "Order is already canceled and cannot be changed"}, status=status.HTTP_400_BAD_REQUEST)

        # Role-based validation
        if user.role == "Customer" and new_status != "Cancel":
            return Response({"error": "Customers can only cancel orders"}, status=status.HTTP_400_BAD_REQUEST)

        if user.role not in ["Admin", "DeliveryPartner"] and new_status not in ["Cancel"]:
            return Response({"error": "You do not have permission to update the status"}, status=status.HTTP_403_FORBIDDEN)

        # Validate new status
        valid_statuses = ["Unfulfilled", "Fulfilled", "Cancel"]
        if new_status not in valid_statuses:
            return Response({"error": "Invalid status"}, status=status.HTTP_400_BAD_REQUEST)

        # Update the order status and save the comment
        order.status = new_status
        order.comment = comment
        order.save()

        return Response({"status": "Order status updated"}, status=status.HTTP_200_OK)


class CheckoutView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, checkout_id=None):
        # If checkout_id is provided, return the specific checkout
        if checkout_id:
            try:
                checkout = Checkout.objects.get(id=checkout_id, user=request.user)
            except Checkout.DoesNotExist:
                return Response({"error": "Checkout not found or does not belong to user"}, status=status.HTTP_404_NOT_FOUND)
            serializer = CheckoutSerializer(checkout)
            return Response({"checkout": serializer.data}, status=status.HTTP_200_OK)

        # If no checkout_id is provided, return all checkouts for the user
        checkouts = Checkout.objects.filter(user=request.user)
        serializer = CheckoutSerializer(checkouts, many=True)
        return Response({"checkouts": serializer.data}, status=status.HTTP_200_OK)


class CustomerOrderHistoryView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        user = request.user
        orders = Order.objects.filter(user=user).order_by("-created_at")
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class CreateCheckoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # Extracting user details and request data
        user = request.user
        shipping_address = request.data.get("shipping_address")
        billing_address = request.data.get("billing_address")
        checkout_lines_data = request.data.get("checkout_lines")

        # # Basic validation for the addresses
        if not shipping_address or not billing_address:
            raise ValidationError(
                "Both shipping_address and billing_address are required."
            )

        # # Create the checkout object
        checkout = Checkout.objects.create(
            user=user,
            total_price=0,  # Will calculate total price later
            shipping_address=shipping_address,
            billing_address=billing_address,
        )

        total_price = 0
        # # Add checkout lines
        for line_data in checkout_lines_data:
            pizza = Pizza.objects.get(id=line_data["pizza_id"])
            price = line_data["price"]
            quantity = line_data["quantity"]
            size = line_data["size"]

            # Calculate total price
            total_price += price * quantity

            # Create CheckoutLine
            CheckoutLine.objects.create(
                checkout=checkout,
                pizza=pizza,
                quantity=quantity,
                price=price,
                size=size,
                customizations=line_data.get("customizations", ""),
            )

        # # Update the total price of the checkout
        checkout.total_price = total_price
        checkout.save()

        serializer = CheckoutSerializer(checkout)

        # Return response
        return Response(
            {"message": "Checkout created", "checkout_data": serializer.data},
            status=status.HTTP_201_CREATED,
        )


class UpdateCheckoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, checkout_id):
        # Extract the checkout ID from the request

        if not checkout_id:
            raise ValidationError("checkout_id is required")

        # Get the checkout object
        try:
            checkout = Checkout.objects.get(id=checkout_id)
        except Checkout.DoesNotExist:
            return Response(
                {"message": "Checkout not found"}, status=status.HTTP_404_NOT_FOUND
            )

        # Update shipping and billing addresses if provided
        shipping_address = request.data.get("shipping_address")
        billing_address = request.data.get("billing_address")

        if shipping_address:
            checkout.shipping_address = shipping_address
        if billing_address:
            checkout.billing_address = billing_address

        checkout.save()

        # Handle checkout line updates (adding, removing, or updating)
        checkout_lines_data = request.data.get("checkout_lines", [])
        total_price = checkout.total_price

        for line_data in checkout_lines_data:
            checkout_line_id = line_data.get("checkout_line_id")
            action = line_data.get("action", "update")  # Default action is 'update'
            pizza_id = line_data.get("pizza_id")
            quantity = line_data.get("quantity")
            size = line_data.get("size")
            price = line_data.get("price")
            customizations = line_data.get("customizations", "")

            if action == "remove" and checkout_line_id:
                try:
                    checkout_line = CheckoutLine.objects.get(
                        id=checkout_line_id, checkout=checkout
                    )
                    total_price -= checkout_line.price * checkout_line.quantity
                    checkout_line.delete()
                except CheckoutLine.DoesNotExist:
                    return Response(
                        {"message": f"Checkout line {checkout_line_id} not found"},
                        status=status.HTTP_404_NOT_FOUND,
                    )

            elif action == "add" or action == "update":
                if action == "add" or not checkout_line_id:
                    # If the line doesn't exist, create a new one
                    try:
                        pizza = Pizza.objects.get(id=pizza_id)
                    except Pizza.DoesNotExist:
                        return Response(
                            {"message": f"Pizza with ID {pizza_id} not found"},
                            status=status.HTTP_404_NOT_FOUND,
                        )

                    # Create new checkout line
                    checkout_line = CheckoutLine.objects.create(
                        checkout=checkout,
                        pizza=pizza,
                        quantity=quantity,
                        price=price,
                        size=size,
                        customizations=customizations,
                    )

                    total_price += price * quantity
                elif action == "update" and checkout_line_id:
                    try:
                        checkout_line = CheckoutLine.objects.get(
                            id=checkout_line_id, checkout=checkout
                        )
                    except CheckoutLine.DoesNotExist:
                        return Response(
                            {"message": f"Checkout line {checkout_line_id} not found"},
                            status=status.HTTP_404_NOT_FOUND,
                        )

                    # Update existing checkout line
                    total_price -= (
                        checkout_line.price * checkout_line.quantity
                    )  # Remove old price

                    # Update only the provided values (keep old values if not provided)
                    if quantity is not None:
                        checkout_line.quantity = quantity
                    if price is not None:
                        checkout_line.price = price
                    if size:
                        checkout_line.size = size
                    if customizations:
                        checkout_line.customizations = customizations

                    checkout_line.save()
                    total_price += (
                        checkout_line.price * checkout_line.quantity
                    )  # Add new price

            # Update the total price of the checkout
            checkout.total_price = total_price
            checkout.save()

        serializer = CheckoutSerializer(checkout)

        return Response(
            {"message": "Checkout updated", "checkout_data": serializer.data},
            status=status.HTTP_200_OK,
        )


class CompleteCheckoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # Extract the checkout_id from the request
        checkout_id = request.data.get("checkout_id")
        if not checkout_id:
            raise ValidationError("checkout_id is required")

        # Get the checkout object
        try:
            checkout = Checkout.objects.get(id=checkout_id)
        except Checkout.DoesNotExist:
            return Response(
                {"message": "Checkout not found"}, status=status.HTTP_404_NOT_FOUND
            )

        # Create Order object
        order = Order.objects.create(
            user=checkout.user,
            total_price=checkout.total_price,
            shipping_address=checkout.shipping_address,
            billing_address=checkout.billing_address,
            status="Unfulfilled",  # Initially the order is unfulfilled
        )

        # Create OrderLine objects from CheckoutLine
        for checkout_line in checkout.checkout_lines.all():
            OrderLine.objects.create(
                order=order,
                pizza=checkout_line.pizza,
                quantity=checkout_line.quantity,
                price=checkout_line.price,
                size=checkout_line.size,
                customizations=checkout_line.customizations,
            )

        
        # Assign Delivery Partner (Dummy Setup: first available DeliveryPartner)
        delivery_partner = CustomUser.objects.filter(role="DeliveryPartner", is_available=True).first()
        if delivery_partner:
            order.delivery_partner = delivery_partner
            order.save()
            
        # Update Payment object with the associated order ID
        payment = Payment.objects.filter(checkout=checkout).first()
        if payment:
            payment.order = order
            payment.save()

        # Delete the Checkout and its associated CheckoutLines
        checkout.checkout_lines.all().delete()  # Delete checkout lines first to avoid foreign key issues
        checkout.delete()  # Delete the checkout after processing

        serializer = OrderSerializer(order)
        # Return the response with the order ID
        return Response(
            {"message": "Checkout completed", "order_data": serializer.data},
            status=status.HTTP_200_OK,
        )


class CreateReviewView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request, order_id):
        # Extract rating and comment from the request
        rating = request.data.get("rating")
        comment = request.data.get("comment")
        
        # Validation: Ensure rating and comment are provided
        if not all([rating, comment]):
            return Response(
                {"error": "Rating and comment are required"}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        # Validate rating is within 1-5
        if rating not in [1, 2, 3, 4, 5]:
            return Response(
                {"error": "Rating must be between 1 and 5"}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        # Retrieve the order, and check conditions
        try:
            order = Order.objects.get(id=order_id)
        except Order.DoesNotExist:
            return Response({"error": "Order not found"}, status=status.HTTP_404_NOT_FOUND)

        # Ensure the order is fulfilled and belongs to the user
        if order.status != "Fulfilled":
            return Response(
                {"error": "You can only review a delivery partner for a fulfilled order"}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        if order.user != request.user:
            return Response(
                {"error": "You can only review orders you placed"}, 
                status=status.HTTP_403_FORBIDDEN
            )

        # Ensure the order has a delivery partner assigned
        if not order.delivery_partner:
            return Response(
                {"error": "Order does not have an assigned delivery partner"}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        # Create the review for the delivery partner
        Review.objects.create(
            order=order,
            rating=rating,
            comment=comment,
        )

        return Response(
            {"message": "Review submitted successfully"}, 
            status=status.HTTP_201_CREATED
        )