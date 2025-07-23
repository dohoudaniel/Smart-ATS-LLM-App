#!/usr/bin/env python3
"""
Enhanced test script for the Smart ATS API with Gemini 2.0
"""
import requests
import json
import io
import os

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

def create_sample_pdf_content():
    """Create sample PDF content for testing"""
    try:
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import letter

        buffer = io.BytesIO()
        p = canvas.Canvas(buffer, pagesize=letter)

        # Add sample resume content
        p.drawString(100, 750, "John Doe")
        p.drawString(100, 730, "Senior Python Developer")
        p.drawString(100, 710, "Email: john.doe@email.com")
        p.drawString(100, 690, "Phone: (555) 123-4567")
        p.drawString(100, 670, "")
        p.drawString(100, 650, "SKILLS:")
        p.drawString(120, 630, "• Python programming (5+ years)")
        p.drawString(120, 610, "• Flask and Django frameworks")
        p.drawString(120, 590, "• REST API development")
        p.drawString(120, 570, "• PostgreSQL and MySQL databases")
        p.drawString(120, 550, "• Git version control")
        p.drawString(120, 530, "• Docker containerization")
        p.drawString(120, 510, "• Unit testing and TDD")
        p.drawString(100, 490, "")
        p.drawString(100, 470, "EXPERIENCE:")
        p.drawString(120, 450, "• Senior Python Developer at TechCorp (2020-2024)")
        p.drawString(120, 430, "• Built scalable web applications using Flask")
        p.drawString(120, 410, "• Designed and implemented REST APIs")
        p.drawString(120, 390, "• Worked with PostgreSQL databases")
        p.drawString(120, 370, "• Collaborated with cross-functional teams")

        p.save()
        buffer.seek(0)
        return buffer

    except ImportError:
        print("⚠️  reportlab not installed. Install with: pip install reportlab")
        return None

def test_analyze_endpoint():
    """Test the analyze endpoint with sample data"""
    try:
        # Sample job description
        job_description = """
        Senior Python Developer Position

        We are looking for an experienced Python Developer with the following qualifications:

        Required Skills:
        - 3+ years of Python programming experience
        - Experience with Flask or Django frameworks
        - REST API development and integration
        - Database design and management (PostgreSQL, MySQL)
        - Git version control
        - Docker containerization
        - Unit testing and test-driven development

        Preferred Skills:
        - Cloud platforms (AWS, GCP, Azure)
        - Microservices architecture
        - CI/CD pipelines
        - Kubernetes orchestration
        - Machine learning libraries

        Responsibilities:
        - Design and develop scalable web applications
        - Build and maintain REST APIs
        - Collaborate with cross-functional teams
        - Write clean, maintainable code
        - Participate in code reviews
        """

        # Try to create a sample PDF
        pdf_buffer = create_sample_pdf_content()

        if pdf_buffer is None:
            print("❌ Cannot test analyze endpoint without PDF file")
            print("   To test manually:")
            print("   1. POST to http://localhost:5000/analyze")
            print("   2. Form data: job_description (text) and resume (PDF file)")
            return False

        print("📄 Created sample PDF resume")
        print("📝 Prepared job description")
        print("🚀 Testing analyze endpoint...")

        # Prepare the request
        files = {
            'resume': ('sample_resume.pdf', pdf_buffer, 'application/pdf')
        }
        data = {
            'job_description': job_description
        }

        print("   Sending request to analyze endpoint...")
        response = requests.post('http://localhost:5000/analyze', files=files, data=data, timeout=120)

        if response.status_code == 200:
            result = response.json()
            print("✅ Analyze endpoint working!")
            print(f"   JD Match: {result.get('jd_match', 'N/A')}")
            print(f"   Missing Keywords: {result.get('missing_keywords', [])}")
            print(f"   Profile Summary: {result.get('profile_summary', 'N/A')[:100]}...")
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

def test_gemini_model():
    """Test if Gemini 2.0 model is accessible"""
    try:
        import google.generativeai as genai
        import os
        from dotenv import load_dotenv

        load_dotenv()
        api_key = os.getenv("GOOGLE_API_KEY")

        if not api_key:
            print("❌ GOOGLE_API_KEY not found in environment")
            return False

        genai.configure(api_key=api_key)

        # Test Gemini 2.0 model
        model = genai.GenerativeModel('gemini-2.0-flash-exp')
        response = model.generate_content("Hello, this is a test. Please respond with 'Test successful'.")

        if response.text:
            print("✅ Gemini 2.0 model accessible")
            print(f"   Response: {response.text}")
            return True
        else:
            print("❌ Gemini 2.0 model returned empty response")
            return False

    except Exception as e:
        print(f"❌ Gemini 2.0 model test failed: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing Smart ATS API with Gemini 2.0")
    print("=" * 60)

    # Test Gemini model first
    print("1. Testing Gemini 2.0 Model Access...")
    gemini_ok = test_gemini_model()
    print()

    # Test health check
    print("2. Testing API Health Check...")
    health_ok = test_health_check()
    print()

    # Test analyze endpoint
    print("3. Testing Analyze Endpoint...")
    analyze_ok = test_analyze_endpoint()
    print()

    print("=" * 60)
    print("📊 TEST RESULTS:")
    print(f"Gemini 2.0 Model: {'✅ PASS' if gemini_ok else '❌ FAIL'}")
    print(f"Health Check: {'✅ PASS' if health_ok else '❌ FAIL'}")
    print(f"Analyze Endpoint: {'✅ PASS' if analyze_ok else '❌ FAIL'}")

    if all([gemini_ok, health_ok, analyze_ok]):
        print("\n🎉 All tests passed! API is ready for frontend integration.")
    else:
        print("\n⚠️  Some tests failed. Check the issues above.")
        if not gemini_ok:
            print("   - Verify GOOGLE_API_KEY is set correctly")
            print("   - Check Google AI Studio for API access")
        if not health_ok:
            print("   - Make sure Flask app is running on localhost:5000")
        if not analyze_ok:
            print("   - Check Flask app logs for detailed error information")
