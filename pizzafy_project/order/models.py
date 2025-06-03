from django.db import models
from core.models import User as CustomUser
from pizza.models import Pizza

# Order model: Represents the confirmed order after checkout
class Order(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    status = models.CharField(
        max_length=20,
        choices=[("Unfulfilled", "Unfulfilled"), ("Fulfilled", "Fulfilled"), ("Cancel", "Cancel")],
        default="Unfulfilled",
    )
    total_price = models.DecimalField(max_digits=10, decimal_places=2)  # Total price after checkout
    shipping_address = models.TextField()  # Shipping address at the time of order placement
    billing_address = models.TextField()  # Billing address at the time of order placement
    payment_status = models.CharField(
        max_length=20,
        choices=[("Pending", "Pending"), ("Paid", "Paid"), ("Failed", "Failed")],
        default="Pending",
    )
    delivery_date = models.DateTimeField(null=True, blank=True)  # Actual delivery date
    delivery_partner = models.ForeignKey(CustomUser, related_name="assigned_orders", null=True, blank=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)  # Order creation timestamp

    def __str__(self):
        return f"Order {self.id} for {self.user.username}"

# OrderLine model: Represents the pizza items within an order
class OrderLine(models.Model):
    order = models.ForeignKey(Order, related_name="order_lines", on_delete=models.CASCADE)
    pizza = models.ForeignKey(Pizza, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)  # Quantity of pizza in the order
    price = models.DecimalField(max_digits=6, decimal_places=2)  # Price per pizza at the time of order
    size = models.CharField(max_length=20, choices=[("Small", "Small"), ("Medium", "Medium"), ("Large", "Large")])
    customizations = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.quantity} x {self.pizza.name} ({self.size}) in Order {self.order.id}"

# Checkout model: Represents the shopping cart before the order is confirmed
class Checkout(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    shipping_address = models.TextField()  # Shipping address during checkout
    billing_address = models.TextField()  # Billing address during checkout
    created_at = models.DateTimeField(auto_now_add=True)  # Timestamp when the cart was created
    updated_at = models.DateTimeField(auto_now=True)  # Timestamp when the cart was updated

    def __str__(self):
        return f"Checkout for {self.user.username} - {self.checkout_status}"

# CheckoutLine model: Represents the pizza items in the cart (before order placement)
class CheckoutLine(models.Model):
    checkout = models.ForeignKey(Checkout, related_name="checkout_lines", on_delete=models.CASCADE)
    pizza = models.ForeignKey(Pizza, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)  # Quantity of pizza in the cart
    price = models.DecimalField(max_digits=6, decimal_places=2)  # Price per pizza in the checkout
    size = models.CharField(max_length=20, choices=[("Small", "Small"), ("Medium", "Medium"), ("Large", "Large")])
    customizations = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.quantity} x {self.pizza.name} ({self.size}) in Checkout {self.checkout.id}"