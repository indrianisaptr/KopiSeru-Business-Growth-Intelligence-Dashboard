# 🚀 KopiSeru Dashboard - Setup Guide

## ✅ Checklist Lengkap Setup Project

### 📁 Struktur Folder yang Harus Dibuat

```
kopiseru-dashboard/
├── app.py
├── requirements.txt
├── README.md
├── .gitignore
├── secrets.toml.example
│
├── .streamlit/
│   ├── config.toml
│   └── secrets.toml (JANGAN COMMIT! Buat sendiri)
│
├── data/
│   └── kopiseru_clean_v4.csv
│
├── pages/
│   ├── 1_📊_Executive_Dashboard.py
│   ├── 2_📈_Business_Growth.py
│   ├── 3_💹_Profitability.py
│   ├── 4_🏪_Branch_Performance.py
│   ├── 5_🎯_Expansion_Opportunity.py
│   ├── 6_😊_Customer_Insight.py
│   └── 7_🤖_AI_Business_Analyst.py
│
├── components/
│   ├── __init__.py
│   ├── sidebar.py
│   ├── metrics.py
│   ├── charts.py
│   └── ai_analyst.py
│
└── utils/
    ├── __init__.py
    └── data_loader.py
```

---

## 🔧 Setup Step-by-Step

### Step 1: Persiapkan Folder

```bash
# Clone atau buat folder baru
mkdir kopiseru-dashboard
cd kopiseru-dashboard

# Buat subfolder
mkdir -p .streamlit
mkdir -p data
mkdir -p pages
mkdir -p components
mkdir -p utils
```

### Step 2: Copy File-File dari Outputs

Semua file yang sudah dibuat ada di `/mnt/user-data/outputs/`

**Root files** (copy ke root directory):
- ✅ `app.py`
- ✅ `requirements.txt`
- ✅ `README.md`
- ✅ `.gitignore`
- ✅ `secrets.toml.example`

**Streamlit folder** (copy ke `.streamlit/`):
- ✅ `config.toml` → `.streamlit/config.toml`

**Pages folder** (copy ke `pages/`):
- ✅ `1_📊_Executive_Dashboard.py`
- ✅ `2_📈_Business_Growth.py`
- ✅ `3_💹_Profitability.py`
- ✅ `4_🏪_Branch_Performance.py`
- ✅ `5_🎯_Expansion_Opportunity.py`
- ✅ `6_😊_Customer_Insight.py`
- ✅ `7_🤖_AI_Business_Analyst.py`

**Components folder** (copy ke `components/`):
- ✅ `__init__.py`
- ✅ `sidebar.py`
- ✅ `metrics.py`
- ✅ `charts.py`
- ✅ `ai_analyst.py`

**Utils folder** (copy ke `utils/`):
- ✅ `__init__.py`
- ✅ `data_loader.py`

**Data folder** (copy ke `data/`):
- ✅ `kopiseru_clean_v4.csv`

### Step 3: Setup Virtual Environment (Recommended)

```bash
# Create virtual environment
python -m venv venv

# Activate
# On macOS/Linux:
source venv/bin/activate

# On Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Step 4: Create Secrets File

```bash
# Copy template
cp secrets.toml.example .streamlit/secrets.toml

# Edit the file and add your Groq API key
# .streamlit/secrets.toml:
# GROQ_API_KEY = "gsk_your_actual_key_here"
```

**Dapatkan API Key dari:**
1. Buka https://console.groq.com/api-keys
2. Login atau buat akun
3. Generate new API key
4. Copy dan paste ke `.streamlit/secrets.toml`

### Step 5: Verify Data File

```bash
# Pastikan data ada di lokasi yang benar
ls -la data/kopiseru_clean_v4.csv

# Jika path berbeda, update di:
# utils/data_loader.py -> DATA_PATH variable
```

### Step 6: Run Dashboard

```bash
# Make sure venv is activated
streamlit run app.py
```

Dashboard akan open di `http://localhost:8501`

---

## 📋 Pre-Launch Checklist

Sebelum menjalankan dashboard, pastikan:

- [ ] Semua file sudah di folder yang benar
- [ ] `.streamlit/secrets.toml` sudah dibuat dan berisi API key
- [ ] `data/kopiseru_clean_v4.csv` sudah ada
- [ ] Semua dependencies terinstall (`pip install -r requirements.txt`)
- [ ] Virtual environment sudah diaktifkan
- [ ] Tidak ada import errors saat `streamlit run app.py`

---

## 🎯 File Organization Summary

| File/Folder | Lokasi | Deskripsi |
|---|---|---|
| `app.py` | Root | Entry point dashboard (home page) |
| `requirements.txt` | Root | Python dependencies |
| `README.md` | Root | Dokumentasi lengkap |
| `.gitignore` | Root | Git ignore rules |
| `secrets.toml.example` | Root | Template untuk API keys |
| `config.toml` | `.streamlit/` | Streamlit settings & theme |
| `secrets.toml` | `.streamlit/` | **JANGAN COMMIT!** Buat sendiri |
| `*_Dashboard.py` dll | `pages/` | 7 halaman dashboard |
| `sidebar.py`, `metrics.py`, dll | `components/` | Reusable UI components |
| `data_loader.py` | `utils/` | Data loading & preprocessing |
| `kopiseru_clean_v4.csv` | `data/` | Dataset CSV |

---

## 🚨 Important Notes

### ⚠️ JANGAN Commit Secrets!

```bash
# ❌ WRONG - Jangan commit secrets file
git add .streamlit/secrets.toml

# ✅ RIGHT - Hanya commit template
git add secrets.toml.example
```

### 🔐 Untuk Streamlit Cloud Deployment

1. Push ke GitHub (tanpa `secrets.toml`)
2. Connect ke Streamlit Cloud
3. Go to Settings → Secrets
4. Paste isi dari `.streamlit/secrets.toml`
5. Streamlit Cloud otomatis manage secrets

### 📍 Data Path Issues

Jika data tidak ditemukan:

```python
# Edit utils/data_loader.py
# Ubah DATA_PATH ke path yang benar:

# Current:
DATA_PATH = Path(__file__).parent.parent / "data" / "kopiseru_clean_v4.csv"

# Alternative:
DATA_PATH = "data/kopiseru_clean_v4.csv"
DATA_PATH = "/absolute/path/to/kopiseru_clean_v4.csv"
```

---

## 🧪 Testing

### Test Local Deployment

```bash
# Run dengan debug mode
streamlit run app.py --logger.level=debug

# Run specific page
streamlit run pages/1_📊_Executive_Dashboard.py
```

### Test Sidebar Filters

1. Buka dashboard
2. Klik dropdown filters di sidebar
3. Pilih berbagai kombinasi (Year, Month, City, dll)
4. Verify semua charts update sesuai filter

### Test AI Features

1. Buka page 7 (AI Business Analyst)
2. Klik salah satu quick prompt button
3. Verify AI response muncul dalam beberapa detik
4. Pastikan API key valid

---

## 📚 Dokumentasi Lengkap

Lihat `README.md` untuk:
- Dashboard features
- Design & branding
- AI integration details
- Deployment options
- Development guide
- Troubleshooting

---

## 🎉 You're All Set!

Setelah semua setup selesai:

1. Dashboard siap digunakan
2. Semua 7 halaman accessible
3. AI features aktif
4. Filters bekerja di semua page
5. Siap untuk production deployment

**Enjoy exploring KopiSeru business insights! ☕📊**

---

## 📞 Troubleshooting Quick Links

- **"No such file or directory"** → Cek folder structure
- **"GROQ_API_KEY not found"** → Setup `.streamlit/secrets.toml`
- **"Module not found"** → Run `pip install -r requirements.txt`
- **"Port 8501 already in use"** → `streamlit run app.py --server.port=8502`

---

Untuk bantuan lebih lanjut, baca **README.md** atau check GitHub Issues.
