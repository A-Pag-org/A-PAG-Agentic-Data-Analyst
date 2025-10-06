# 📸 Visual Step-by-Step Walkthrough

## 🎯 Your Complete Guide to Using the AI Data Analytics Platform

---

## 🔧 Setup Phase

### Step 1: Install Dependencies ✅ COMPLETED
```bash
# Frontend dependencies installed
✅ 693 packages installed
✅ No vulnerabilities found
```

### Step 2: Configure Environment Variables
You need to create two files:

#### File 1: `.env` (Backend - in root directory)
```bash
# Copy the template
cp .env.example .env

# Then edit .env with your text editor and add:
```

```env
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
DATABASE_URL=postgresql://postgres:password@xxxxx.supabase.co:5432/postgres
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxxxxx
```

**Where to get these:**
- Supabase credentials → https://app.supabase.com → Your Project → Settings → API
- OpenAI API key → https://platform.openai.com/api-keys

#### File 2: `frontend/.env.local` (Frontend)
```bash
# Copy the template
cp frontend/.env.local.example frontend/.env.local

# Then edit frontend/.env.local:
```

```env
NEXT_PUBLIC_SUPABASE_URL=https://xxxxx.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
NEXT_PUBLIC_BACKEND_URL=http://localhost:8000
```

### Step 3: Start the Application

#### Terminal 1: Start Backend
```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**You should see:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

✅ **Success!** Backend is running at http://localhost:8000

#### Terminal 2: Start Frontend
```bash
cd frontend
npm run dev
```

**You should see:**
```
▲ Next.js 15.5.4
- Local:        http://localhost:3000
- Environments: .env.local

✓ Starting...
✓ Ready in 2.3s
```

✅ **Success!** Frontend is running at http://localhost:3000

---

## 📱 Using the Application

### The Main Dashboard

When you open http://localhost:3000, you'll see:

```
┌─────────────────────────────────────────────────┐
│ 📊 AI Data Analytics              🌙 [Dark Mode]│
├─────────────────────────────────────────────────┤
│                                                   │
│  AI-Powered Data Analytics Platform               │
│  Upload your data, ask questions, and get        │
│  intelligent insights with visualizations         │
│                                                   │
│  ┌─────────────────────────────────────────┐    │
│  │ 📊 Analyze Data │ 📁 Upload Data │ 📖 Guide│ │
│  └─────────────────────────────────────────┘    │
│                                                   │
└─────────────────────────────────────────────────┘
```

---

## 📁 Tab 1: Upload Data

### What You'll See:

```
┌─────────────────────────────────────────────────┐
│ ℹ️  Upload CSV, Excel, or JSON files            │
│    to analyze your data                          │
├─────────────────────────────────────────────────┤
│                                                   │
│ User ID *                                         │
│ ┌─────────────────────────────────────────┐     │
│ │ demo-user                                │     │
│ └─────────────────────────────────────────┘     │
│                                                   │
│ Select File *                                     │
│ ┌─────────────────────────────────────────┐     │
│ │ [Choose File] sales_data.csv             │     │
│ └─────────────────────────────────────────┘     │
│                                                   │
│     ┌─────────────────────┐                     │
│     │   Upload Data        │                     │
│     └─────────────────────┘                     │
│                                                   │
└─────────────────────────────────────────────────┘
```

### Steps:
1. **Enter User ID**: Type `demo-user` (or any ID you prefer)
2. **Click "Choose File"**: Select your data file
   - ✅ Supported: `.csv`, `.xlsx`, `.xls`, `.json`
   - 📊 Example: sales_data.csv, customers.xlsx, metrics.json
3. **Click "Upload Data"**: Wait for confirmation

### Success Message:
```
┌─────────────────────────────────────────┐
│ ✅ Upload Successful                     │
│ File uploaded successfully.              │
│ 1,234 chunks created.                    │
└─────────────────────────────────────────┘
```

---

## 🔍 Tab 2: Analyze Data

### What You'll See:

```
┌─────────────────────────────────────────────────┐
│ User ID *                                         │
│ ┌─────────────────────────────────────────┐     │
│ │ demo-user                                │     │
│ └─────────────────────────────────────────┘     │
│                                                   │
│ Your Question *                                   │
│ ┌─────────────────────────────────────────┐     │
│ │ What are the top 5 products by revenue? │     │
│ │                                          │     │
│ │                                          │     │
│ └─────────────────────────────────────────┘     │
│                                                   │
│ ☑️ Generate Visualizations                       │
│ ☑️ Include Forecasting                           │
│                                                   │
│     ┌─────────────────────┐                     │
│     │   Analyze Data       │                     │
│     └─────────────────────┘                     │
└─────────────────────────────────────────────────┘
```

### Steps:
1. **Enter User ID**: Same as you used for upload (`demo-user`)
2. **Type Your Question**: Ask in natural language
   - "What are the top 5 products by revenue?"
   - "Show me sales trends over time"
   - "Which customers bought the most?"
3. **Check Options**:
   - ✅ **Generate Visualizations** - Get charts and graphs
   - ✅ **Include Forecasting** - Get predictions (for time-series data)
4. **Click "Analyze Data"**: Wait for AI to process

### While Processing:
```
┌─────────────────────────────────────────┐
│           ⌛ (Spinning)                  │
│     Analyzing your data with AI...       │
└─────────────────────────────────────────┘
```

### Results Display:

```
┌─────────────────────────────────────────────────┐
│ Analysis Results                                  │
├─────────────────────────────────────────────────┤
│                                                   │
│ ℹ️  Answer                                       │
│ Based on your data, the top 5 products by        │
│ revenue are:                                      │
│ 1. Product A - $125,000                          │
│ 2. Product B - $98,500                           │
│ 3. Product C - $87,200                           │
│ 4. Product D - $76,300                           │
│ 5. Product E - $65,100                           │
│                                                   │
├─────────────────────────────────────────────────┤
│                                                   │
│ 📊 Visualization                                 │
│                                                   │
│  Revenue by Product                               │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━       │
│  Product A ████████████████████ $125K            │
│  Product B ███████████████ $98K                  │
│  Product C █████████████ $87K                    │
│  Product D ███████████ $76K                      │
│  Product E ██████████ $65K                       │
│                                                   │
│  💡 Key Insights:                                │
│  • Product A accounts for 28% of total revenue   │
│  • Top 3 products drive 70% of revenue           │
│  • Clear concentration in premium products       │
│                                                   │
└─────────────────────────────────────────────────┘
```

---

## 📖 Tab 3: Guide

### What You'll See:

```
┌─────────────────────────────────────────────────┐
│ 📚 How to Use This App                           │
├─────────────────────────────────────────────────┤
│                                                   │
│ Step 1: Upload Your Data                         │
│ Go to the "Upload Data" tab and upload your      │
│ CSV, Excel, or JSON file...                      │
│                                                   │
│ Step 2: Ask Questions                            │
│ Switch to the "Analyze Data" tab and ask         │
│ questions about your data in natural language... │
│                                                   │
│ Step 3: Get Insights                             │
│ The AI will analyze your data and provide:       │
│ ✅ Natural language answers                      │
│ 📊 Interactive visualizations                    │
│ 📈 Forecasts (when enabled)                      │
│ 💡 Data insights                                 │
│                                                   │
│ ✅ Pro Tip!                                      │
│ Enable "Generate Visualizations" for charts      │
│ and graphs, and "Include Forecasting" for        │
│ predictive analytics.                            │
│                                                   │
└─────────────────────────────────────────────────┘
```

---

## 💬 Example Queries to Try

### 📊 Basic Analytics
```
Query: "Summarize this dataset"
Expected: Overview statistics, row counts, column info

Query: "What are the column names?"
Expected: List of all columns in your data

Query: "Show me the first 5 rows"
Expected: Sample data preview
```

### 📈 Sales & Revenue
```
Query: "What are the top 5 products by revenue?"
Expected: Ranked list with revenue values + bar chart

Query: "Show sales trends over the last 6 months"
Expected: Time series analysis + line chart

Query: "Compare Q1 vs Q2 revenue"
Expected: Comparison + bar/line chart
```

### 👥 Customer Analytics
```
Query: "Who are my top 10 customers?"
Expected: Customer list sorted by value + table/chart

Query: "What's the average order value?"
Expected: Calculated metric + distribution chart

Query: "Show customer distribution by region"
Expected: Geographic breakdown + pie/bar chart
```

### 🔮 Forecasting (Enable "Include Forecasting")
```
Query: "Predict next month's sales"
Expected: Forecast values + confidence intervals + chart

Query: "What will revenue be in Q4?"
Expected: Quarterly forecast + trend analysis

Query: "Forecast customer growth for next quarter"
Expected: Growth prediction + visualization
```

### 🔍 Data Exploration
```
Query: "Find any anomalies in the data"
Expected: Outlier detection + highlighted values

Query: "Show correlations between columns"
Expected: Correlation matrix + heatmap

Query: "What patterns do you see?"
Expected: AI-discovered insights
```

---

## 🎨 UI Features

### Toast Notifications
```
┌─────────────────────────┐
│ ✅ Upload Successful     │
│ File uploaded            │
│ successfully             │
└─────────────────────────┘

┌─────────────────────────┐
│ ⚠️  Missing Information  │
│ Please enter a query     │
└─────────────────────────┘

┌─────────────────────────┐
│ ❌ Analysis Failed       │
│ No data found for this   │
│ user ID                  │
└─────────────────────────┘
```

### Dark Mode Toggle
- Click the 🌙 (moon) icon → Switch to dark mode
- Click the ☀️ (sun) icon → Switch to light mode
- Preference saved automatically

---

## 📊 Sample Data Formats

### CSV Example (`sales_data.csv`)
```csv
date,product,revenue,quantity,region
2024-01-01,Widget A,1000,50,North
2024-01-01,Widget B,1500,75,South
2024-01-02,Widget A,1200,60,East
2024-01-02,Widget C,800,40,West
```

### Excel Example (`customers.xlsx`)
| customer_id | name        | total_purchases | lifetime_value | join_date  |
|-------------|-------------|-----------------|----------------|------------|
| C001        | Acme Corp   | 45              | 125000         | 2023-01-15 |
| C002        | TechStart   | 32              | 98000          | 2023-02-20 |
| C003        | DataFlow    | 28              | 87000          | 2023-03-10 |

### JSON Example (`metrics.json`)
```json
[
  {
    "timestamp": "2024-01-01T00:00:00Z",
    "metric": "revenue",
    "value": 15000,
    "category": "sales"
  },
  {
    "timestamp": "2024-01-01T00:00:00Z",
    "metric": "orders",
    "value": 234,
    "category": "sales"
  }
]
```

---

## ✅ Success Checklist

Before asking your first question, make sure:

- [ ] ✅ Backend running (Terminal 1 shows "Uvicorn running")
- [ ] ✅ Frontend running (Terminal 2 shows "Ready")
- [ ] ✅ Browser open to http://localhost:3000
- [ ] ✅ Data uploaded successfully (green toast notification)
- [ ] ✅ Same User ID used for upload and analysis
- [ ] ✅ "Generate Visualizations" enabled (for charts)
- [ ] ✅ Question is clear and specific

---

## 🎯 First-Time User Workflow

### Complete Example: Analyzing Sales Data

#### 1️⃣ Prepare Your Data
```bash
# Create a sample CSV file
echo "date,product,revenue
2024-01-01,Product A,1000
2024-01-02,Product B,1500
2024-01-03,Product A,1200" > sample_sales.csv
```

#### 2️⃣ Upload
- Tab: **Upload Data**
- User ID: `test-user`
- File: `sample_sales.csv`
- Click: **Upload Data**
- Wait for: ✅ Success message

#### 3️⃣ Analyze
- Tab: **Analyze Data**
- User ID: `test-user`
- Question: `What is the total revenue?`
- Enable: ✅ Generate Visualizations
- Click: **Analyze Data**

#### 4️⃣ Review Results
- Read the AI answer
- View the visualization
- Check insights
- Try another question!

---

## 🚀 You're Ready!

Your application is now fully set up and ready to use. Start with:

1. **Upload** your first dataset
2. **Ask** a simple question
3. **Explore** the visualizations
4. **Experiment** with different queries
5. **Export** your results

**Have fun analyzing! 📊✨**

---

## 📞 Quick Help

### Something not working?

**Check Backend:**
```bash
# Should see "Uvicorn running on http://0.0.0.0:8000"
curl http://localhost:8000/api/v1/health
```

**Check Frontend:**
```bash
# Should return HTML
curl http://localhost:3000
```

**Check Environment:**
```bash
# Backend
cat .env | grep -v "^#" | grep .

# Frontend
cat frontend/.env.local | grep -v "^#" | grep .
```

**Still stuck?** Check [SETUP_GUIDE.md](SETUP_GUIDE.md) or [QUICK_REFERENCE.md](QUICK_REFERENCE.md)

