# Smart ATS Backend API

Smart ATS Backend is a Flask-based REST API designed to evaluate resumes against job descriptions using Google Generative AI. The API provides endpoints for analyzing resumes and returning structured data about job matching, missing keywords, and profile summaries.

## Features
- **REST API Endpoints:** RESTful API for resume analysis
- **PDF Processing:** Extract text from PDF resumes
- **AI-Powered Analysis:** Uses Google Gemini AI for intelligent matching
- **Job Description Matching:** Analyzes alignment between resume and job requirements
- **Keyword Analysis:** Identifies missing keywords for ATS optimization
- **Profile Summary:** Generates comprehensive resume summaries
- **CORS Support:** Cross-origin requests enabled for frontend integration

## Technologies Used
- **Flask**: Web framework for creating REST API
- **Flask-CORS**: Cross-origin resource sharing support
- **Google Generative AI (Gemini 2.0)**: Latest AI model for intelligent resume analysis
- **PyPDF2**: PDF text extraction and processing
- **python-dotenv**: Environment variable management
- **Gunicorn**: WSGI HTTP server for production deployment

## Installation

### Prerequisites
Ensure you have Python installed on your machine. Then, clone the repository and install the necessary dependencies.

1. Clone the repository:

   ```bash
   git clone https://github.com/your-repository-url
   ```

2. Navigate to the project directory:

   ```bash
   cd your-project-directory
   ```

3. Set up a virtual environment (optional but recommended):

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

4. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

### Environment Setup
Create a `.env` file in the project root directory and add your Google API key:

```bash
GOOGLE_API_KEY=your_google_api_key
```

### Run the Application

#### Option 1: Using the startup script (Recommended)
```bash
python start_server.py
```

#### Option 2: Direct execution
```bash
python app.py
```

The API will be available at `http://localhost:5000`

#### Testing the API
```bash
python test_api.py
```

## API Endpoints

### Health Check
- **GET** `/`
- **Response:**
  ```json
  {
    "status": "healthy",
    "message": "Smart ATS API is running",
    "version": "1.0.0"
  }
  ```

### Analyze Resume
- **POST** `/analyze`
- **Content-Type:** `multipart/form-data`
- **Form Data:**
  - `job_description`: Job description text (required)
  - `resume`: PDF file (required)
- **Response:**
  ```json
  {
    "jd_match": "85%",
    "missing_keywords": ["python", "docker", "kubernetes"],
    "profile_summary": "Experienced software developer with strong background in web development..."
  }
  ```

## Usage

Send a POST request to `/analyze` with:
1. **job_description**: The job posting text
2. **resume**: PDF file of the candidate's resume

The API will return structured analysis data including match percentage, missing keywords, and profile summary.

## Example

Here’s an example of how the app generates responses:

```
{
   "JD Match": "85%",
   "MissingKeywords": ["Python", "Data Science", "Machine Learning"],
   "Profile Summary": "The resume is strong in software engineering but lacks significant keywords related to data science..."
}
```

## Project Structure

- **`app.py`**: The main application file that handles the logic and interaction with Streamlit and Google Generative AI.
- **`requirements.txt`**: A list of Python dependencies required for the project.
- **`.env`**: Stores sensitive environment variables, such as API keys (not included in the repository for security reasons).

## Acknowledgements
Special thanks to the open-source libraries and tools that made this project possible: Streamlit, Google Generative AI, PyPDF2, and Python Dotenv.

