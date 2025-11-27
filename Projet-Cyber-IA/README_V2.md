# 🛡️ CyberSec Blue Team Toolkit V2

**Professional Modular Cybersecurity Analysis Platform with AI/ML Capabilities**

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Streamlit](https://img.shields.io/badge/streamlit-1.28+-red.svg)](https://streamlit.io/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## 🎯 Overview

Blue Team Toolkit V2 is a complete rewrite of the original application, featuring a **professional modular architecture** and **advanced AI/ML capabilities**. This toolkit provides security analysts with powerful tools for threat detection, log analysis, and security auditing.

### 🆕 What's New in V2

- **🏗️ Modular Architecture** - Clean separation of concerns with `modules/` package
- **🤖 AI/ML Integration** - Hugging Face transformers for intelligent detection
- **🗺️ Geographic Intelligence** - Interactive maps showing attack origins
- **📊 Advanced Visualization** - Professional gauge charts and metrics
- **🌐 DNS Validation** - MX record checking for email domains
- **⚡ Optimized Performance** - Cached models and efficient processing
- **🎨 Modern UI/UX** - Professional design with custom styling

---

## 📦 Modules

### 1. 🔒 SSH Forensics & Geolocation

Advanced SSH log analysis with geographic intelligence.

**Features:**
- Parse `/var/log/auth.log` for failed authentication attempts
- Identify attacking IP addresses
- **NEW:** Interactive world map visualization
- **NEW:** Geolocation data (Country, City, ISP, Organization)
- Export forensic reports to CSV
- Security recommendations

**APIs Used:**
- `ip-api.com` (Free, no key required - 45 req/min)

**Example Output:**
```
Top 10 Attacking IPs:
🇨🇳 203.0.113.50 | 45 attempts | Beijing, China | ISP: China Telecom
🇷🇺 198.51.100.25 | 32 attempts | Moscow, Russia | ISP: Rostelecom
```

---

### 2. 🎣 AI-Powered Phishing Detection

Machine Learning phishing classifier using BERT transformers.

**Features:**
- **NEW:** AI-powered phishing probability (Hugging Face BERT)
- **NEW:** DNS MX record validation for sender domains
- Heuristic keyword analysis (urgency, financial, etc.)
- Automatic URL extraction via regex
- Email address extraction and validation
- Comprehensive risk scoring

**AI Model:**
- `ealvaradob/bert-finetuned-phishing` (primary)
- Fallback to `distilbert-base-uncased` if unavailable

**APIs Used:**
- DNS resolution (dnspython)
- VirusTotal (optional, for URL scanning)

**Example Analysis:**
```
🤖 AI Phishing Probability: 87%
📊 Heuristic Score: 72%
⚠️ Overall Risk: HIGH 🚨

Suspicious Keywords: urgent, verify, suspended, click here
URLs Found: http://suspicious-bank-verify[.]com
Domain Status: ❌ No MX records (likely spoofed)
```

---

### 3. 🔑 Password Strength Auditor

Professional password analysis with visual gauge chart.

**Features:**
- **NEW:** Interactive Plotly gauge chart (0-100 score)
- Comprehensive strength scoring algorithm
- Realistic crack time estimation (10B attempts/sec)
- HaveIBeenPwned breach checking (k-Anonymity)
- Character diversity analysis
- Pattern detection (sequences, repetitions)
- Actionable recommendations

**Privacy:**
- All analysis performed locally
- Only SHA-1 hash prefix (5 chars) sent to HaveIBeenPwned
- k-Anonymity protocol ensures privacy

**Example Output:**
```
Password: Tr0ub4dor&3
Score: 85/100 (Excellent)
Crack Time: 2,458 years
Breach Status: ✅ Not found in any known breaches
```

---

### 4. 💉 ML-Powered Payload Classifier

Machine Learning injection attack detector (NO REGEX approach).

**Features:**
- **NEW:** TF-IDF + Logistic Regression classifier
- **NEW:** Trained on real attack patterns
- SQL Injection detection (UNION, OR 1=1, etc.)
- XSS (Cross-Site Scripting) detection
- Confidence scoring per attack type
- Feature breakdown and explanation
- Security recommendations

**ML Approach:**
- Primary: Hugging Face text classification models
- Fallback: TF-IDF vectorizer + Logistic Regression
- Training on 50+ real SQLi/XSS samples
- Character n-gram analysis (2-4 grams)

**Example Classification:**
```
Input: admin' OR '1'='1'--

Classification: SQL Injection
Confidence: 94%
Risk Level: 🔴 HIGH RISK

SQL Injection Score: 95%
XSS Score: 5%

Features Detected:
- SQL Keywords: 2 (OR)
- SQL Quotes: 4
- Tautology: Yes
- SQL Comments: Yes (--
```

---

## 🚀 Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- 4GB+ RAM (for ML models)
- Internet connection (for model download on first run)

### Step 1: Clone Repository

```bash
git clone https://github.com/yourusername/blue-team-toolkit-v2.git
cd blue-team-toolkit-v2
```

### Step 2: Create Virtual Environment (Recommended)

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

**Note:** First installation may take 5-10 minutes due to ML libraries (torch, transformers).

### Step 4: Configure API Keys (Optional)

```bash
# Copy example file
cp .env.example .env

# Edit .env and add your keys
notepad .env  # Windows
nano .env     # Linux/Mac
```

**Required API Keys:**
- `ABUSEIPDB_API_KEY` - For IP reputation in SSH module
- `VIRUSTOTAL_API_KEY` - For URL scanning in phishing module

**No Keys Required:**
- HaveIBeenPwned (public API)
- ip-api.com (free geolocation)
- Hugging Face models (downloaded locally)

### Step 5: Launch Application

```bash
streamlit run main.py
```

The application will open automatically in your browser at `http://localhost:8501`

---

## 🔑 API Configuration

### Option 1: Environment Variables (.env file)

Create a `.env` file in the project root:

```env
ABUSEIPDB_API_KEY=your_key_here
VIRUSTOTAL_API_KEY=your_key_here
```

### Option 2: Streamlit Secrets

Create `.streamlit/secrets.toml`:

```toml
ABUSEIPDB_API_KEY = "your_key_here"
VIRUSTOTAL_API_KEY = "your_key_here"
```

### Getting API Keys

#### AbuseIPDB
1. Register at [abuseipdb.com/api](https://www.abuseipdb.com/api)
2. Generate free API key
3. Free tier: 1,000 requests/day

#### VirusTotal
1. Register at [virustotal.com](https://www.virustotal.com/gui/join-us)
2. Get API key from your profile
3. Free tier: 500 requests/day, 4 requests/minute

---

## 📁 Project Structure

```
blue-team-toolkit-v2/
├── main.py                    # Entry point & navigation
├── requirements.txt           # Python dependencies
├── .env.example              # API key template
├── README_V2.md              # This file
│
├── modules/                  # Core logic modules
│   ├── __init__.py           # Package initialization
│   ├── ssh_detector.py       # Module 1: SSH Forensics
│   ├── phishing_ai.py        # Module 2: Phishing AI
│   ├── pass_auditor.py       # Module 3: Password Auditor
│   └── payload_ml.py         # Module 4: Payload ML
│
├── .streamlit/               # Streamlit config
│   └── secrets.toml.example  # API key template
│
└── example_auth.log          # Sample SSH log file
```

---

## 🎮 Usage Examples

### SSH Forensics

1. Navigate to "🔒 SSH Forensics" in sidebar
2. Upload your `/var/log/auth.log` file
3. Wait for parsing and geolocation lookup
4. View interactive map and statistics
5. Download CSV report

**Sample Log Format:**
```
Nov 26 08:15:23 server sshd[12345]: Failed password for root from 192.168.1.100 port 22 ssh2
```

### Phishing Detection

1. Navigate to "🎣 Phishing Detector"
2. Paste email subject and body
3. Optionally add sender email
4. Click "Analyze Email"
5. Review AI probability and risk assessment

### Password Auditing

1. Navigate to "🔑 Password Auditor"
2. Enter password in secure field
3. View instant gauge chart and score
4. Check breach database status
5. Review recommendations

### Payload Classification

1. Navigate to "💉 Payload Classifier"
2. Paste HTTP request or URL parameter
3. Click "Analyze Payload"
4. Review ML classification and confidence
5. View detected features

---

## 🧪 Testing

### Quick Test Commands

**Test SSH Module:**
```bash
# Use provided example_auth.log
streamlit run main.py
# Upload example_auth.log in SSH module
```

**Test Phishing Module:**
```
Subject: URGENT: Verify Your Account
Body: Your account will be suspended. Click here: http://phishing.com
```

**Test Password Module:**
```
Weak: password123
Strong: Tr0ub4dor&3#Xk9$mQ
```

**Test Payload Module:**
```
SQLi: admin' OR '1'='1'--
XSS: <script>alert('XSS')</script>
Safe: search?q=python
```

---

## 🏗️ Architecture

### Modular Design

```
main.py (Navigation)
    ↓
modules/__init__.py (Exports)
    ↓
Individual Modules (Render Functions)
    ↓
External APIs / ML Models
```

### Key Design Principles

1. **Separation of Concerns** - Each module is self-contained
2. **Caching** - ML models loaded once with `@st.cache_resource`
3. **Error Handling** - Graceful degradation when APIs unavailable
4. **Performance** - Lazy loading, efficient algorithms
5. **Security** - No data persistence, local processing

---

## 🛡️ Security & Privacy

### Data Handling

- ✅ **No data storage** - All analysis is ephemeral
- ✅ **Local processing** - ML models run on your machine
- ✅ **k-Anonymity** - Password breach checks use hash prefix only
- ✅ **No telemetry** - No data sent to third parties (except APIs)

### API Privacy

| API | Data Sent | Privacy Level |
|-----|-----------|---------------|
| HaveIBeenPwned | SHA-1 prefix (5 chars) | 🟢 High |
| ip-api.com | IP address | 🟡 Medium |
| AbuseIPDB | IP address | 🟡 Medium |
| VirusTotal | URL | 🟡 Medium |
| Hugging Face | None (local) | 🟢 High |

---

## 📊 Performance

### Resource Requirements

- **RAM:** 2-4 GB (depends on ML models)
- **Disk:** 1-2 GB (ML models cached)
- **CPU:** Any modern processor
- **GPU:** Not required (CPU mode)

### First Run

- ML models downloaded automatically
- BERT model: ~400 MB
- TF-IDF model: Built on-the-fly (~1 MB)
- Subsequent runs: Instant (cached)

---

## 🤝 Contributing

We welcome contributions! Please see our contributing guidelines:

1. Fork the repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open Pull Request

### Development Setup

```bash
# Install dev dependencies
pip install -r requirements.txt
pip install black flake8 pytest

# Run linters
black modules/ main.py
flake8 modules/ main.py

# Run tests (if available)
pytest tests/
```

---

## 🐛 Troubleshooting

### ML Model Download Fails

**Issue:** Timeout or connection error during model download

**Solution:**
```bash
# Manually download models
python -c "from transformers import pipeline; pipeline('text-classification', model='ealvaradob/bert-finetuned-phishing')"
```

### Out of Memory Error

**Issue:** System runs out of RAM

**Solution:**
- Close other applications
- Use TF-IDF fallback instead of BERT
- Reduce batch size in code

### API Rate Limits

**Issue:** Too many requests to external APIs

**Solution:**
- Wait 24 hours for quota reset
- Upgrade to paid API tier
- Use alternative free services

### Import Errors

**Issue:** `ModuleNotFoundError`

**Solution:**
```bash
# Reinstall dependencies
pip install --upgrade -r requirements.txt
```

---

## 📚 Resources

### Documentation

- [Streamlit Docs](https://docs.streamlit.io/)
- [Hugging Face Transformers](https://huggingface.co/docs/transformers/)
- [scikit-learn](https://scikit-learn.org/stable/)

### APIs

- [AbuseIPDB API Docs](https://docs.abuseipdb.com/)
- [VirusTotal API Docs](https://developers.virustotal.com/reference)
- [HaveIBeenPwned API](https://haveibeenpwned.com/API/v3)
- [ip-api.com Docs](https://ip-api.com/docs/)

### Security Resources

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [CWE Database](https://cwe.mitre.org/)
- [SANS Blue Team Resources](https://www.sans.org/blue-team/)

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- Hugging Face for transformer models
- OWASP for security testing methodologies
- Troy Hunt for HaveIBeenPwned API
- Streamlit team for amazing framework
- Open source security community

---

## 📞 Support

- 🐛 **Bug Reports:** [GitHub Issues](https://github.com/yourusername/blue-team-toolkit-v2/issues)
- 💬 **Discussions:** [GitHub Discussions](https://github.com/yourusername/blue-team-toolkit-v2/discussions)
- 📧 **Email:** security@yourcompany.com
- 🐦 **Twitter:** @BluTeamToolkit

---

## 🗺️ Roadmap

### V2.1 (Planned)

- [ ] Real-time log streaming
- [ ] Multi-file batch processing
- [ ] Custom ML model training interface
- [ ] API rate limit management
- [ ] Dark mode theme

### V2.2 (Future)

- [ ] Database integration for history
- [ ] User authentication system
- [ ] Team collaboration features
- [ ] Scheduled scans
- [ ] Email/Slack alerts

---

<div align="center">

**Made with ❤️ by the Blue Team**

⭐ Star us on GitHub if you find this useful!

[Report Bug](https://github.com/yourusername/blue-team-toolkit-v2/issues) · [Request Feature](https://github.com/yourusername/blue-team-toolkit-v2/issues) · [Documentation](https://github.com/yourusername/blue-team-toolkit-v2/wiki)

</div>

