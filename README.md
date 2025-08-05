# Smart ATS - Backend API

A comprehensive Flask-based backend API for the Smart ATS resume analysis application. This backend provides AI-powered resume analysis, user authentication, and review management with MongoDB integration.

## 🚀 Features

### Core Functionality

- **AI-Powered Resume Analysis**: Uses Google Gemini 2.0 Flash for intelligent resume evaluation
- **PDF Processing**: Extracts text from PDF resumes for analysis
- **Job Matching**: Compares resumes against job descriptions with percentage matching
- **Keyword Analysis**: Identifies missing keywords to improve ATS compatibility

### Authentication & User Management

- **JWT Authentication**: Secure token-based authentication system
- **User Registration**: Complete signup flow with validation
- **User Login**: Secure authentication with password hashing
- **Profile Management**: Update user information and settings
- **Password Security**: Bcrypt hashing for secure password storage

### Review Management

- **Review Storage**: Save analysis results to MongoDB
- **Review History**: Track user's previous resume analyses
- **Statistics**: Generate user statistics and performance metrics
- **Search & Filter**: Search through review history
- **Data Export**: Export user data and analysis history

### Database Integration

- **MongoDB**: Robust NoSQL database for scalable data storage
- **User Collections**: Structured user data with profiles
- **Review Collections**: Comprehensive analysis result storage
- **Indexing**: Optimized database queries with proper indexing

## 🛠️ Tech Stack

- **Framework**: Flask 3.0.0
- **Database**: MongoDB with PyMongo
- **Authentication**: Flask-JWT-Extended
- **AI Service**: Google Generative AI (Gemini 2.0)
- **PDF Processing**: PyPDF2
- **Password Hashing**: Bcrypt
- **Validation**: Email-validator, Marshmallow
- **CORS**: Flask-CORS
- **Environment**: Python-dotenv

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
