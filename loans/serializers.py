from rest_framework import serializers
from .models import Customer, Loan


class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ['customer_id', 'first_name', 'last_name', 'age', 'phone_number', 
                 'monthly_salary', 'approved_limit', 'current_debt']
        read_only_fields = ['customer_id', 'approved_limit']

    def validate_phone_number(self, value):
        if not value.isdigit() or len(value) < 10:
            raise serializers.ValidationError("Phone number must be at least 10 digits")
        return value

    def validate_monthly_salary(self, value):
        if value <= 0:
            raise serializers.ValidationError("Monthly salary must be positive")
        return value


class CustomerRegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ['first_name', 'last_name', 'age', 'phone_number', 'monthly_salary']

    def validate_phone_number(self, value):
        if not value.isdigit() or len(value) < 10:
            raise serializers.ValidationError("Phone number must be at least 10 digits")
        return value

    def validate_monthly_salary(self, value):
        if value <= 0:
            raise serializers.ValidationError("Monthly salary must be positive")
        return value


class LoanSerializer(serializers.ModelSerializer):
    customer_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Loan
        fields = ['loan_id', 'customer', 'customer_name', 'loan_amount', 'tenure', 
                 'interest_rate', 'monthly_repayment', 'emis_paid_on_time', 
                 'start_date', 'end_date']
        read_only_fields = ['loan_id']

    def get_customer_name(self, obj):
        return f"{obj.customer.first_name} {obj.customer.last_name}"


class LoanDetailSerializer(serializers.ModelSerializer):
    customer = CustomerSerializer(read_only=True)
    
    class Meta:
        model = Loan
        fields = ['loan_id', 'customer', 'loan_amount', 'tenure', 
                 'interest_rate', 'monthly_repayment', 'emis_paid_on_time', 
                 'start_date', 'end_date']


class EligibilityCheckSerializer(serializers.Serializer):
    customer_id = serializers.IntegerField()
    loan_amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    interest_rate = serializers.DecimalField(max_digits=5, decimal_places=2)
    tenure = serializers.IntegerField()

    def validate_loan_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Loan amount must be positive")
        return value

    def validate_interest_rate(self, value):
        if value <= 0:
            raise serializers.ValidationError("Interest rate must be positive")
        return value

    def validate_tenure(self, value):
        if value <= 0:
            raise serializers.ValidationError("Tenure must be positive")
        return value


class LoanCreationSerializer(serializers.Serializer):
    customer_id = serializers.IntegerField()
    loan_amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    interest_rate = serializers.DecimalField(max_digits=5, decimal_places=2)
    tenure = serializers.IntegerField()

    def validate_loan_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Loan amount must be positive")
        return value

    def validate_interest_rate(self, value):
        if value <= 0:
            raise serializers.ValidationError("Interest rate must be positive")
        return value

    def validate_tenure(self, value):
        if value <= 0:
            raise serializers.ValidationError("Tenure must be positive")
        return value
