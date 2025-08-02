from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from decimal import Decimal
from datetime import date, timedelta
from django.utils import timezone

from .models import Customer, Loan
from .services import CreditScoreCalculator, LoanEligibilityService


class CustomerModelTest(TestCase):
    def setUp(self):
        self.customer_data = {
            'first_name': 'John',
            'last_name': 'Doe',
            'age': 30,
            'phone_number': '1234567890',
            'monthly_salary': Decimal('50000.00')
        }

    def test_customer_creation(self):
        customer = Customer.objects.create(**self.customer_data)
        self.assertEqual(customer.first_name, 'John')
        self.assertEqual(customer.last_name, 'Doe')
        self.assertEqual(customer.approved_limit, 1800000)  # round(36 * 50000, -5)

    def test_approved_limit_calculation(self):
        customer = Customer(**self.customer_data)
        expected_limit = round(36 * float(customer.monthly_salary), -5)
        self.assertEqual(customer.calculate_approved_limit(), expected_limit)


class LoanModelTest(TestCase):
    def setUp(self):
        self.customer = Customer.objects.create(
            first_name='John',
            last_name='Doe',
            age=30,
            phone_number='1234567890',
            monthly_salary=Decimal('50000.00')
        )
        
        self.loan_data = {
            'customer': self.customer,
            'loan_amount': Decimal('100000.00'),
            'tenure': 12,
            'interest_rate': Decimal('10.00'),
            'monthly_repayment': Decimal('8792.00'),
            'start_date': timezone.now().date(),
            'end_date': timezone.now().date() + timedelta(days=365)
        }

    def test_loan_creation(self):
        loan = Loan.objects.create(**self.loan_data)
        self.assertEqual(loan.customer, self.customer)
        self.assertEqual(loan.loan_amount, Decimal('100000.00'))
        self.assertTrue(loan.is_active)


class CreditScoreCalculatorTest(TestCase):
    def setUp(self):
        self.customer = Customer.objects.create(
            first_name='John',
            last_name='Doe',
            age=30,
            phone_number='1234567890',
            monthly_salary=Decimal('50000.00'),
            approved_limit=Decimal('1800000.00')
        )

    def test_credit_score_calculation_no_loans(self):
        score = CreditScoreCalculator.calculate_credit_score(self.customer.customer_id)
        # Should get points for: no past loans (20), no current year activity (20), 
        # low volume ratio (20) = 60 points minimum
        self.assertGreaterEqual(score, 60)

    def test_credit_score_exceeds_approved_limit(self):
        # Create a loan that exceeds approved limit
        Loan.objects.create(
            customer=self.customer,
            loan_amount=Decimal('2000000.00'),  # Exceeds approved limit
            tenure=12,
            interest_rate=Decimal('10.00'),
            monthly_repayment=Decimal('175000.00'),
            start_date=timezone.now().date(),
            end_date=timezone.now().date() + timedelta(days=365)
        )
        
        score = CreditScoreCalculator.calculate_credit_score(self.customer.customer_id)
        self.assertEqual(score, 0)


class LoanEligibilityServiceTest(TestCase):
    def setUp(self):
        self.customer = Customer.objects.create(
            first_name='John',
            last_name='Doe',
            age=30,
            phone_number='1234567890',
            monthly_salary=Decimal('50000.00'),
            approved_limit=Decimal('1800000.00')
        )

    def test_calculate_monthly_emi(self):
        emi = LoanEligibilityService.calculate_monthly_emi(100000, 12, 12)
        # Should calculate compound interest EMI
        self.assertGreater(emi, 8000)
        self.assertLess(emi, 9500)

    def test_get_corrected_interest_rate(self):
        # High credit score
        rate = LoanEligibilityService.get_corrected_interest_rate(80)
        self.assertEqual(rate, 10.0)
        
        # Medium credit score
        rate = LoanEligibilityService.get_corrected_interest_rate(40)
        self.assertEqual(rate, 12.0)
        
        # Low credit score
        rate = LoanEligibilityService.get_corrected_interest_rate(20)
        self.assertEqual(rate, 16.0)
        
        # Very low credit score
        rate = LoanEligibilityService.get_corrected_interest_rate(5)
        self.assertIsNone(rate)

    def test_check_eligibility_high_emi(self):
        # Create a loan that would result in high EMI
        result = LoanEligibilityService.check_eligibility(
            self.customer.customer_id, 
            1000000,  # High loan amount
            15, 
            12
        )
        
        # Should be rejected due to high EMI
        self.assertFalse(result['approval'])
        self.assertIn('EMI', result['message'])


class CustomerAPITest(APITestCase):
    def test_register_customer(self):
        url = reverse('register_customer')
        data = {
            'first_name': 'John',
            'last_name': 'Doe',
            'age': 30,
            'phone_number': '1234567890',
            'monthly_salary': '50000.00'
        }
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Customer.objects.count(), 1)
        
        customer = Customer.objects.first()
        self.assertEqual(customer.first_name, 'John')
        self.assertEqual(customer.approved_limit, 1800000)

    def test_register_customer_invalid_data(self):
        url = reverse('register_customer')
        data = {
            'first_name': 'John',
            'last_name': 'Doe',
            'age': 30,
            'phone_number': '123',  # Invalid phone number
            'monthly_salary': '50000.00'
        }
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class EligibilityAPITest(APITestCase):
    def setUp(self):
        self.customer = Customer.objects.create(
            first_name='John',
            last_name='Doe',
            age=30,
            phone_number='1234567890',
            monthly_salary=Decimal('50000.00'),
            approved_limit=Decimal('1800000.00')
        )

    def test_check_eligibility(self):
        url = reverse('check_eligibility')
        data = {
            'customer_id': self.customer.customer_id,
            'loan_amount': '100000.00',
            'interest_rate': '12.00',
            'tenure': 12
        }
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        result = response.json()
        self.assertIn('approval', result)
        self.assertIn('monthly_installment', result)

    def test_check_eligibility_nonexistent_customer(self):
        url = reverse('check_eligibility')
        data = {
            'customer_id': 99999,  # Non-existent customer
            'loan_amount': '100000.00',
            'interest_rate': '12.00',
            'tenure': 12
        }
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        result = response.json()
        self.assertFalse(result['approval'])
        self.assertIn('not found', result['message'])


class LoanAPITest(APITestCase):
    def setUp(self):
        self.customer = Customer.objects.create(
            first_name='John',
            last_name='Doe',
            age=30,
            phone_number='1234567890',
            monthly_salary=Decimal('50000.00'),
            approved_limit=Decimal('1800000.00')
        )

    def test_create_loan(self):
        url = reverse('create_loan')
        data = {
            'customer_id': self.customer.customer_id,
            'loan_amount': '100000.00',
            'interest_rate': '12.00',
            'tenure': 12
        }
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        result = response.json()
        self.assertTrue(result['loan_approved'])
        self.assertIsNotNone(result['loan_id'])
        
        # Verify loan was created in database
        self.assertEqual(Loan.objects.count(), 1)

    def test_view_loan(self):
        loan = Loan.objects.create(
            customer=self.customer,
            loan_amount=Decimal('100000.00'),
            tenure=12,
            interest_rate=Decimal('10.00'),
            monthly_repayment=Decimal('8792.00'),
            start_date=timezone.now().date(),
            end_date=timezone.now().date() + timedelta(days=365)
        )
        
        url = reverse('view_loan', kwargs={'loan_id': loan.loan_id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        result = response.json()
        self.assertEqual(result['loan_id'], loan.loan_id)
        self.assertEqual(result['customer']['customer_id'], self.customer.customer_id)

    def test_view_customer_loans(self):
        # Create multiple loans for the customer
        for i in range(3):
            Loan.objects.create(
                customer=self.customer,
                loan_amount=Decimal('100000.00'),
                tenure=12,
                interest_rate=Decimal('10.00'),
                monthly_repayment=Decimal('8792.00'),
                start_date=timezone.now().date(),
                end_date=timezone.now().date() + timedelta(days=365)
            )
        
        url = reverse('view_customer_loans', kwargs={'customer_id': self.customer.customer_id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        result = response.json()
        self.assertEqual(len(result), 3)
