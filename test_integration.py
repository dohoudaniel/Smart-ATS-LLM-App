#!/usr/bin/env python3
"""
Integration test script for Smart ATS Frontend-Backend communication
"""
import requests
import json
import time
import os
from pathlib import Path

# Configuration
BACKEND_URL = "https://api-mysmartats.onrender.com"
LOCAL_BACKEND_URL = "http://localhost:5000"

def test_backend_health(url):
    """Test if backend is accessible"""
    try:
        print(f"Testing backend health at: {url}")
        response = requests.get(f"{url}/", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Backend is healthy!")
            print(f"   Status: {data.get('status')}")
            print(f"   Message: {data.get('message')}")
            print(f"   Version: {data.get('version')}")
            return True
        else:
            print(f"❌ Backend health check failed: {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Backend not accessible: {e}")
        return False

def test_cors_headers(url):
    """Test CORS configuration"""
    try:
        print(f"\nTesting CORS headers...")
        response = requests.options(f"{url}/analyze", headers={
            'Origin': 'http://localhost:5173',
            'Access-Control-Request-Method': 'POST',
            'Access-Control-Request-Headers': 'Content-Type'
        })
        
        cors_headers = {
            'Access-Control-Allow-Origin': response.headers.get('Access-Control-Allow-Origin'),
            'Access-Control-Allow-Methods': response.headers.get('Access-Control-Allow-Methods'),
            'Access-Control-Allow-Headers': response.headers.get('Access-Control-Allow-Headers')
        }
        
        print(f"✅ CORS Headers:")
        for header, value in cors_headers.items():
            print(f"   {header}: {value}")
        
        return True
        
    except Exception as e:
        print(f"❌ CORS test failed: {e}")
        return False

def create_sample_pdf():
    """Create a simple PDF for testing (requires reportlab)"""
    try:
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import letter
        import io
        
        buffer = io.BytesIO()
        p = canvas.Canvas(buffer, pagesize=letter)
        
        # Add comprehensive sample resume content
        p.drawString(100, 750, "SARAH JOHNSON")
        p.drawString(100, 730, "Senior Python Developer")
        p.drawString(100, 710, "Email: sarah.johnson@email.com | Phone: (555) 987-6543")
        p.drawString(100, 690, "LinkedIn: linkedin.com/in/sarahjohnson | GitHub: github.com/sarahj")
        p.drawString(100, 670, "")
        p.drawString(100, 650, "TECHNICAL SKILLS:")
        p.drawString(120, 630, "• Programming: Python (6+ years), JavaScript, SQL, Bash")
        p.drawString(120, 610, "• Frameworks: Flask, Django, FastAPI, React")
        p.drawString(120, 590, "• Databases: PostgreSQL, MySQL, Redis, MongoDB")
        p.drawString(120, 570, "• Tools: Docker, Git, Jenkins, AWS, Kubernetes")
        p.drawString(120, 550, "• Testing: pytest, unittest, TDD, integration testing")
        p.drawString(100, 530, "")
        p.drawString(100, 510, "PROFESSIONAL EXPERIENCE:")
        p.drawString(120, 490, "Senior Python Developer | TechCorp Inc. | 2020-2024")
        p.drawString(120, 470, "• Developed microservices architecture using Flask and Docker")
        p.drawString(120, 450, "• Built REST APIs serving 1M+ requests daily")
        p.drawString(120, 430, "• Optimized PostgreSQL queries improving performance by 40%")
        p.drawString(120, 410, "• Implemented CI/CD pipelines using Jenkins and AWS")
        p.drawString(120, 390, "• Led team of 3 junior developers")
        p.drawString(100, 370, "")
        p.drawString(120, 350, "Python Developer | StartupXYZ | 2018-2020")
        p.drawString(120, 330, "• Developed web applications using Django framework")
        p.drawString(120, 310, "• Integrated third-party APIs and payment systems")
        p.drawString(120, 290, "• Wrote comprehensive unit tests achieving 95% coverage")
        
        p.save()
        buffer.seek(0)
        return buffer
        
    except ImportError:
        print("⚠️  reportlab not installed. Cannot create sample PDF.")
        print("   Install with: pip install reportlab")
        return None

def test_analyze_endpoint(url):
    """Test the analyze endpoint with sample data"""
    try:
        print(f"\nTesting analyze endpoint with Gemini 2.0...")

        # Enhanced job description for better testing
        job_description = """
        Senior Python Developer - Remote Position

        We are seeking an experienced Senior Python Developer to join our growing engineering team.

        REQUIRED QUALIFICATIONS:
        • 5+ years of Python programming experience
        • Strong experience with Flask or Django web frameworks
        • REST API development and microservices architecture
        • Database design and optimization (PostgreSQL, MySQL, Redis)
        • Git version control and collaborative development
        • Docker containerization and deployment
        • Unit testing, integration testing, and TDD practices
        • Linux/Unix system administration

        PREFERRED QUALIFICATIONS:
        • Cloud platforms experience (AWS, GCP, Azure)
        • Kubernetes orchestration and container management
        • CI/CD pipeline development (Jenkins, GitLab CI, GitHub Actions)
        • Message queues and event-driven architecture (RabbitMQ, Kafka)
        • Machine learning libraries (scikit-learn, pandas, numpy)
        • Frontend technologies (React, Vue.js, JavaScript)
        • Agile/Scrum development methodologies

        KEY RESPONSIBILITIES:
        • Design and develop scalable, high-performance web applications
        • Build and maintain robust REST APIs and microservices
        • Collaborate with cross-functional teams including DevOps and QA
        • Write clean, maintainable, and well-documented code
        • Participate in code reviews and technical architecture discussions
        • Mentor junior developers and contribute to team knowledge sharing
        • Optimize application performance and troubleshoot production issues

        COMPENSATION & BENEFITS:
        • Competitive salary: $120,000 - $160,000
        • Remote work flexibility
        • Health, dental, and vision insurance
        • 401(k) with company matching
        • Professional development budget
        """
        
        # Try to create a sample PDF
        pdf_buffer = create_sample_pdf()
        
        if pdf_buffer is None:
            print("❌ Cannot test analyze endpoint without PDF file")
            print("   To test manually:")
            print(f"   1. POST to {url}/analyze")
            print("   2. Form data: job_description (text) and resume (PDF file)")
            return False
        
        # Prepare the request
        files = {
            'resume': ('sample_resume.pdf', pdf_buffer, 'application/pdf')
        }
        data = {
            'job_description': job_description
        }
        
        print("   Sending request to analyze endpoint...")
        response = requests.post(f"{url}/analyze", files=files, data=data, timeout=120)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Analyze endpoint working!")
            print(f"   JD Match: {result.get('jd_match', 'N/A')}")
            print(f"   Missing Keywords: {len(result.get('missing_keywords', []))} found")
            print(f"   Profile Summary: {len(result.get('profile_summary', ''))} characters")
            return True
        else:
            print(f"❌ Analyze endpoint failed: {response.status_code}")
            try:
                error_data = response.json()
                print(f"   Error: {error_data.get('error', 'Unknown error')}")
            except:
                print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Analyze endpoint test failed: {e}")
        return False

def main():
    """Run all integration tests"""
    print("🚀 Smart ATS Integration Test")
    print("=" * 50)
    
    # Test both local and deployed backend
    backends_to_test = [
        ("Deployed Backend", BACKEND_URL),
        ("Local Backend", LOCAL_BACKEND_URL)
    ]
    
    results = {}
    
    for name, url in backends_to_test:
        print(f"\n📡 Testing {name}")
        print("-" * 30)
        
        # Test health
        health_ok = test_backend_health(url)
        
        if health_ok:
            # Test CORS
            cors_ok = test_cors_headers(url)
            
            # Test analyze endpoint
            analyze_ok = test_analyze_endpoint(url)
            
            results[name] = {
                'health': health_ok,
                'cors': cors_ok,
                'analyze': analyze_ok,
                'overall': health_ok and cors_ok and analyze_ok
            }
        else:
            results[name] = {
                'health': False,
                'cors': False,
                'analyze': False,
                'overall': False
            }
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 TEST SUMMARY")
    print("=" * 50)
    
    for name, result in results.items():
        status = "✅ PASS" if result['overall'] else "❌ FAIL"
        print(f"{name}: {status}")
        if not result['overall']:
            print(f"   Health: {'✅' if result['health'] else '❌'}")
            print(f"   CORS: {'✅' if result['cors'] else '❌'}")
            print(f"   Analyze: {'✅' if result['analyze'] else '❌'}")
    
    # Frontend testing instructions
    print("\n🌐 FRONTEND TESTING")
    print("-" * 30)
    print("To test the frontend:")
    print("1. cd Smart_ATS")
    print("2. npm run dev")
    print("3. Open http://localhost:5173")
    print("4. Upload a PDF resume and enter a job description")
    print("5. Click 'Analyze Resume'")
    
    # Check if any backend is working
    working_backends = [name for name, result in results.items() if result['overall']]
    
    if working_backends:
        print(f"\n✅ Integration ready! Working backends: {', '.join(working_backends)}")
    else:
        print(f"\n❌ No working backends found. Check deployment and configuration.")

if __name__ == "__main__":
    main()
