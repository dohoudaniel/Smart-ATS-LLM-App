# Smart ATS Deployment Guide

This guide covers deploying both the frontend (React) and backend (Flask API) components of the Smart ATS application.

## Backend Deployment (Flask API)

### Prerequisites
- Python 3.11+
- Google Gemini AI API key

### Deploy to Render.com

1. **Create a new Web Service on Render**
   - Connect your GitHub repository
   - Select the `Smart-ATS-LLM-App` directory as the root

2. **Configure Build Settings**
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn app:app`

3. **Set Environment Variables**
   ```
   GOOGLE_API_KEY=your_google_gemini_api_key
   PORT=5000
   PYTHON_VERSION=3.11.0
   ```

4. **Deploy**
   - The service will be available at: `https://your-app-name.onrender.com`

### Deploy to Heroku

1. **Install Heroku CLI and login**
   ```bash
   heroku login
   ```

2. **Create Heroku app**
   ```bash
   cd Smart-ATS-LLM-App
   heroku create your-app-name
   ```

3. **Set environment variables**
   ```bash
   heroku config:set GOOGLE_API_KEY=your_google_gemini_api_key
   ```

4. **Deploy**
   ```bash
   git add .
   git commit -m "Deploy to Heroku"
   git push heroku main
   ```

## Frontend Deployment (React App)

### Prerequisites
- Node.js 18+
- Backend API URL

### Deploy to Vercel

1. **Install Vercel CLI**
   ```bash
   npm i -g vercel
   ```

2. **Configure Environment Variables**
   Create `.env.production`:
   ```
   VITE_API_URL=https://your-backend-url.onrender.com
   ```

3. **Deploy**
   ```bash
   cd Smart_ATS
   vercel --prod
   ```

### Deploy to Netlify

1. **Build the project**
   ```bash
   cd Smart_ATS
   npm run build
   ```

2. **Deploy to Netlify**
   - Upload the `dist` folder to Netlify
   - Set environment variable: `VITE_API_URL=https://your-backend-url.onrender.com`

## Local Development Setup

### Backend
```bash
cd Smart-ATS-LLM-App
pip install -r requirements.txt
cp .env.example .env
# Edit .env and add your GOOGLE_API_KEY
python app.py
```

### Frontend
```bash
cd Smart_ATS
npm install
cp .env.example .env
# Edit .env and set VITE_API_URL to your backend URL
npm run dev
```

## Testing the Integration

1. **Test Backend Health**
   ```bash
   curl https://your-backend-url.onrender.com/
   ```

2. **Test Frontend**
   - Open the frontend URL
   - Upload a PDF resume
   - Enter a job description
   - Click "Analyze Resume"

## Troubleshooting

### Common Issues

1. **CORS Errors**
   - Ensure the backend CORS configuration includes your frontend domain
   - Check that the API URL in frontend matches the deployed backend

2. **File Upload Issues**
   - Verify PDF file size is under 16MB
   - Check that the file is a valid PDF

3. **AI API Errors**
   - Verify GOOGLE_API_KEY is set correctly
   - Check API quota and billing status

4. **Timeout Issues**
   - AI processing can take 30-60 seconds
   - Ensure frontend timeout is set appropriately (currently 2 minutes)

### Environment Variables Checklist

**Backend:**
- ✅ GOOGLE_API_KEY
- ✅ PORT (optional, defaults to 5000)

**Frontend:**
- ✅ VITE_API_URL

## Security Considerations

1. **API Keys**
   - Never commit API keys to version control
   - Use environment variables for all sensitive data

2. **CORS**
   - In production, restrict CORS origins to your frontend domain
   - Currently set to allow all origins (`*`) for development

3. **File Upload**
   - File size limited to 16MB
   - Only PDF files accepted
   - Files are processed in memory and not stored

## Performance Optimization

1. **Backend**
   - Consider implementing caching for repeated analyses
   - Add request rate limiting
   - Optimize PDF text extraction

2. **Frontend**
   - Implement proper loading states
   - Add retry mechanisms for failed requests
   - Consider adding offline support

## Monitoring

1. **Backend Logs**
   - Monitor application logs for errors
   - Track API response times
   - Monitor AI API usage and costs

2. **Frontend**
   - Monitor user interactions
   - Track successful vs failed analyses
   - Monitor page load times
