from django.shortcuts import render
from django.contrib.auth.models import User
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from .models import ExpanseIncome
from .serializers import ExpenseIncomeSerializer, ExpenseIncomeListSerializer, UserSerializer, CustomTokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from django.core.paginator import Paginator
from rest_framework.pagination import PageNumberPagination


def is_owner_or_superuser(user, obj):
    return user == obj.user or user.is_superuser

@api_view(['POST'])
def register_user(request):
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer
    

@api_view(['GET','POST'])
@permission_classes([IsAuthenticated])
def expense_list(request):
    if request.method == 'GET':
        if request.user.is_superuser:
            expenses = ExpanseIncome.objects.all()
        else:
            expenses = ExpanseIncome.objects.filter(user=request.user)
        paginator = PageNumberPagination()
        paginator.page_size = 4
        result_page = paginator.paginate_queryset(expenses, request)    
        serilizer = ExpenseIncomeListSerializer(result_page, many=True)
        return paginator.get_paginated_response(serilizer.data)
    
    elif request.method == 'POST':
        serializer = ExpenseIncomeSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def expense_detail(request, pk):
    try:
        expense = ExpanseIncome.objects.get(pk=pk)
    except ExpanseIncome.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    
    if not is_owner_or_superuser(request.user, expense):
        return Response(status=status.HTTP_403_FORBIDDEN)
    
    if request.method == 'GET':
        serializer = ExpenseIncomeSerializer(expense)
        return Response(serializer.data)
    
    elif request.method == 'PUT':
        serializer = ExpenseIncomeSerializer(expense, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'DELETE':
        expense.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)