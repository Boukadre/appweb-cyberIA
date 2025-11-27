# ⚡ Quick Start Guide - Blue Team Toolkit V2

Get up and running in **5 minutes**!

---

## 📦 Installation (3 steps)

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

⏱️ *This may take 5-10 minutes on first install (ML libraries are large)*

### 2. Configure API Keys (Optional)

Create a `.env` file:

```bash
cp .env.example .env
```

Edit `.env` and add your keys:

```env
ABUSEIPDB_API_KEY=your_key_here
VIRUSTOTAL_API_KEY=your_key_here
```

**Get Free API Keys:**
- AbuseIPDB: https://www.abuseipdb.com/api
- VirusTotal: https://www.virustotal.com/gui/join-us

**Note:** App works without API keys, but with limited features.

### 3. Launch Application

```bash
streamlit run main.py
```

🎉 **Done!** Your browser will open at `http://localhost:8501`

---

## 🎯 First Run

### What to Expect

1. **Initial Setup (1-2 minutes)**
   - ML models will download automatically on first use
   - BERT model: ~400 MB
   - Progress shown in Streamlit

2. **Home Page**
   - Overview of all modules
   - Configuration status
   - Getting started guide

3. **Sidebar Navigation**
   - Select modules from the left
   - Check API status
   - View system info

---

## 🧪 Quick Test

### Test Each Module

#### 1. SSH Forensics 🔒

**Sample Data:** Use included `example_auth.log`

```bash
# In the app:
1. Click "SSH Forensics" in sidebar
2. Upload example_auth.log
3. Wait for map to load (~10 seconds)
4. View results!
```

**Expected Output:**
- Table of attacking IPs
- Interactive world map
- Country/ISP information

---

#### 2. Phishing Detector 🎣

**Test Email:**

```
Subject: URGENT: Action Required on Your Account

Body:
Dear Customer,

Your account has been suspended due to unusual activity.
Please verify your information immediately by clicking here:
http://suspicious-bank-verify.com/login

Failure to act within 24 hours will result in permanent closure.

Best regards,
Security Team
```

**Steps:**
1. Click "Phishing Detector" in sidebar
2. Paste subject and body
3. Optional: Add fake sender email
4. Click "Analyze Email"

**Expected Output:**
- AI Phishing Probability: 70-90%
- Suspicious keywords detected
- Risk level: HIGH

---

#### 3. Password Auditor 🔑

**Test Passwords:**

| Password | Expected Strength |
|----------|-------------------|
| `password123` | Very Weak (compromised) |
| `P@ssw0rd` | Weak |
| `MyDog2024!` | Moderate |
| `C0mpl3x!P@ssw0rd` | Strong |
| `Tr0ub4dor&3#Xk9$mQ` | Excellent |

**Steps:**
1. Click "Password Auditor" in sidebar
2. Enter password
3. View instant gauge chart
4. Check breach status

**Expected Output:**
- Gauge chart (0-100)
- Crack time estimate
- Breach check result

---

#### 4. Payload Classifier 💉

**Test Payloads:**

**Safe:**
```
search?query=python programming
```

**SQL Injection:**
```
admin' OR '1'='1'--
```

**XSS:**
```
<script>alert('XSS')</script>
```

**Steps:**
1. Click "Payload Classifier" in sidebar
2. Paste payload
3. Click "Analyze Payload"

**Expected Output:**
- Classification (Safe/SQLi/XSS)
- Confidence percentage
- Feature breakdown

---

## 🔧 Troubleshooting

### ML Model Not Loading

**Error:** `Connection timeout` or `Model download failed`

**Solution:**
```bash
# Pre-download models manually
python -c "from transformers import pipeline; pipeline('text-classification', model='ealvaradob/bert-finetuned-phishing', device=-1)"
```

### Out of Memory

**Error:** `RuntimeError: out of memory`

**Solution:**
- Close other applications
- Restart Streamlit
- Models will use fallback (TF-IDF) if BERT fails

### API Not Working

**Error:** `API Key manquante` in sidebar

**Solution:**
1. Check `.env` file exists
2. Verify keys are correct (no quotes in .env)
3. Restart Streamlit: `Ctrl+C` then `streamlit run main.py`

### Import Errors

**Error:** `ModuleNotFoundError: No module named 'X'`

**Solution:**
```bash
# Reinstall all dependencies
pip install --upgrade -r requirements.txt
```

---

## 💡 Pro Tips

### Performance

- ✅ **First Run:** Models download once, cached forever
- ✅ **Subsequent Runs:** Instant loading
- ✅ **Close Unused Tabs:** Save memory

### Best Practices

- 🔐 **Never test real passwords** in production
- 📁 **Use sample data** for testing
- 🔑 **Keep API keys private** (don't commit .env)
- 📊 **Export reports** for documentation

### Keyboard Shortcuts

- `R` - Rerun the app
- `C` - Clear cache
- `Ctrl+C` - Stop server

---

## 📚 Next Steps

### Learn More

1. **Read Full Documentation:** `README_V2.md`
2. **API Configuration:** `CONFIG.md`
3. **Module Details:** Explore each module in the app

### Customize

- Modify modules in `modules/` directory
- Add new modules by creating new `.py` files
- Update `main.py` navigation

### Deploy

- **Local Network:** Use `--server.address 0.0.0.0`
- **Cloud:** Deploy to Streamlit Cloud, Heroku, or AWS
- **Docker:** Create Dockerfile for containerization

---

## 🆘 Getting Help

### Resources

- 📖 **Documentation:** README_V2.md
- 🐛 **Issues:** GitHub Issues
- 💬 **Discussions:** GitHub Discussions

### Community

- 🌟 Star the project
- 🍴 Fork for customization
- 🤝 Contribute improvements

---

## ✅ Checklist

Before you start, make sure you have:

- [ ] Python 3.8+ installed
- [ ] Installed requirements.txt
- [ ] (Optional) Created .env file
- [ ] (Optional) Added API keys
- [ ] Launched with `streamlit run main.py`
- [ ] Browser opened to localhost:8501

---

## 🚀 Ready to Go!

You're all set! Open the app and start analyzing:

```bash
streamlit run main.py
```

**Happy Threat Hunting! 🛡️**

---

*Need help? Check README_V2.md or open an issue on GitHub.*


