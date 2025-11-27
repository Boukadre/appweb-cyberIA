"""
CyberSec Blue Team Toolkit V2
Professional Modular Cybersecurity Analysis Platform

Main entry point with Streamlit navigation
"""

import streamlit as st
from datetime import datetime
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import all modules
from modules import (
    render_ssh_forensics,
    render_phishing_detector,
    render_password_auditor,
    render_payload_classifier
)

# Page configuration
st.set_page_config(
    page_title="🛡️ Blue Team Toolkit V2",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://github.com/yourusername/blue-team-toolkit',
        'Report a bug': 'https://github.com/yourusername/blue-team-toolkit/issues',
        'About': '''
        # Blue Team Toolkit V2
        
        Professional cybersecurity analysis platform with AI/ML capabilities.
        
        **Version:** 2.0.0
        
        **Features:**
        - SSH Forensics with geolocation
        - AI-powered phishing detection
        - Password breach checking
        - ML-based payload classification
        '''
    }
)

# Custom CSS for better UI
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        padding: 1rem 0;
    }
    
    .stAlert {
        border-radius: 10px;
    }
    
    .module-card {
        padding: 1.5rem;
        border-radius: 10px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        margin: 1rem 0;
    }
    
    .metric-card {
        background: #f0f2f6;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #667eea;
    }
</style>
""", unsafe_allow_html=True)


def check_api_keys() -> dict:
    """
    Check which API keys are configured
    
    Returns:
        Dictionary of API key availability
    """
    return {
        'abuseipdb': bool(os.getenv('ABUSEIPDB_API_KEY')),
        'virustotal': bool(os.getenv('VIRUSTOTAL_API_KEY'))
    }


def render_sidebar():
    """Render the sidebar navigation"""
    
    with st.sidebar:
        # Logo and title
        st.markdown("""
        <div style='text-align: center; padding: 1rem 0;'>
            <h1 style='color: #667eea; margin: 0;'>🛡️</h1>
            <h2 style='margin: 0.5rem 0;'>Blue Team</h2>
            <h3 style='margin: 0; color: #666;'>Toolkit V2</h3>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Navigation menu
        st.markdown("### 📋 Navigation")
        
        module = st.radio(
            "Select Module:",
            [
                "🏠 Home",
                "🔒 SSH Forensics",
                "🎣 Phishing Detector",
                "🔑 Password Auditor",
                "💉 Payload Classifier"
            ],
            key="navigation_radio"
        )
        
        st.markdown("---")
        
        # API Status
        st.markdown("### ⚙️ API Configuration")
        
        api_status = check_api_keys()
        
        if api_status['abuseipdb']:
            st.success("✅ AbuseIPDB")
        else:
            st.error("❌ AbuseIPDB")
        
        if api_status['virustotal']:
            st.success("✅ VirusTotal")
        else:
            st.error("❌ VirusTotal")
        
        st.info("💡 HaveIBeenPwned: No key required")
        st.info("🗺️ IP Geolocation: No key required")
        
        if not api_status['abuseipdb'] or not api_status['virustotal']:
            with st.expander("🔧 Setup API Keys"):
                st.markdown("""
                **Configure in `.env` file:**
                ```
                ABUSEIPDB_API_KEY=your_key
                VIRUSTOTAL_API_KEY=your_key
                ```
                
                Or use Streamlit secrets (`.streamlit/secrets.toml`)
                """)
        
        st.markdown("---")
        
        # System info
        st.markdown("### 📊 System Info")
        st.caption(f"🕒 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        st.caption("🐍 Python 3.x")
        st.caption("🚀 Streamlit")
        st.caption("🤖 AI/ML Enabled")
        
        st.markdown("---")
        
        # Footer
        st.caption("Made with ❤️ by Blue Team")
        st.caption(f"© {datetime.now().year} | Version 2.0.0")
        
        return module


def render_home():
    """Render the home page"""
    
    st.markdown('<h1 class="main-header">🛡️ Blue Team Toolkit V2</h1>', unsafe_allow_html=True)
    
    st.markdown("""
    <div style='text-align: center; font-size: 1.2rem; color: #666; margin-bottom: 2rem;'>
        Professional Cybersecurity Analysis Platform with AI/ML Capabilities
    </div>
    """, unsafe_allow_html=True)
    
    # Feature highlights
    st.markdown("## 🚀 What's New in V2")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        ### ✨ New Features
        - 🤖 **AI-Powered Detection** using Hugging Face transformers
        - 🗺️ **Geographic Intelligence** with interactive maps
        - 📊 **Advanced ML Classification** for payload analysis
        - 🎯 **Professional Gauge Charts** for password strength
        - 🌐 **DNS Validation** for email domains
        - 📈 **Enhanced Analytics** and reporting
        """)
    
    with col2:
        st.markdown("""
        ### 🏗️ Architecture
        - 📦 **Modular Design** - Clean separation of concerns
        - ⚡ **Optimized Performance** - Cached ML models
        - 🔒 **Enhanced Security** - k-Anonymity, local processing
        - 🎨 **Modern UI/UX** - Professional design
        - 📚 **Comprehensive Logging** - Detailed analysis
        - 🛡️ **Production Ready** - Error handling & validation
        """)
    
    st.markdown("---")
    
    # Module overview
    st.markdown("## 📦 Available Modules")
    
    # Module 1
    with st.container():
        col1, col2 = st.columns([1, 4])
        with col1:
            st.markdown("<h1 style='text-align: center;'>🔒</h1>", unsafe_allow_html=True)
        with col2:
            st.markdown("### SSH Forensics & Geolocation")
            st.markdown("""
            Advanced SSH log analysis with **geographic intelligence**:
            - Parse authentication logs
            - Identify attacking IPs
            - **NEW:** Interactive world map visualization
            - **NEW:** Geolocation data (Country, City, ISP)
            - Top attacker statistics
            - Export forensic reports
            
            **API Used:** ip-api.com (free, no key required)
            """)
    
    st.markdown("---")
    
    # Module 2
    with st.container():
        col1, col2 = st.columns([1, 4])
        with col1:
            st.markdown("<h1 style='text-align: center;'>🎣</h1>", unsafe_allow_html=True)
        with col2:
            st.markdown("### AI-Powered Phishing Detection")
            st.markdown("""
            Machine Learning phishing classifier with **BERT model**:
            - **NEW:** AI probability scoring using transformers
            - **NEW:** DNS MX record validation
            - Heuristic keyword analysis
            - Automatic URL extraction
            - Sender domain verification
            - Comprehensive risk assessment
            
            **AI Model:** Hugging Face BERT (phishing-specific)
            """)
    
    st.markdown("---")
    
    # Module 3
    with st.container():
        col1, col2 = st.columns([1, 4])
        with col1:
            st.markdown("<h1 style='text-align: center;'>🔑</h1>", unsafe_allow_html=True)
        with col2:
            st.markdown("### Password Strength Auditor")
            st.markdown("""
            Professional password analysis with **visual gauge**:
            - **NEW:** Interactive gauge chart (Plotly)
            - Comprehensive strength scoring (0-100)
            - Realistic crack time estimation
            - HaveIBeenPwned breach checking
            - k-Anonymity privacy protection
            - Actionable security recommendations
            
            **Privacy:** Local analysis, only hash prefix transmitted
            """)
    
    st.markdown("---")
    
    # Module 4
    with st.container():
        col1, col2 = st.columns([1, 4])
        with col1:
            st.markdown("<h1 style='text-align: center;'>💉</h1>", unsafe_allow_html=True)
        with col2:
            st.markdown("### ML Payload Classifier")
            st.markdown("""
            Machine Learning injection attack detector:
            - **NEW:** TF-IDF + Logistic Regression classifier
            - **NO REGEX:** Pure ML approach
            - SQL Injection detection
            - XSS (Cross-Site Scripting) detection
            - Confidence scoring
            - Feature breakdown and analysis
            
            **ML Model:** Trained on real attack patterns
            """)
    
    st.markdown("---")
    
    # Getting started
    st.markdown("## 🎯 Getting Started")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        ### 1️⃣ Select Module
        Use the sidebar to navigate to your desired analysis module
        """)
    
    with col2:
        st.markdown("""
        ### 2️⃣ Upload/Input Data
        Provide logs, emails, passwords, or payloads for analysis
        """)
    
    with col3:
        st.markdown("""
        ### 3️⃣ Review Results
        Get detailed insights, recommendations, and export reports
        """)
    
    st.markdown("---")
    
    # API Configuration status
    st.markdown("## 🔧 Configuration Status")
    
    api_status = check_api_keys()
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if api_status['abuseipdb']:
            st.success("✅ AbuseIPDB\nConfigured")
        else:
            st.warning("⚠️ AbuseIPDB\nNot Configured")
    
    with col2:
        if api_status['virustotal']:
            st.success("✅ VirusTotal\nConfigured")
        else:
            st.warning("⚠️ VirusTotal\nNot Configured")
    
    with col3:
        st.info("✅ HaveIBeenPwned\nNo Key Required")
    
    with col4:
        st.info("✅ IP Geolocation\nNo Key Required")
    
    if not all(api_status.values()):
        st.info("""
        💡 **Note:** Some features work without API keys in degraded mode.
        For full functionality, configure API keys in `.env` or `.streamlit/secrets.toml`
        """)
    
    st.markdown("---")
    
    # Quick stats
    st.markdown("## 📈 Toolkit Capabilities")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Modules", "4", "Professional")
    with col2:
        st.metric("AI Models", "3+", "ML/DL")
    with col3:
        st.metric("API Integrations", "5", "External")
    with col4:
        st.metric("Detection Types", "10+", "Threats")
    
    st.markdown("---")
    
    # Footer callout
    st.success("""
    🚀 **Ready to enhance your security posture?**
    
    Select a module from the sidebar to begin your analysis!
    """)


def main():
    """Main application entry point"""
    
    # Render sidebar and get selected module
    selected_module = render_sidebar()
    
    # Route to appropriate module
    if selected_module == "🏠 Home":
        render_home()
    
    elif selected_module == "🔒 SSH Forensics":
        render_ssh_forensics()
    
    elif selected_module == "🎣 Phishing Detector":
        render_phishing_detector()
    
    elif selected_module == "🔑 Password Auditor":
        render_password_auditor()
    
    elif selected_module == "💉 Payload Classifier":
        render_payload_classifier()


if __name__ == "__main__":
    main()

