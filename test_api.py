#!/usr/bin/env python3
"""
Sample script to test the Credit Approval System API
Run this after starting the Django server to test all endpoints
"""

import requests
import json
import time

# Base URL for the API
BASE_URL = "http://localhost:8000/api"

def test_register_customer():
    """Test customer registration endpoint"""
    print("Testing customer registration...")
    
    url = f"{BASE_URL}/register/"
    data = {
        "first_name": "John",
        "last_name": "Doe", 
        "age": 30,
        "phone_number": "1234567890",
        "monthly_salary": 50000.00
    }
    
    response = requests.post(url, json=data)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    if response.status_code == 201:
        return response.json()['customer_id']
    return None

def test_check_eligibility(customer_id):
    """Test loan eligibility check endpoint"""
    print(f"\nTesting loan eligibility for customer {customer_id}...")
    
    url = f"{BASE_URL}/check-eligibility/"
    data = {
        "customer_id": customer_id,
        "loan_amount": 100000.00,
        "interest_rate": 12.00,
        "tenure": 12
    }
    
    response = requests.post(url, json=data)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    return response.json()

def test_create_loan(customer_id):
    """Test loan creation endpoint"""
    print(f"\nTesting loan creation for customer {customer_id}...")
    
    url = f"{BASE_URL}/create-loan/"
    data = {
        "customer_id": customer_id,
        "loan_amount": 100000.00,
        "interest_rate": 12.00,
        "tenure": 12
    }
    
    response = requests.post(url, json=data)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    if response.status_code == 201:
        return response.json()['loan_id']
    return None

def test_view_loan(loan_id):
    """Test view loan details endpoint"""
    print(f"\nTesting view loan details for loan {loan_id}...")
    
    url = f"{BASE_URL}/view-loan/{loan_id}/"
    response = requests.get(url)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

def test_view_customer_loans(customer_id):
    """Test view customer loans endpoint"""
    print(f"\nTesting view customer loans for customer {customer_id}...")
    
    url = f"{BASE_URL}/view-loans/{customer_id}/"
    response = requests.get(url)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

def test_edge_cases():
    """Test edge cases and error handling"""
    print("\nTesting edge cases...")
    
    # Test with non-existent customer
    print("1. Testing eligibility with non-existent customer...")
    url = f"{BASE_URL}/check-eligibility/"
    data = {
        "customer_id": 99999,
        "loan_amount": 100000.00,
        "interest_rate": 12.00,
        "tenure": 12
    }
    response = requests.post(url, json=data)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    # Test with invalid data
    print("\n2. Testing registration with invalid phone number...")
    url = f"{BASE_URL}/register/"
    data = {
        "first_name": "Jane",
        "last_name": "Smith",
        "age": 25,
        "phone_number": "123",  # Invalid phone number
        "monthly_salary": 40000.00
    }
    response = requests.post(url, json=data)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

def main():
    """Main test function"""
    print("Starting Credit Approval System API Tests")
    print("=" * 50)
    
    try:
        # Test customer registration
        customer_id = test_register_customer()
        
        if customer_id:
            # Test eligibility check
            eligibility_result = test_check_eligibility(customer_id)
            
            # Test loan creation
            loan_id = test_create_loan(customer_id)
            
            if loan_id:
                # Test view loan details
                test_view_loan(loan_id)
                
                # Test view customer loans
                test_view_customer_loans(customer_id)
        
        # Test edge cases
        test_edge_cases()
        
        print("\n" + "=" * 50)
        print("API tests completed!")
        print("\nFor more detailed API documentation, visit:")
        print("http://localhost:8000/api/docs/")
        
    except requests.exceptions.ConnectionError:
        print("Could not connect to the API server.")
        print("Make sure the Django server is running on http://localhost:8000")
        print("Run: docker-compose up --build")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
