#!/usr/bin/env python3
"""
Excel Data Preparation Guide
This script helps you prepare your Excel files for the Credit Approval System
"""

import pandas as pd
import os

def create_sample_customer_data():
    """Create a sample customer data file with proper column structure"""
    sample_data = {
        'Customer ID': [1, 2, 3, 4, 5],
        'First Name': ['John', 'Jane', 'Mike', 'Sarah', 'David'],
        'Last Name': ['Doe', 'Smith', 'Johnson', 'Wilson', 'Brown'],
        'Age': [30, 25, 35, 28, 42],
        'Phone Number': ['1234567890', '2345678901', '3456789012', '4567890123', '5678901234'],
        'Monthly Salary': [50000.00, 45000.00, 75000.00, 60000.00, 80000.00],
        'Approved Limit': [1800000.00, 1600000.00, 2700000.00, 2200000.00, 2900000.00],
        'Current Debt': [0.00, 25000.00, 0.00, 15000.00, 0.00]
    }
    
    df = pd.DataFrame(sample_data)
    df.to_excel('sample_customer_data.xlsx', index=False)
    print("Created sample_customer_data.xlsx")
    return df

def create_sample_loan_data():
    """Create a sample loan data file with proper column structure"""
    sample_data = {
        'Loan ID': [1001, 1002, 1003, 1004, 1005],
        'Customer ID': [1, 2, 1, 3, 4],
        'Principal': [100000.00, 50000.00, 200000.00, 75000.00, 150000.00],
        'Tenure': [12, 24, 36, 18, 24],
        'Interest Rate': [10.5, 12.0, 9.5, 11.0, 10.0],
        'Monthly payment': [8792.00, 2354.00, 6217.00, 4421.00, 6929.00],
        'EMIs paid on Time': [12, 18, 24, 12, 20],
        'Date of Approval': ['2023-01-15', '2022-06-20', '2021-03-10', '2023-05-05', '2022-09-12'],
        'End Date': ['2024-01-15', '2024-06-20', '2024-03-10', '2024-11-05', '2024-09-12']
    }
    
    df = pd.DataFrame(sample_data)
    df.to_excel('sample_loan_data.xlsx', index=False)
    print("Created sample_loan_data.xlsx")
    return df

def validate_customer_data(file_path):
    """Validate customer data file"""
    print(f"\nValidating customer data: {file_path}")
    
    try:
        df = pd.read_excel(file_path)
        issues = []
        
        required_cols = ['Customer ID', 'First Name', 'Last Name', 'Age', 'Phone Number', 'Monthly Salary']
        for col in required_cols:
            if col not in df.columns:
                issues.append(f"Missing required column: {col}")
        
        id_col = 'Customer ID' if 'Customer ID' in df.columns else 'customer_id'
        if id_col in df.columns:
            duplicates = df[id_col].duplicated().sum()
            if duplicates > 0:
                issues.append(f"{duplicates} duplicate Customer IDs found")
        
        if not issues:
            print("Customer data validation passed!")
        else:
            print("Issues found:")
            for issue in issues:
                print(f"   {issue}")
        
        return len(issues) == 0
        
    except Exception as e:
        print(f"Error validating customer data: {e}")
        return False

def validate_loan_data(file_path):
    """Validate loan data file"""
    print(f"\nValidating loan data: {file_path}")
    
    try:
        df = pd.read_excel(file_path)
        issues = []
        
        required_cols = ['Loan ID', 'Customer ID', 'Principal', 'Tenure', 'Interest Rate', 
                        'Monthly payment', 'EMIs paid on Time', 'Date of Approval', 'End Date']
        
        for col in required_cols:
            if col not in df.columns:
                issues.append(f"Missing required column: {col}")
        
        id_col = 'Loan ID' if 'Loan ID' in df.columns else 'loan_id'
        if id_col in df.columns:
            duplicates = df[id_col].duplicated().sum()
            if duplicates > 0:
                issues.append(f"{duplicates} duplicate Loan IDs found")
        
        if not issues:
            print("Loan data validation passed!")
        else:
            print("Issues found:")
            for issue in issues:
                print(f"   {issue}")
        
        return len(issues) == 0
        
    except Exception as e:
        print(f"Error validating loan data: {e}")
        return False

def main():
    print("EXCEL DATA PREPARATION GUIDE")
    print("=" * 60)
    
    create_sample_customer_data()
    create_sample_loan_data()
    
    customer_file = "customer_data.xlsx"
    loan_file = "loan_data.xlsx"
    
    customer_exists = os.path.exists(customer_file)
    loan_exists = os.path.exists(loan_file)
    
    print(f"\ncustomer_data.xlsx: {'Found' if customer_exists else 'Not found'}")
    print(f"loan_data.xlsx: {'Found' if loan_exists else 'Not found'}")
    
    if customer_exists:
        validate_customer_data(customer_file)
    
    if loan_exists:
        validate_loan_data(loan_file)
    
    print("\nNEXT STEPS:")
    if not customer_exists or not loan_exists:
        print("1. Place your Excel files in this directory")
        print("2. Use the sample files as templates")
    print("3. Run: python prepare_excel.py")
    print("4. Load data: docker-compose exec web python manage.py load_data")

if __name__ == "__main__":
    main()
