from decimal import Decimal
from datetime import datetime, date
from django.utils import timezone
from django.db.models import Sum, Q
from .models import Customer, Loan


class CreditScoreCalculator:
    """
    Calculate credit score based on the given criteria:
    1. Past loans paid on time
    2. Number of loans taken in past
    3. Loan activity in current year
    4. Loan approved volume vs current loan volume
    """
    
    @staticmethod
    def calculate_credit_score(customer_id):
        try:
            customer = Customer.objects.get(customer_id=customer_id)
        except Customer.DoesNotExist:
            return 0
        
        # Get all loans for this customer
        loans = Loan.objects.filter(customer=customer)
        
        # Check if sum of current loans exceeds approved limit
        current_loans = loans.filter(
            start_date__lte=timezone.now().date(),
            end_date__gte=timezone.now().date()
        )
        
        total_current_loan_amount = sum(
            loan.remaining_amount for loan in current_loans
        )
        
        if total_current_loan_amount > customer.approved_limit:
            return 0
        
        score = 0
        
        # 1. Past loans paid on time (40% weight)
        total_loans = loans.count()
        if total_loans > 0:
            total_emis = sum(loan.tenure for loan in loans)
            total_paid_on_time = sum(loan.emis_paid_on_time for loan in loans)
            
            if total_emis > 0:
                on_time_ratio = total_paid_on_time / total_emis
                score += on_time_ratio * 40
        
        # 2. Number of loans taken in past (20% weight)
        if total_loans <= 2:
            score += 20
        elif total_loans <= 5:
            score += 15
        elif total_loans <= 10:
            score += 10
        else:
            score += 5
        
        # 3. Loan activity in current year (20% weight)
        current_year = timezone.now().year
        current_year_loans = loans.filter(start_date__year=current_year).count()
        
        if current_year_loans == 0:
            score += 20
        elif current_year_loans <= 2:
            score += 15
        elif current_year_loans <= 4:
            score += 10
        else:
            score += 5
        
        # 4. Loan approved volume vs current loan volume (20% weight)
        if float(customer.approved_limit) > 0:
            volume_ratio = float(total_current_loan_amount) / float(customer.approved_limit)
            if volume_ratio <= 0.3:
                score += 20
            elif volume_ratio <= 0.5:
                score += 15
            elif volume_ratio <= 0.7:
                score += 10
            else:
                score += 5
        
        return min(100, max(0, score))


class LoanEligibilityService:
    """
    Service class to handle loan eligibility logic
    """
    
    @staticmethod
    def calculate_monthly_emi(loan_amount, interest_rate, tenure):
        """
        Calculate monthly EMI using compound interest formula:
        EMI = P * r * (1 + r)^n / ((1 + r)^n - 1)
        where P = principal, r = monthly interest rate, n = tenure in months
        """
        principal = float(loan_amount)
        monthly_rate = float(interest_rate) / 100 / 12
        
        if monthly_rate == 0:
            return principal / tenure
        
        emi = principal * monthly_rate * (1 + monthly_rate) ** tenure / ((1 + monthly_rate) ** tenure - 1)
        return round(emi, 2)
    
    @staticmethod
    def get_corrected_interest_rate(credit_score):
        """
        Get corrected interest rate based on credit score bands
        """
        if credit_score > 50:
            return 10.0
        elif credit_score > 30:
            return 12.0
        elif credit_score > 10:
            return 16.0
        else:
            return None  # Not eligible
    
    @staticmethod
    def check_eligibility(customer_id, loan_amount, interest_rate, tenure):
        """
        Check loan eligibility and return detailed response
        """
        try:
            customer = Customer.objects.get(customer_id=customer_id)
        except Customer.DoesNotExist:
            return {
                'customer_id': customer_id,
                'approval': False,
                'message': 'Customer not found'
            }
        
        # Calculate credit score
        credit_score = CreditScoreCalculator.calculate_credit_score(customer_id)
        
        # Get corrected interest rate
        corrected_interest_rate = LoanEligibilityService.get_corrected_interest_rate(credit_score)
        
        if corrected_interest_rate is None:
            return {
                'customer_id': customer_id,
                'approval': False,
                'interest_rate': float(interest_rate),
                'corrected_interest_rate': None,
                'tenure': tenure,
                'monthly_installment': 0,
                'message': 'Credit score too low for loan approval'
            }
        
        # Use corrected interest rate for EMI calculation
        final_interest_rate = corrected_interest_rate
        monthly_emi = LoanEligibilityService.calculate_monthly_emi(
            loan_amount, final_interest_rate, tenure
        )
        
        # Check if EMI exceeds 50% of monthly income
        max_allowed_emi = float(customer.monthly_salary) * 0.5
        
        # Get current EMIs
        current_loans = Loan.objects.filter(
            customer=customer,
            start_date__lte=timezone.now().date(),
            end_date__gte=timezone.now().date()
        )
        current_emis = sum(float(loan.monthly_repayment) for loan in current_loans)
        
        total_emis_after_loan = current_emis + monthly_emi
        
        approval = total_emis_after_loan <= max_allowed_emi
        
        return {
            'customer_id': customer_id,
            'approval': approval,
            'interest_rate': float(interest_rate),
            'corrected_interest_rate': final_interest_rate,
            'tenure': tenure,
            'monthly_installment': monthly_emi,
            'message': 'Loan approved' if approval else 'EMIs exceed 50% of monthly income'
        }
    
    @staticmethod
    def create_loan(customer_id, loan_amount, interest_rate, tenure):
        """
        Create a loan if eligible
        """
        eligibility = LoanEligibilityService.check_eligibility(
            customer_id, loan_amount, interest_rate, tenure
        )
        
        if not eligibility['approval']:
            return {
                'loan_id': None,
                'customer_id': customer_id,
                'loan_approved': False,
                'message': eligibility['message'],
                'monthly_installment': eligibility['monthly_installment']
            }
        
        try:
            customer = Customer.objects.get(customer_id=customer_id)
            
            # Use corrected interest rate
            final_interest_rate = eligibility['corrected_interest_rate']
            monthly_emi = eligibility['monthly_installment']
            
            # Calculate loan dates
            start_date = timezone.now().date()
            end_date = date(
                start_date.year + (start_date.month + tenure - 1) // 12,
                (start_date.month + tenure - 1) % 12 + 1,
                start_date.day
            )
            
            # Create loan
            loan = Loan.objects.create(
                customer=customer,
                loan_amount=loan_amount,
                tenure=tenure,
                interest_rate=final_interest_rate,
                monthly_repayment=monthly_emi,
                start_date=start_date,
                end_date=end_date
            )
            
            # Update customer's current debt
            customer.current_debt += loan_amount
            customer.save()
            
            return {
                'loan_id': loan.loan_id,
                'customer_id': customer_id,
                'loan_approved': True,
                'message': 'Loan approved and created successfully',
                'monthly_installment': monthly_emi
            }
            
        except Exception as e:
            return {
                'loan_id': None,
                'customer_id': customer_id,
                'loan_approved': False,
                'message': f'Error creating loan: {str(e)}',
                'monthly_installment': 0
            }
