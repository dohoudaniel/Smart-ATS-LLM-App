from flask import Flask, request, jsonify
from flask_cors import CORS
import google.generativeai as genai
import os
import PyPDF2 as pdf
from dotenv import load_dotenv
import json
import io
import logging
from werkzeug.utils import secure_filename
from werkzeug.exceptions import RequestEntityTooLarge

# Load environment variables
load_dotenv()

# Configure Gemini AI
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Initialize Flask app
app = Flask(__name__)

# Configure CORS with specific settings
CORS(app,
     origins=['*'],  # Allow all origins for now, restrict in production
     methods=['GET', 'POST', 'OPTIONS'],
     allow_headers=['Content-Type', 'Authorization'],
     supports_credentials=False)

# Configure Flask
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Error handlers
@app.errorhandler(413)
def too_large(e):
    return jsonify({'error': 'File too large. Maximum size is 16MB.'}), 413

@app.errorhandler(400)
def bad_request(e):
    return jsonify({'error': 'Bad request. Please check your input.'}), 400

@app.errorhandler(500)
def internal_error(e):
    logger.error(f"Internal server error: {str(e)}")
    return jsonify({'error': 'Internal server error. Please try again later.'}), 500

def get_gemini_response(input_text):
    """Get response from Gemini AI model"""
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(input_text)
        return response.text
    except Exception as e:
        raise Exception(f"AI model error: {str(e)}")

def extract_pdf_text(file_stream):
    """Extract text from PDF file"""
    try:
        reader = pdf.PdfReader(file_stream)
        text = ""
        for page in reader.pages:
            text += str(page.extract_text())
        return text
    except Exception as e:
        raise Exception(f"PDF processing error: {str(e)}")

def parse_ai_response(response_text):
    """Parse the AI response and extract structured data"""
    try:
        # Clean the response text
        response_text = response_text.strip()

        # Try to find JSON-like structure in the response
        start_idx = response_text.find('{')
        end_idx = response_text.rfind('}') + 1

        if start_idx != -1 and end_idx != -1:
            json_str = response_text[start_idx:end_idx]
            # Replace single quotes with double quotes for valid JSON
            json_str = json_str.replace("'", '"')
            parsed_data = json.loads(json_str)

            return {
                'jd_match': parsed_data.get('JD Match', '0%'),
                'missing_keywords': parsed_data.get('MissingKeywords', []),
                'profile_summary': parsed_data.get('Profile Summary', 'No summary available')
            }
        else:
            # Fallback parsing if JSON structure is not found
            return {
                'jd_match': '0%',
                'missing_keywords': [],
                'profile_summary': response_text
            }
    except Exception as e:
        # Return default structure if parsing fails
        return {
            'jd_match': '0%',
            'missing_keywords': [],
            'profile_summary': f'Error parsing response: {str(e)}'
        }

# Prompt template
input_prompt = """
Hey Act Like a skilled or very experience ATS(Application Tracking System)
with a deep understanding of tech field,software engineering,data science ,data analyst
and big data engineer. Your task is to evaluate the resume based on the given job description.
You must consider the job market is very competitive and you should provide
best assistance for improving the resumes. Assign the percentage Matching based
on JD and the missing keywords with high accuracy
resume:{text}
description:{jd}

I want the response in one single string having the structure
{{"JD Match":"%","MissingKeywords":[],"Profile Summary":""}}
"""

@app.route('/', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'message': 'Smart ATS API is running',
        'version': '1.0.0'
    })

@app.route('/analyze', methods=['POST'])
def analyze_resume():
    """Analyze resume against job description"""
    try:
        logger.info("Received resume analysis request")

        # Check if required fields are present
        if 'job_description' not in request.form:
            logger.warning("Job description missing from request")
            return jsonify({'error': 'Job description is required'}), 400

        if 'resume' not in request.files:
            logger.warning("Resume file missing from request")
            return jsonify({'error': 'Resume file is required'}), 400

        job_description = request.form['job_description']
        resume_file = request.files['resume']

        logger.info(f"Processing resume: {resume_file.filename}")

        # Validate inputs
        if not job_description.strip():
            logger.warning("Empty job description provided")
            return jsonify({'error': 'Job description cannot be empty'}), 400

        if resume_file.filename == '':
            logger.warning("No resume file selected")
            return jsonify({'error': 'No resume file selected'}), 400

        if not resume_file.filename.lower().endswith('.pdf'):
            logger.warning(f"Invalid file type: {resume_file.filename}")
            return jsonify({'error': 'Only PDF files are supported'}), 400

        # Extract text from PDF
        logger.info("Extracting text from PDF")
        resume_text = extract_pdf_text(resume_file.stream)

        if not resume_text.strip():
            logger.error("Failed to extract text from PDF")
            return jsonify({'error': 'Could not extract text from PDF. Please ensure the PDF contains readable text.'}), 400

        logger.info(f"Extracted {len(resume_text)} characters from PDF")

        # Prepare prompt for AI
        formatted_prompt = input_prompt.format(
            text=resume_text,
            jd=job_description
        )

        # Get AI response
        logger.info("Sending request to AI model")
        ai_response = get_gemini_response(formatted_prompt)
        logger.info("Received response from AI model")

        # Parse the response
        parsed_response = parse_ai_response(ai_response)
        logger.info("Successfully parsed AI response")

        return jsonify(parsed_response)

    except Exception as e:
        logger.error(f"Error in analyze_resume: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)