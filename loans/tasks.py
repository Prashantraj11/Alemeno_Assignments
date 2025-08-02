from celery import shared_task
import pandas as pd
import os
from django.conf import settings
from .models import Customer, Loan
from datetime import datetime


@shared_task
def ingest_customer_data(file_path=None):
    """
    Celery task to ingest customer data from Excel file
    """
    if not file_path:
        file_path = os.path.join(settings.BASE_DIR, 'customer_data.xlsx')
    
    try:
        # Read Excel file
        df = pd.read_excel(file_path)
        
        customers_created = 0
        customers_updated = 0
        
        for _, row in df.iterrows():
            try:
                customer, created = Customer.objects.get_or_create(
                    customer_id=row.get('Customer ID', row.get('customer_id')),
                    defaults={
                        'first_name': row.get('First Name', row.get('first_name', '')),
                        'last_name': row.get('Last Name', row.get('last_name', '')),
                        'age': int(row.get('Age', row.get('age', 0))),
                        'phone_number': str(row.get('Phone Number', row.get('phone_number', ''))),
                        'monthly_salary': float(row.get('Monthly Salary', row.get('monthly_salary', 0))),
                        'approved_limit': float(row.get('Approved Limit', row.get('approved_limit', 0))),
                        'current_debt': float(row.get('Current Debt', row.get('current_debt', 0))),
                    }
                )
                
                if created:
                    customers_created += 1
                else:
                    # Update existing customer
                    customer.first_name = row.get('First Name', row.get('first_name', customer.first_name))
                    customer.last_name = row.get('Last Name', row.get('last_name', customer.last_name))
                    customer.age = int(row.get('Age', row.get('age', customer.age)))
                    customer.phone_number = str(row.get('Phone Number', row.get('phone_number', customer.phone_number)))
                    customer.monthly_salary = float(row.get('Monthly Salary', row.get('monthly_salary', customer.monthly_salary)))
                    customer.approved_limit = float(row.get('Approved Limit', row.get('approved_limit', customer.approved_limit)))
                    customer.current_debt = float(row.get('Current Debt', row.get('current_debt', customer.current_debt)))
                    customer.save()
                    customers_updated += 1
                    
            except Exception as e:
                print(f"Error processing customer row: {e}")
                continue
        
        return {
            'status': 'success',
            'customers_created': customers_created,
            'customers_updated': customers_updated,
            'total_processed': len(df)
        }
        
    except Exception as e:
        return {
            'status': 'error',
            'message': str(e)
        }


@shared_task
def ingest_loan_data(file_path=None):
    """
    Celery task to ingest loan data from Excel file
    """
    if not file_path:
        file_path = os.path.join(settings.BASE_DIR, 'loan_data.xlsx')
    
    try:
        # Read Excel file
        df = pd.read_excel(file_path)
        
        loans_created = 0
        loans_updated = 0
        
        for _, row in df.iterrows():
            try:
                # Get customer
                customer_id = row.get('Customer ID', row.get('customer_id'))
                try:
                    customer = Customer.objects.get(customer_id=customer_id)
                except Customer.DoesNotExist:
                    print(f"Customer {customer_id} not found, skipping loan")
                    continue
                
                # Parse dates
                start_date = row.get('Date of Approval', row.get('start_date'))
                end_date = row.get('End Date', row.get('end_date'))
                
                if isinstance(start_date, str):
                    start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
                if isinstance(end_date, str):
                    end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
                
                loan, created = Loan.objects.get_or_create(
                    loan_id=row.get('Loan ID', row.get('loan_id')),
                    defaults={
                        'customer': customer,
                        'loan_amount': float(row.get('Principal', row.get('loan_amount', 0))),
                        'tenure': int(row.get('Tenure', row.get('tenure', 0))),
                        'interest_rate': float(row.get('Interest Rate', row.get('interest_rate', 0))),
                        'monthly_repayment': float(row.get('Monthly payment', row.get('monthly_repayment', 0))),
                        'emis_paid_on_time': int(row.get('EMIs paid on Time', row.get('emis_paid_on_time', 0))),
                        'start_date': start_date,
                        'end_date': end_date,
                    }
                )
                
                if created:
                    loans_created += 1
                else:
                    # Update existing loan
                    loan.customer = customer
                    loan.loan_amount = float(row.get('Principal', row.get('loan_amount', loan.loan_amount)))
                    loan.tenure = int(row.get('Tenure', row.get('tenure', loan.tenure)))
                    loan.interest_rate = float(row.get('Interest Rate', row.get('interest_rate', loan.interest_rate)))
                    loan.monthly_repayment = float(row.get('Monthly payment', row.get('monthly_repayment', loan.monthly_repayment)))
                    loan.emis_paid_on_time = int(row.get('EMIs paid on Time', row.get('emis_paid_on_time', loan.emis_paid_on_time)))
                    loan.start_date = start_date
                    loan.end_date = end_date
                    loan.save()
                    loans_updated += 1
                    
            except Exception as e:
                print(f"Error processing loan row: {e}")
                continue
        
        return {
            'status': 'success',
            'loans_created': loans_created,
            'loans_updated': loans_updated,
            'total_processed': len(df)
        }
        
    except Exception as e:
        return {
            'status': 'error',
            'message': str(e)
        }


@shared_task
def ingest_all_data():
    """
    Celery task to ingest both customer and loan data
    """
    customer_result = ingest_customer_data()
    loan_result = ingest_loan_data()
    
    return {
        'customer_ingestion': customer_result,
        'loan_ingestion': loan_result
    }
