from rest_framework import serializers
from .models import ExpanseIncome
from django.contrib.auth.models import User
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email','password']
        extra_kwargs = {'password': {'write_only': True}}
        
    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        return user
    
class ExpenseIncomeSerializer(serializers.ModelSerializer):
    total = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    class Meta:
        model = ExpanseIncome
        fields = '__all__'
        read_only_fields = ('user','created_at','updated_at')
        
class ExpenseIncomeListSerializer(serializers.ModelSerializer):
    total = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    class Meta:
        model = ExpanseIncome
        fields = ('id','title','amount','transaction_type','total','created_at')
        
class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['username'] = user.username
        token['is_superuser'] = user.is_superuser
        return token
