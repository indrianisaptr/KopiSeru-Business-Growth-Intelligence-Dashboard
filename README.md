# 🏪 KopiSeru Business Intelligence Dashboard

Comprehensive Business Intelligence Dashboard untuk KopiSeru coffee chain, built with **Streamlit**, **Plotly**, dan **Groq AI**.

---

## 📊 Dashboard Features

### 7 Interactive Pages:

1. **📊 Executive Dashboard** - KPI overview dan ringkasan performa bisnis
2. **📈 Business Growth** - Revenue trends, transaction analysis, promotion impact
3. **💹 Profitability** - Margin analysis, cost structure, weekend profitability challenge
4. **🏪 Branch Performance** - Detailed branch & city rankings, channel mix analysis
5. **🎯 Expansion Opportunity** - Expansion score, saturation vs profitability matrix
6. **😊 Customer Insight** - Satisfaction drivers analysis, trend monitoring
7. **🤖 AI Business Analyst** - Interactive AI-powered insights & recommendations

### Key Capabilities:

✅ **Global Sidebar Filters** - Year, Month, City, Branch Type, Promotion, Weather, Channel, Weekday/Weekend
✅ **AI-Powered Analysis** - Groq LLaMA 3.3 70B integration for contextual insights
✅ **Interactive Charts** - Plotly visualizations with drill-down capabilities
✅ **Production-Ready** - Caching, error handling, responsive design
✅ **Modular Architecture** - Separated components, utils, and pages

---

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- pip or conda

### 1. Clone & Setup

```bash
# Clone repository
git clone <repo-url>
cd kopiseru-dashboard

# Create virtual environment (optional but recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Setup Groq API Key

```bash
# Create .streamlit directory
mkdir -p .streamlit

# Create secrets file
cp secrets.toml.example .streamlit/secrets.toml

# Edit .streamlit/secrets.toml and add your Groq API key
# Get key from: https://console.groq.com/api-keys
```

### 3. Prepare Data

```bash
# Data file should be at: data/kopiseru_clean_v4.csv
# If using different path, update DATA_PATH in utils/data_loader.py
```

### 4. Run Dashboard

```bash
streamlit run app.py
```

Dashboard akan terbuka di `http://localhost:8501`

---

## 📁 Project Structure

```
kopiseru-dashboard/
├── app.py                          # Entry point (home page)
├── requirements.txt                # Dependencies
├── secrets.toml.example            # API key template
├── .gitignore                      # Git ignore rules
│
├── data/
│   └── kopiseru_clean_v4.csv       # Dataset (2021-2023)
│
├── pages/                          # Multipage apps
│   ├── 1_📊_Executive_Dashboard.py
│   ├── 2_📈_Business_Growth.py
│   ├── 3_💹_Profitability.py
│   ├── 4_🏪_Branch_Performance.py
│   ├── 5_🎯_Expansion_Opportunity.py
│   ├── 6_😊_Customer_Insight.py
│   └── 7_🤖_AI_Business_Analyst.py
│
├── components/                     # Reusable UI components
│   ├── __init__.py
│   ├── sidebar.py                  # Global filters
│   ├── metrics.py                  # KPI cards, formatting
│   ├── charts.py                   # Plotly visualizations
│   └── ai_analyst.py               # Groq AI integration
│
├── utils/                          # Data processing
│   ├── __init__.py
│   └── data_loader.py              # Load, filter, aggregate data
│
└── .streamlit/
    ├── config.toml                 # Streamlit settings
    └── secrets.toml                # API keys (NOT in git)
```

---

## 🎨 Design & Branding

**Color Palette (KopiSeru Theme):**
- Primary: `#5C3D1E` (Deep Coffee Brown)
- Secondary: `#8B5E3C` (Medium Brown)
- Accent: `#D4A853` (Warm Gold)
- Background: `#FDF6EC` (Cream)

**Font:** Inter (imported from Google Fonts)

---

## 🤖 AI Integration (Groq)

### Features:

- **Context-Aware Analysis** - AI receives current filters, stats, and page context
- **Quick Prompts** - Pre-built analysis templates (Executive Summary, Recommendations, etc.)
- **Custom Questions** - Free-form chat with data context
- **Chart Explanations** - Explain any analysis topic from the dashboard

### Model:
- **LLaMA 3.3 70B** (via Groq API)
- Temperature: 0.4 (balanced)
- Max tokens: 200-800 (adaptive)

### Setup:
1. Get API key from https://console.groq.com
2. Add to `.streamlit/secrets.toml`
3. AI features enabled automatically

---

## 📊 Data Schema

**Dataset:** `kopiseru_clean_v4.csv` (2021-2023 operational data)

**Key Columns:**
- `date`, `year`, `month`, `day_of_week`
- `branch_id`, `branch_city`, `branch_type`
- `total_revenue`, `profit`, `profit_margin`
- `total_transactions`, `avg_ticket_size`
- `customer_satisfaction`
- `takeaway_percent`, `delivery_percent`, `dine_in_percent`
- `promo_type`, `promo_active`, `weather`, `is_weekend`

---

## 🚢 Deployment

### Streamlit Cloud (Recommended)

```bash
# 1. Push to GitHub
git push origin main

# 2. Visit https://share.streamlit.io
# 3. Deploy from GitHub repo

# 4. Add secrets in Streamlit Cloud:
# Settings → Secrets → Paste .streamlit/secrets.toml content
```

### Docker (Optional)

```dockerfile
FROM python:3.10-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8501
CMD ["streamlit", "run", "app.py"]
```

```bash
docker build -t kopiseru-dashboard .
docker run -p 8501:8501 kopiseru-dashboard
```

---

## 📈 Key Insights (From Analysis)

- **Revenue Growth:** +73.7% (2021→2022), +49.2% (2022→2023)
- **Best Branch Type:** Mall (35.2% margin)
- **Expansion Targets:** Makassar (0.933), Denpasar (0.700)
- **Weekend Challenge:** -19% profit despite stable revenue
- **Satisfaction Driver:** Branch atmosphere (NOT weather/promo)
- **Channel Trend:** Delivery growing consistently (24% → 30%)

---

## 🔧 Development

### Adding New Charts

1. Create function in `components/charts.py`
2. Import in `components/__init__.py`
3. Use in page with `st.plotly_chart(fig, use_container_width=True)`

### Adding New Pages

1. Create file: `pages/8_🎯_NewPage.py`
2. Follow structure of existing pages
3. Use `render_sidebar()` and `apply_filters()`
4. Streamlit auto-detects multipage apps

### Testing Locally

```bash
# Run with verbose logging
streamlit run app.py --logger.level=debug

# Profile performance
streamlit run app.py --logger.level=debug --client.showErrorDetails=true
```

---

## 🐛 Troubleshooting

**"No such file or directory: data/kopiseru_clean_v4.csv"**
→ Ensure CSV is in `data/` folder or update path in `utils/data_loader.py`

**"GROQ_API_KEY not found"**
→ Create `.streamlit/secrets.toml` and add key from Groq console

**"Module not found"**
→ Run `pip install -r requirements.txt` to install all deps

**Performance slow?**
→ Check caching decorators (`@st.cache_data`) are applied
→ Filter to smaller date range or fewer branches

---

## 📝 License

Fictional case study for educational purposes. KopiSeru is a fictional brand.

---

## 👥 Credits

**Analysis Framework:** Pandas, NumPy, Scikit-learn
**Visualization:** Plotly
**Frontend:** Streamlit
**AI:** Groq LLaMA 3.3 70B
**Data:** Fictional operational dataset (2021-2023)

---

## 📞 Support

For issues or feature requests:
1. Check GitHub Issues
2. Review existing documentation
3. Test with simplified filters first
4. Check `.streamlit/secrets.toml` configuration

---

**Happy analyzing! 🎉 Use data-driven insights to make smarter business decisions.**
