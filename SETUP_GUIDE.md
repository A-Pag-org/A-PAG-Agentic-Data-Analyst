# 🚀 Setup Guide - AI Data Analytics Platform

This comprehensive guide will walk you through setting up and using the AI Data Analytics Platform.

## 📋 Table of Contents

1. [Prerequisites](#prerequisites)
2. [Installation](#installation)
3. [Configuration](#configuration)
4. [Running the Application](#running-the-application)
5. [Using the Platform](#using-the-platform)
6. [Troubleshooting](#troubleshooting)

---

## Prerequisites

Before you begin, ensure you have the following installed:

- **Node.js** (v18 or higher) - [Download here](https://nodejs.org/)
- **Python** (v3.9 or higher) - [Download here](https://www.python.org/)
- **pip** (Python package manager)
- **Supabase Account** - [Sign up free](https://supabase.com/)
- **OpenAI API Key** - [Get your key](https://platform.openai.com/api-keys)

---

## Installation

### Step 1: Clone the Repository

```bash
git clone <your-repo-url>
cd <repo-directory>
```

### Step 2: Install Frontend Dependencies

```bash
cd frontend
npm install
```

### Step 3: Install Backend Dependencies

```bash
cd ../backend
pip install -r requirements.txt
```

---

## Configuration

### Step 1: Set Up Supabase

1. **Create a Supabase Project:**
   - Go to [Supabase Dashboard](https://app.supabase.com/)
   - Click "New Project"
   - Fill in your project details

2. **Get Your Credentials:**
   - Go to Project Settings → API
   - Copy:
     - Project URL
     - `anon` public key
     - `service_role` secret key

3. **Get Database Connection String:**
   - Go to Project Settings → Database
   - Copy the connection string under "Connection string"

4. **Run Database Migrations:**
   ```bash
   # From project root
   cd supabase
   # Apply migrations to your Supabase database
   # You can use the Supabase CLI or SQL Editor
   ```

### Step 2: Configure Backend Environment

1. **Copy the example environment file:**
   ```bash
   cp .env.example .env
   ```

2. **Edit `.env` and add your credentials:**
   ```bash
   SUPABASE_URL=https://your-project.supabase.co
   SUPABASE_ANON_KEY=your-anon-key
   SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
   DATABASE_URL=postgresql://postgres:[password]@[host]/postgres
   OPENAI_API_KEY=sk-your-openai-api-key
   ```

### Step 3: Configure Frontend Environment

1. **Copy the example environment file:**
   ```bash
   cd frontend
   cp .env.local.example .env.local
   ```

2. **Edit `.env.local` and add your credentials:**
   ```bash
   NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
   NEXT_PUBLIC_SUPABASE_ANON_KEY=your-anon-key
   NEXT_PUBLIC_BACKEND_URL=http://localhost:8000
   ```

---

## Running the Application

### Option 1: Run Everything Together (Recommended for Development)

#### Terminal 1 - Start Backend:
```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

#### Terminal 2 - Start Frontend:
```bash
cd frontend
npm run dev
```

You should see:
```
▲ Next.js 15.5.4
- Local:        http://localhost:3000
```

### Option 2: Production Build

```bash
# Build frontend
cd frontend
npm run build
npm start

# Run backend with production settings
cd backend
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

---

## Using the Platform

### 🎯 Quick Start Tutorial

#### Step 1: Access the Application

1. Open your browser to [http://localhost:3000](http://localhost:3000)
2. You should see the main dashboard with three tabs:
   - 📊 **Analyze Data**
   - 📁 **Upload Data**
   - 📖 **Guide**

#### Step 2: Upload Your Data

1. Click on the **"Upload Data"** tab
2. Enter a User ID (e.g., `demo-user`)
3. Click **"Select File"** and choose your data file
   - Supported formats: CSV, Excel (.xlsx, .xls), JSON
4. Click **"Upload Data"**
5. Wait for the success message

**Example Data Files You Can Use:**
- Sales data with columns: date, product, revenue, quantity
- Customer data with columns: customer_id, name, purchases, total_spent
- Time series data with columns: timestamp, metric_name, value

#### Step 3: Ask Questions About Your Data

1. Go to the **"Analyze Data"** tab
2. Enter your User ID (same as used for upload)
3. Type your question in natural language, for example:
   ```
   What are the top 5 products by revenue?
   ```
   ```
   Show me sales trends for the last quarter
   ```
   ```
   Which customers have the highest lifetime value?
   ```
   ```
   Compare Q1 and Q2 performance
   ```

4. **Optional Settings:**
   - ✅ Check **"Generate Visualizations"** for charts and graphs
   - ✅ Check **"Include Forecasting"** for predictive analytics

5. Click **"Analyze Data"**

#### Step 4: View Results

After analysis completes, you'll see:

1. **Text Answer**: Natural language response to your question
2. **Interactive Visualizations**: Charts, graphs, and plots
3. **Insights**: Key findings and patterns
4. **Forecast Data**: Future predictions (if enabled)

#### Step 5: Export Results

- Use the export buttons on visualizations to download:
  - PNG images
  - PDF reports
  - Raw data

---

## 🎨 Features Overview

### 1. Natural Language Queries
Ask questions in plain English - no SQL or code required!

**Examples:**
```
✅ What were total sales last month?
✅ Show me the distribution of customer ages
✅ Find anomalies in the transaction data
✅ Predict next quarter's revenue
```

### 2. AI-Powered Analysis
- Automatic data understanding
- Context-aware responses
- Multi-step reasoning
- Smart visualizations

### 3. Interactive Visualizations
- Line charts for trends
- Bar charts for comparisons
- Pie charts for distributions
- Scatter plots for relationships
- Heatmaps for correlations

### 4. Forecasting
- Time series predictions
- Trend analysis
- Seasonality detection
- Confidence intervals

### 5. Data Export
- Download charts as images
- Export to PDF
- Raw data download
- Share insights

---

## 📊 Sample Queries by Use Case

### Sales Analytics
```
- What are my top selling products this month?
- Compare sales between Q1 and Q2
- Show revenue trends over the last year
- Which region has the highest sales growth?
```

### Customer Analytics
```
- Who are my top 10 customers by revenue?
- What's the average customer lifetime value?
- Show customer segmentation by purchase behavior
- Predict customer churn risk
```

### Financial Analytics
```
- What's the month-over-month revenue growth?
- Show expense breakdown by category
- Forecast next quarter's profit
- Identify cost-saving opportunities
```

### Operations Analytics
```
- What's the inventory turnover rate?
- Show order fulfillment time distribution
- Identify supply chain bottlenecks
- Predict stock requirements for next month
```

---

## 🔧 Troubleshooting

### Issue: "Upload failed"
**Solutions:**
- Verify your backend is running on port 8000
- Check that `NEXT_PUBLIC_BACKEND_URL` is set correctly
- Ensure your data file is in a supported format (CSV, Excel, JSON)
- Check backend logs for specific error messages

### Issue: "Analysis failed"
**Solutions:**
- Make sure you've uploaded data for this User ID
- Verify your OpenAI API key is valid and has credits
- Check that your Supabase database is accessible
- Ensure the query is clear and specific

### Issue: Backend won't start
**Solutions:**
- Check all required environment variables are set in `.env`
- Verify Python dependencies are installed: `pip install -r requirements.txt`
- Make sure port 8000 is not in use by another application
- Check Supabase credentials are correct

### Issue: Frontend won't start
**Solutions:**
- Ensure Node.js version is 18 or higher
- Run `npm install` in the frontend directory
- Check that `.env.local` has required variables
- Delete `.next` folder and restart: `rm -rf .next && npm run dev`

### Issue: No visualizations showing
**Solutions:**
- Make sure "Generate Visualizations" checkbox is enabled
- Verify your query asks for data that can be visualized
- Check browser console for JavaScript errors
- Try a different chart type or query

### Issue: Slow analysis
**Solutions:**
- Large datasets may take longer to process
- Complex queries require more AI processing time
- Check your OpenAI API rate limits
- Consider upgrading your OpenAI plan for faster responses

---

## 🛡️ Security Best Practices

1. **Never commit `.env` files** to version control
2. **Use environment-specific configurations** for dev/prod
3. **Rotate API keys regularly**
4. **Enable Supabase Row Level Security (RLS)** for production
5. **Use HTTPS** in production deployments
6. **Implement rate limiting** to prevent abuse
7. **Monitor API usage and costs**

---

## 📚 Additional Resources

- [Supabase Documentation](https://supabase.com/docs)
- [OpenAI API Documentation](https://platform.openai.com/docs)
- [Next.js Documentation](https://nextjs.org/docs)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)

---

## 💡 Pro Tips

1. **Start with simple queries** to understand the system
2. **Be specific in your questions** for better results
3. **Use consistent User IDs** to track your datasets
4. **Enable visualizations** for better insights
5. **Try forecasting** for time-series data
6. **Export and save** important analyses
7. **Review insights** for AI-discovered patterns

---

## 🆘 Need Help?

If you encounter issues not covered in this guide:

1. Check the backend logs in your terminal
2. Check the browser console for frontend errors
3. Verify all environment variables are set correctly
4. Review the API documentation at `http://localhost:8000/docs`
5. Create an issue in the repository with:
   - Error message
   - Steps to reproduce
   - Environment details (OS, Node version, Python version)

---

## 🎉 You're Ready!

You now have everything you need to use the AI Data Analytics Platform. Start by uploading a dataset and asking your first question!

**Happy Analyzing! 📊✨**
