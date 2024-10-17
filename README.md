# Austin's Smart ATS

Austin's Smart ATS is a Streamlit web application designed to evaluate resumes against job descriptions using Google Generative AI. The tool mimics the functionality of an ATS (Application Tracking System) and provides insights into how well a resume matches a job description by analyzing keywords and profile summaries, with recommendations for improvements.

## Features
- **Upload Resume:** Upload a PDF resume for analysis.
- **Job Description Matching:** Paste the job description to evaluate how well the resume aligns with the role.
- **Keyword Matching:** The system identifies missing keywords crucial for optimizing the resume for ATS.
- **Profile Summary:** Summarizes the key strengths of the resume and areas for improvement based on the job description.

## Technologies Used
- **Streamlit**: For creating the web application interface.
- **Google Generative AI**: Powering the intelligent analysis of resumes and job descriptions.
- **PyPDF2**: Extracts text from PDF resumes for analysis.
- **python-dotenv**: Loads environment variables for API key management.

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
To launch the Streamlit app, run the following command:

```bash
streamlit run app.py
```

## Usage

1. **Job Description**: Paste the job description into the provided text area.
2. **Upload Resume**: Upload your resume in PDF format.
3. **Analyze**: Click the "Submit" button to get a detailed analysis. The app will generate:
   - A percentage match between the resume and job description.
   - A list of missing keywords.
   - A profile summary with insights into strengths and areas for improvement.

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

