from django.db import models
from order.models import Order, Checkout

# Create your models here.
class Payment(models.Model):
    order = models.OneToOneField(Order, null=True, on_delete=models.CASCADE)
    checkout = models.OneToOneField(Checkout, null=True, on_delete=models.SET_NULL)
    payment_method = models.CharField(max_length=50, choices=[('COD', 'Cash on Delivery'), ('Online', 'Online')])
    amount = models.DecimalField(max_digits=6, decimal_places=2)
    status = models.CharField(max_length=50, choices=[('Pending', 'Pending'), ('Completed', 'Completed')], default='Pending')
    payment_date = models.DateTimeField(auto_now_add=True)  # Date of the payment
    
    def __str__(self):
        return f"Payment for Order {self.order.id} via {self.payment_method}"

class Transaction(models.Model):
    payment = models.ForeignKey(Payment, related_name='transactions', on_delete=models.CASCADE)
    transaction_id = models.CharField(max_length=100, unique=True)  # Unique ID for the transaction
    transaction_date = models.DateTimeField(auto_now_add=True)  # Date when the transaction occurred
    amount = models.DecimalField(max_digits=6, decimal_places=2)  # Amount of the transaction
    transaction_status = models.CharField(max_length=50, choices=[('Success', 'Success'), ('Failed', 'Failed'), ('Pending', 'Pending')])
    gateway_response = models.TextField(blank=True, null=True)  # Any additional response from the payment gateway
    
    def __str__(self):
        return f"Transaction {self.transaction_id} for Payment {self.payment.id}"