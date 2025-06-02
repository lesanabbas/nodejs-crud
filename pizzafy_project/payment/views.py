import uuid
from .models import Payment, Transaction
from order.models import Checkout
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated

# Create your views here.
class CreatePaymentView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        # Extract data from request
        checkout_id = request.data.get("checkout_id")
        payment_method = request.data.get("payment_method")
        
        if not checkout_id or not payment_method:
            raise ValidationError("Both checkout_id and payment_method are required.")
        
        # Fetch checkout object
        try:
            checkout = Checkout.objects.get(id=checkout_id)
        except Checkout.DoesNotExist:
            return Response({"message": "Checkout not found"}, status=status.HTTP_404_NOT_FOUND)
        
        # Validate payment method
        if payment_method not in ["COD", "Online"]:
            raise ValidationError("Invalid payment method. Choose 'COD' or 'Online'.")
        
        # Create Payment object
        payment = Payment.objects.create(
            checkout=checkout,
            payment_method=payment_method,
            amount=checkout.total_price,  # The amount is the total price of the checkout
            status="Completed",  # Set initial status to Pending
        )

        # Create a Transaction object for the payment
        transaction = Transaction.objects.create(
            payment=payment,
            transaction_id=str(uuid.uuid4()),  # Generate a unique transaction ID
            amount=payment.amount,
            transaction_status="Success",  # Set initial status to Pending
            gateway_response="",  # Can be updated with real gateway response
        )

        # Return response with payment and transaction details
        return Response(
            {
                "message": "Payment created successfully",
                "payment_id": payment.id,
                "transaction_id": transaction.transaction_id,
                "amount": payment.amount,
                "payment_status": payment.status,
                "transaction_status": transaction.transaction_status,
            },
            status=status.HTTP_201_CREATED,
        )