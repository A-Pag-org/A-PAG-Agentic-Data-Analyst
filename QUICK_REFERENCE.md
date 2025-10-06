# 🚀 Quick Reference Guide

## Essential Commands

### Starting the Application
```bash
# Terminal 1 - Backend
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Terminal 2 - Frontend  
cd frontend
npm run dev
```

### Access Points
- **Frontend:** http://localhost:3000
- **Backend API:** http://localhost:8000
- **API Docs:** http://localhost:8000/docs

---

## Common Workflows

### 📁 Upload Data
1. Tab: **Upload Data**
2. User ID: `demo-user` (or your choice)
3. Select file (CSV/Excel/JSON)
4. Click "Upload Data"

### 🔍 Analyze Data
1. Tab: **Analyze Data**
2. User ID: Same as upload
3. Enter question
4. ✅ Enable "Generate Visualizations"
5. ✅ Enable "Include Forecasting" (optional)
6. Click "Analyze Data"

---

## Sample Questions by Category

### 📈 Sales Analytics
```
What are the top 5 products by revenue?
Show sales trends for Q1 vs Q2
What's the month-over-month growth rate?
```

### 👥 Customer Analytics
```
Who are my top 10 customers?
What's the average customer lifetime value?
Show customer distribution by region
```

### 📊 Data Exploration
```
Summarize the dataset
Show distribution of [column_name]
Find correlations in the data
Identify any anomalies or outliers
```

### 🔮 Forecasting
```
Predict next month's sales
What will revenue be in Q4?
Forecast customer growth for next quarter
```

---

## Troubleshooting Checklist

### ❌ Upload Fails
- [ ] Backend running on port 8000?
- [ ] File format correct (CSV/Excel/JSON)?
- [ ] File size reasonable (<100MB)?

### ❌ Analysis Fails  
- [ ] Data uploaded for this User ID?
- [ ] OpenAI API key set in `.env`?
- [ ] Query is clear and specific?
- [ ] Supabase database accessible?

### ❌ App Won't Start
- [ ] Dependencies installed? (`npm install`, `pip install -r requirements.txt`)
- [ ] Environment files configured? (`.env`, `.env.local`)
- [ ] Correct ports available? (3000, 8000)
- [ ] Credentials valid? (Supabase, OpenAI)

---

## Environment Variables Quick Check

### Backend (.env)
```bash
✅ SUPABASE_URL
✅ SUPABASE_ANON_KEY  
✅ SUPABASE_SERVICE_ROLE_KEY
✅ DATABASE_URL
✅ OPENAI_API_KEY
```

### Frontend (.env.local)
```bash
✅ NEXT_PUBLIC_SUPABASE_URL
✅ NEXT_PUBLIC_SUPABASE_ANON_KEY
✅ NEXT_PUBLIC_BACKEND_URL
```

---

## API Endpoints Reference

### Ingest
- `POST /api/v1/ingest/upload` - Upload data file

### Analysis  
- `POST /api/v1/agents/analyze` - Analyze data with AI

### Search
- `POST /api/v1/search` - Search uploaded data

### Export
- `POST /api/v1/export/pdf` - Export to PDF
- `POST /api/v1/export/image` - Export to image

### Forecasting
- `POST /api/v1/forecast` - Generate forecasts

### Health
- `GET /api/v1/health` - Check API status

---

## Keyboard Shortcuts

- `Ctrl/Cmd + K` - Focus search
- `Tab` - Switch between tabs
- `Enter` - Submit form

---

## Data Format Tips

### CSV Format
```csv
date,product,revenue,quantity
2024-01-01,Widget A,1000,50
2024-01-02,Widget B,1500,75
```

### Excel Format
- First row: Column headers
- Subsequent rows: Data
- Avoid merged cells

### JSON Format
```json
[
  {"date": "2024-01-01", "product": "Widget A", "revenue": 1000},
  {"date": "2024-01-02", "product": "Widget B", "revenue": 1500}
]
```

---

## Performance Tips

- 📊 Large datasets (>10k rows) may take 10-30 seconds
- 🔮 Forecasting adds 5-10 seconds to analysis
- 💾 Cache responses for repeated queries
- 🎯 Be specific in queries for faster results

---

## Best Practices

1. **Use consistent User IDs** across sessions
2. **Start with simple questions** to test
3. **Enable visualizations** for better insights
4. **Review AI insights** for discovered patterns
5. **Export important analyses** for later review
6. **Structure data properly** before upload
7. **Monitor API usage** to control costs

---

## Getting Help

1. **Check logs:**
   - Backend: Terminal running uvicorn
   - Frontend: Browser console (F12)

2. **Review documentation:**
   - [SETUP_GUIDE.md](SETUP_GUIDE.md) - Detailed setup
   - [README.md](README.md) - Project overview
   - http://localhost:8000/docs - API docs

3. **Common issues:**
   - Connection errors → Check backend is running
   - Auth errors → Verify environment variables
   - Slow responses → Check OpenAI API status

---

**💡 Pro Tip:** Keep this reference open while using the platform!
