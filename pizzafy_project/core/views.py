from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from .models import User as CustomUser
from .serializers import UserSerializer, RegisterSerializer
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from django.shortcuts import render
from django.http import JsonResponse


# Create your views here.

class RegisterView(APIView):
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "User registered successfully"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CustomTokenObtainPairView(TokenObtainPairView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)

        if response.status_code == 200:
            # Get the username from request.data instead of request.get()
            username_or_email = request.data.get("username") or request.data.get("email")
            user = CustomUser.objects.filter(username=username_or_email).first() or CustomUser.objects.filter(email=username_or_email).first()
            user_data = UserSerializer(user).data if user else {}
            
            return JsonResponse(
                {
                    "access": response.data.get("access"),
                    "refresh": response.data.get("refresh"),
                    "user": user_data,
                }
            )
        return response
    

class UpdateProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request):
        user = request.user
        serializer = RegisterSerializer(user, data=request.data, partial=True)  # `partial=True` allows updating only provided fields
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Profile updated successfully"}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
