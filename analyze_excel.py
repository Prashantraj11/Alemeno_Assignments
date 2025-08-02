#!/usr/bin/env python3
"""
Excel Data Analysis Script
This script analyzes your Excel files and shows the column mapping
"""

import pandas as pd
import os

def analyze_excel_file(file_path, file_type):
    """Analyze Excel file structure and suggest column mappings"""
    
    print(f"\n{'='*60}")
    print(f"ANALYZING {file_type.upper()} FILE: {file_path}")
    print('='*60)
    
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return False
    
    try:
        # Read Excel file
        df = pd.read_excel(file_path)
        
        print(f"File Info:")
        print(f"   - Total rows: {len(df)}")
        print(f"   - Total columns: {len(df.columns)}")
        print(f"   - File size: {os.path.getsize(file_path)} bytes")
        
        print(f"\nColumn Names Found:")
        for i, col in enumerate(df.columns, 1):
            print(f"   {i:2d}. {col}")
        
        print(f"\nSample Data (first 3 rows):")
        print(df.head(3).to_string())
        
        # Column mapping suggestions
        if file_type == "customer":
            expected_mappings = {
                'customer_id': ['Customer ID', 'customer_id', 'ID', 'CustomerId'],
                'first_name': ['First Name', 'first_name', 'FirstName', 'fname'],
                'last_name': ['Last Name', 'last_name', 'LastName', 'lname'],
                'age': ['Age', 'age'],
                'phone_number': ['Phone Number', 'phone_number', 'Phone', 'PhoneNumber'],
                'monthly_salary': ['Monthly Salary', 'monthly_salary', 'Salary', 'Income'],
                'approved_limit': ['Approved Limit', 'approved_limit', 'Credit Limit', 'Limit'],
                'current_debt': ['Current Debt', 'current_debt', 'Debt', 'Outstanding']
            }
        else:  # loan
            expected_mappings = {
                'loan_id': ['Loan ID', 'loan_id', 'ID', 'LoanId'],
                'customer_id': ['Customer ID', 'customer_id', 'CustomerId'],
                'loan_amount': ['Principal', 'loan_amount', 'Amount', 'Loan Amount'],
                'tenure': ['Tenure', 'tenure', 'Duration', 'Term'],
                'interest_rate': ['Interest Rate', 'interest_rate', 'Rate', 'IR'],
                'monthly_repayment': ['Monthly payment', 'monthly_repayment', 'EMI', 'Payment'],
                'emis_paid_on_time': ['EMIs paid on Time', 'emis_paid_on_time', 'On Time', 'Paid On Time'],
                'start_date': ['Date of Approval', 'start_date', 'Start Date', 'Approval Date'],
                'end_date': ['End Date', 'end_date', 'Maturity Date', 'End']
            }
        
        print(f"\n🎯 Column Mapping Analysis:")
        found_mappings = {}
        missing_fields = []
        
        for field, possible_names in expected_mappings.items():
            found = False
            for col in df.columns:
                if col in possible_names:
                    found_mappings[field] = col
                    print(f"   ✅ {field:20} -> '{col}'")
                    found = True
                    break
            
            if not found:
                missing_fields.append(field)
                print(f"   ❌ {field:20} -> NOT FOUND")
        
        if missing_fields:
            print(f"\n⚠️  Missing Required Fields:")
            for field in missing_fields:
                print(f"   - {field}")
                print(f"     Expected column names: {', '.join(expected_mappings[field])}")
        
        print(f"\n📈 Data Quality Check:")
        
        # Check for null values
        null_counts = df.isnull().sum()
        if null_counts.sum() > 0:
            print(f"   ⚠️  Null values found:")
            for col, count in null_counts.items():
                if count > 0:
                    print(f"      - {col}: {count} null values ({count/len(df)*100:.1f}%)")
        else:
            print(f"   ✅ No null values found")
        
        # Check for duplicates
        duplicates = df.duplicated().sum()
        if duplicates > 0:
            print(f"   ⚠️  {duplicates} duplicate rows found")
        else:
            print(f"   ✅ No duplicate rows found")
        
        return True
        
    except Exception as e:
        print(f"❌ Error reading file: {e}")
        return False

def main():
    print("🔍 EXCEL DATA ANALYSIS TOOL")
    print("This tool will analyze your Excel files and check compatibility")
    
    # Analyze customer data
    customer_file = "customer_data.xlsx"
    analyze_excel_file(customer_file, "customer")
    
    # Analyze loan data
    loan_file = "loan_data.xlsx"
    analyze_excel_file(loan_file, "loan")
    
    print(f"\n{'='*60}")
    print("📋 RECOMMENDATIONS:")
    print('='*60)
    print("1. Ensure column names match the expected mappings above")
    print("2. Fix any missing required fields")
    print("3. Handle null values in required columns")
    print("4. Remove duplicate rows if any")
    print("5. Ensure date columns are in YYYY-MM-DD format")
    print("\n💡 The system is flexible with column names, but exact matches work best!")
    
    print(f"\n🚀 Ready to load data? Run:")
    print("   docker-compose exec web python manage.py load_data")

if __name__ == "__main__":
    main()
