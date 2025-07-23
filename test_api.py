#!/usr/bin/env python3
"""
Simple test script for the Smart ATS API
"""
import requests
import json

def test_health_check():
    """Test the health check endpoint"""
    try:
        response = requests.get('http://localhost:5000/')
        print(f"Health Check Status: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"Health check failed: {e}")
        return False

def test_analyze_endpoint():
    """Test the analyze endpoint with sample data"""
    try:
        # Sample job description
        job_description = """
        We are looking for a Python Developer with experience in:
        - Python programming
        - Flask/Django frameworks
        - REST API development
        - Database management
        - Git version control
        - Docker containerization
        """
        
        # Note: This test requires a sample PDF file
        # For actual testing, you would need to provide a real PDF file
        print("Note: To test the /analyze endpoint, you need to provide a PDF file")
        print("Sample job description prepared for testing")
        print(f"Job Description: {job_description}")
        
        return True
    except Exception as e:
        print(f"Analyze endpoint test preparation failed: {e}")
        return False

if __name__ == "__main__":
    print("Testing Smart ATS API...")
    print("=" * 50)
    
    # Test health check
    print("1. Testing Health Check...")
    health_ok = test_health_check()
    print()
    
    # Test analyze endpoint preparation
    print("2. Testing Analyze Endpoint Preparation...")
    analyze_ok = test_analyze_endpoint()
    print()
    
    print("=" * 50)
    print(f"Health Check: {'✓ PASS' if health_ok else '✗ FAIL'}")
    print(f"Analyze Prep: {'✓ PASS' if analyze_ok else '✗ FAIL'}")
    
    if health_ok:
        print("\n✅ API is running and accessible!")
    else:
        print("\n❌ API is not accessible. Make sure it's running on localhost:5000")
