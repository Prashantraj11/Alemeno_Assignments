from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes

from .models import Customer, Loan
from .serializers import (
    CustomerSerializer, CustomerRegistrationSerializer, LoanSerializer,
    LoanDetailSerializer, EligibilityCheckSerializer, LoanCreationSerializer
)
from .services import LoanEligibilityService


@extend_schema(
    request=CustomerRegistrationSerializer,
    responses={201: CustomerSerializer},
    description="Register a new customer"
)
@api_view(['POST'])
def register_customer(request):
    """
    Register a new customer
    """
    serializer = CustomerRegistrationSerializer(data=request.data)
    if serializer.is_valid():
        customer = serializer.save()
        response_serializer = CustomerSerializer(customer)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    request=EligibilityCheckSerializer,
    responses={200: dict},
    description="Check loan eligibility for a customer"
)
@api_view(['POST'])
def check_eligibility(request):
    """
    Check loan eligibility based on customer ID and loan parameters
    """
    serializer = EligibilityCheckSerializer(data=request.data)
    if serializer.is_valid():
        customer_id = serializer.validated_data['customer_id']
        loan_amount = serializer.validated_data['loan_amount']
        interest_rate = serializer.validated_data['interest_rate']
        tenure = serializer.validated_data['tenure']
        
        eligibility_result = LoanEligibilityService.check_eligibility(
            customer_id, loan_amount, interest_rate, tenure
        )
        
        return Response(eligibility_result, status=status.HTTP_200_OK)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    request=LoanCreationSerializer,
    responses={201: dict},
    description="Create a new loan if eligible"
)
@api_view(['POST'])
def create_loan(request):
    """
    Create a new loan if the customer is eligible
    """
    serializer = LoanCreationSerializer(data=request.data)
    if serializer.is_valid():
        customer_id = serializer.validated_data['customer_id']
        loan_amount = serializer.validated_data['loan_amount']
        interest_rate = serializer.validated_data['interest_rate']
        tenure = serializer.validated_data['tenure']
        
        loan_result = LoanEligibilityService.create_loan(
            customer_id, loan_amount, interest_rate, tenure
        )
        
        if loan_result['loan_approved']:
            return Response(loan_result, status=status.HTTP_201_CREATED)
        else:
            return Response(loan_result, status=status.HTTP_400_BAD_REQUEST)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    responses={200: LoanDetailSerializer},
    parameters=[
        OpenApiParameter(name='loan_id', type=OpenApiTypes.INT, location=OpenApiParameter.PATH)
    ],
    description="Get loan details by loan ID"
)
@api_view(['GET'])
def view_loan(request, loan_id):
    """
    Get loan details by loan ID
    """
    loan = get_object_or_404(Loan, loan_id=loan_id)
    serializer = LoanDetailSerializer(loan)
    return Response(serializer.data, status=status.HTTP_200_OK)


@extend_schema(
    responses={200: LoanSerializer(many=True)},
    parameters=[
        OpenApiParameter(name='customer_id', type=OpenApiTypes.INT, location=OpenApiParameter.PATH)
    ],
    description="Get all loans for a specific customer"
)
@api_view(['GET'])
def view_customer_loans(request, customer_id):
    """
    Get all loans for a specific customer
    """
    customer = get_object_or_404(Customer, customer_id=customer_id)
    loans = Loan.objects.filter(customer=customer)
    serializer = LoanSerializer(loans, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)
