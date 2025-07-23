from flask import Flask, request, jsonify
from flask_cors import CORS
import google.generativeai as genai
import os
import PyPDF2 as pdf
from dotenv import load_dotenv
import json
import io
import logging
import time
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
        # Use Gemini 2.0 Flash model
        model = genai.GenerativeModel('gemini-2.0-flash-exp')

        # Configure generation parameters for better consistency
        generation_config = genai.types.GenerationConfig(
            temperature=0.1,  # Lower temperature for more consistent responses
            top_p=0.8,
            top_k=40,
            max_output_tokens=1000,
        )

        response = model.generate_content(
            input_text,
            generation_config=generation_config
        )

        if not response.text:
            raise Exception("Empty response from AI model")

        logger.info(f"AI Response received: {len(response.text)} characters")
        return response.text

    except Exception as e:
        logger.error(f"AI model error: {str(e)}")
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
        logger.info(f"Parsing AI response: {response_text[:200]}...")

        # Clean the response text
        response_text = response_text.strip()

        # Remove any markdown code blocks if present
        if response_text.startswith('```json'):
            response_text = response_text.replace('```json', '').replace('```', '').strip()
        elif response_text.startswith('```'):
            response_text = response_text.replace('```', '').strip()

        # Try to find JSON structure in the response
        start_idx = response_text.find('{')
        end_idx = response_text.rfind('}') + 1

        if start_idx != -1 and end_idx != -1:
            json_str = response_text[start_idx:end_idx]
            logger.info(f"Extracted JSON string: {json_str}")

            # Try to parse as JSON
            try:
                parsed_data = json.loads(json_str)
            except json.JSONDecodeError:
                # If JSON parsing fails, try to fix common issues
                json_str = json_str.replace("'", '"')  # Replace single quotes
                json_str = json_str.replace('""', '"')  # Fix double quotes
                parsed_data = json.loads(json_str)

            # Extract data with fallbacks
            jd_match = parsed_data.get('JD Match', parsed_data.get('jd_match', '0%'))
            missing_keywords = parsed_data.get('MissingKeywords', parsed_data.get('missing_keywords', []))
            profile_summary = parsed_data.get('Profile Summary', parsed_data.get('profile_summary', 'No summary available'))

            # Ensure missing_keywords is a list
            if isinstance(missing_keywords, str):
                missing_keywords = [kw.strip() for kw in missing_keywords.split(',') if kw.strip()]

            result = {
                'jd_match': str(jd_match),
                'missing_keywords': missing_keywords,
                'profile_summary': str(profile_summary)
            }

            logger.info(f"Successfully parsed response: {result}")
            return result

        else:
            logger.warning("No JSON structure found in response")
            # Fallback parsing if JSON structure is not found
            return {
                'jd_match': '0%',
                'missing_keywords': [],
                'profile_summary': response_text[:500] + "..." if len(response_text) > 500 else response_text
            }

    except Exception as e:
        logger.error(f"Error parsing AI response: {str(e)}")
        # Return default structure if parsing fails
        return {
            'jd_match': '0%',
            'missing_keywords': [],
            'profile_summary': f'Error parsing response: {str(e)}'
        }

# Improved prompt template for Gemini 2.0
input_prompt = """
You are an expert ATS (Application Tracking System) analyzer with deep knowledge in technology, software engineering, data science, and data analytics.

Your task is to analyze a resume against a job description and provide a detailed evaluation.

RESUME TEXT:
{text}

JOB DESCRIPTION:
{jd}

Please analyze the resume and provide your response in the following EXACT JSON format (no additional text before or after):

{{
  "JD Match": "XX%",
  "MissingKeywords": ["keyword1", "keyword2", "keyword3"],
  "Profile Summary": "Detailed analysis of the candidate's profile, strengths, and areas for improvement based on the job requirements."
}}

Instructions:
1. Calculate a percentage match (0-100%) based on how well the resume aligns with the job requirements
2. Identify 3-8 important missing keywords that would improve the resume's ATS score
3. Provide a comprehensive profile summary (2-3 sentences) highlighting strengths and improvement areas
4. Respond ONLY with the JSON object, no additional text
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

        # Get AI response with retry mechanism
        logger.info("Sending request to AI model")
        max_retries = 2
        ai_response = None

        for attempt in range(max_retries + 1):
            try:
                ai_response = get_gemini_response(formatted_prompt)
                logger.info(f"Received response from AI model (attempt {attempt + 1})")
                break
            except Exception as ai_error:
                logger.warning(f"AI request attempt {attempt + 1} failed: {str(ai_error)}")
                if attempt == max_retries:
                    # If all retries failed, return a fallback response
                    logger.error("All AI request attempts failed, returning fallback response")
                    return jsonify({
                        'jd_match': '50%',
                        'missing_keywords': ['Unable to analyze - AI service unavailable'],
                        'profile_summary': f'Analysis temporarily unavailable due to AI service issues. Resume contains {len(resume_text)} characters of text. Please try again later.'
                    })
                time.sleep(1)  # Wait 1 second before retry

        if not ai_response:
            logger.error("No AI response received after retries")
            return jsonify({
                'jd_match': '0%',
                'missing_keywords': ['Analysis failed'],
                'profile_summary': 'Unable to analyze resume at this time. Please try again later.'
            }), 500

        # Parse the response
        parsed_response = parse_ai_response(ai_response)
        logger.info("Successfully parsed AI response")

        # Validate the parsed response
        if not parsed_response.get('jd_match') or parsed_response.get('jd_match') == '0%':
            logger.warning("Received low-quality response, adding fallback data")
            if not parsed_response.get('profile_summary') or 'Error' in parsed_response.get('profile_summary', ''):
                parsed_response['profile_summary'] = f"Resume analysis completed. The document contains {len(resume_text)} characters of professional content."

        return jsonify(parsed_response)

    except Exception as e:
        logger.error(f"Error in analyze_resume: {str(e)}")
        return jsonify({
            'error': str(e),
            'jd_match': '0%',
            'missing_keywords': [],
            'profile_summary': 'An error occurred during analysis. Please try again.'
        }), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)