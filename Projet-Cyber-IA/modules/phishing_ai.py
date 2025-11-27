"""
Module 2: AI-Powered Phishing Detector
Uses Hugging Face transformers for advanced phishing detection
"""

import streamlit as st
import re
import dns.resolver
from typing import List, Tuple, Dict, Optional
import warnings

warnings.filterwarnings('ignore')


@st.cache_resource(show_spinner=False)
def load_phishing_model():
    """
    Load pre-trained phishing detection model from Hugging Face
    Cached to avoid reloading on every run
    
    Returns:
        Hugging Face pipeline for text classification
    """
    try:
        from transformers import pipeline
        
        # Try primary model - specifically trained for phishing
        try:
            model = pipeline(
                "text-classification",
                model="ealvaradob/bert-finetuned-phishing",
                device=-1  # CPU mode
            )
            return model, "ealvaradob/bert-finetuned-phishing"
        except Exception:
            # Fallback to a general sentiment/classification model
            try:
                model = pipeline(
                    "text-classification",
                    model="distilbert-base-uncased-finetuned-sst-2-english",
                    device=-1
                )
                return model, "distilbert-base-uncased-finetuned-sst-2-english (fallback)"
            except Exception:
                return None, None
                
    except Exception as e:
        st.error(f"Error loading model: {str(e)}")
        return None, None


def extract_urls(text: str) -> List[str]:
    """Extract all URLs from text"""
    url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
    urls = re.findall(url_pattern, text)
    return urls


def extract_email_addresses(text: str) -> List[str]:
    """Extract email addresses from text"""
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    emails = re.findall(email_pattern, text)
    return emails


def extract_domain_from_email(email: str) -> Optional[str]:
    """Extract domain from email address"""
    try:
        return email.split('@')[1]
    except:
        return None


def check_mx_records(domain: str) -> Dict:
    """
    Check if domain has valid MX records (email server)
    
    Args:
        domain: Domain name to check
        
    Returns:
        Dictionary with validation results
    """
    try:
        mx_records = dns.resolver.resolve(domain, 'MX')
        mx_hosts = [str(r.exchange) for r in mx_records]
        
        return {
            'valid': True,
            'mx_count': len(mx_hosts),
            'mx_records': mx_hosts[:3],  # Show first 3
            'message': f"✅ Valid domain with {len(mx_hosts)} MX record(s)"
        }
    except dns.resolver.NoAnswer:
        return {
            'valid': False,
            'mx_count': 0,
            'mx_records': [],
            'message': "⚠️ Domain exists but has no MX records (suspicious)"
        }
    except dns.resolver.NXDOMAIN:
        return {
            'valid': False,
            'mx_count': 0,
            'mx_records': [],
            'message': "❌ Domain does not exist (likely spoofed)"
        }
    except Exception as e:
        return {
            'valid': None,
            'mx_count': 0,
            'mx_records': [],
            'message': f"⚠️ Could not verify: {str(e)}"
        }


def calculate_heuristic_score(subject: str, body: str) -> Tuple[int, List[str]]:
    """
    Calculate heuristic phishing score (backup method)
    
    Returns:
        Tuple of (score, list of detected keywords)
    """
    text = (subject + " " + body).lower()
    
    suspicious_patterns = {
        # Urgency
        'urgent': 3, 'immediately': 3, 'immédiat': 3, 'action required': 3,
        'act now': 3, 'limited time': 2,
        
        # Account/Security
        'verify': 2, 'suspended': 3, 'blocked': 3, 'locked': 3,
        'unusual activity': 3, 'confirm': 2, 'security alert': 3,
        
        # Financial
        'bank': 2, 'paypal': 2, 'payment': 2, 'invoice': 2,
        'refund': 2, 'transaction': 2, 'credit card': 3,
        
        # Prizes/Rewards
        'winner': 3, 'prize': 3, 'lottery': 4, 'congratulations': 2,
        'claim': 2, 'free': 2, 'gift': 2,
        
        # Legal/Official
        'legal action': 4, 'lawsuit': 4, 'tax': 3, 'irs': 4,
        'fine': 3, 'penalty': 3,
        
        # Authentication
        'reset password': 2, 'update payment': 3, 'verify account': 3,
        'click here': 3, 'download': 2, 'attachment': 2
    }
    
    score = 0
    found_keywords = []
    
    for keyword, weight in suspicious_patterns.items():
        if keyword in text:
            score += weight
            found_keywords.append(keyword)
    
    return score, found_keywords


def render_phishing_detector():
    """Main rendering function for AI Phishing Detector"""
    
    st.header("🎣 AI-Powered Phishing Detector")
    st.markdown("""
    **Advanced email analysis using Machine Learning and DNS validation**
    
    This module provides:
    - 🤖 AI-powered phishing probability detection (BERT model)
    - 🌐 DNS MX record validation for sender domains
    - 🔍 Heuristic keyword analysis
    - 🔗 Automatic URL extraction
    """)
    
    # Load AI model with progress indicator
    with st.spinner("🤖 Loading AI model... (first run may take 30-60 seconds)"):
        model, model_name = load_phishing_model()
    
    if model and model_name:
        st.success(f"✅ AI Model loaded: `{model_name}`")
    else:
        st.warning("⚠️ AI model unavailable. Using heuristic analysis only.")
    
    st.markdown("---")
    
    # Input fields
    col1, col2 = st.columns([2, 1])
    
    with col1:
        subject = st.text_input(
            "📧 Email Subject",
            placeholder="e.g., URGENT: Your account has been suspended!"
        )
    
    with col2:
        sender = st.text_input(
            "📤 From Email (optional)",
            placeholder="sender@domain.com"
        )
    
    body = st.text_area(
        "📝 Email Body",
        height=200,
        placeholder="Paste the full email content here..."
    )
    
    if st.button("🔬 Analyze Email", type="primary", use_container_width=True):
        if not subject and not body:
            st.warning("⚠️ Please provide at least a subject or body to analyze")
            return
        
        # Combine text for analysis
        full_text = f"{subject}\n\n{body}"
        
        st.markdown("---")
        st.subheader("📊 Analysis Results")
        
        # AI Analysis
        ai_score = None
        if model:
            with st.spinner("🤖 Running AI analysis..."):
                try:
                    # Truncate text if too long for model
                    text_for_model = full_text[:512]
                    
                    result = model(text_for_model)
                    
                    # Extract confidence score
                    if result and len(result) > 0:
                        prediction = result[0]
                        label = prediction.get('label', '').upper()
                        confidence = prediction.get('score', 0)
                        
                        # Interpret based on model
                        if 'phishing' in model_name.lower():
                            # Direct phishing model
                            is_phishing = 'PHISH' in label or 'SPAM' in label
                            ai_score = confidence if is_phishing else (1 - confidence)
                        else:
                            # Sentiment model (fallback) - negative sentiment = suspicious
                            is_negative = 'NEGATIVE' in label
                            ai_score = confidence if is_negative else (1 - confidence) * 0.5
                            
                except Exception as e:
                    st.error(f"AI analysis error: {str(e)}")
                    ai_score = None
        
        # Heuristic Analysis
        heuristic_score, keywords = calculate_heuristic_score(subject, body)
        
        # Display results
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if ai_score is not None:
                ai_percentage = int(ai_score * 100)
                if ai_percentage >= 75:
                    st.metric("🤖 AI Phishing Probability", f"{ai_percentage}%", "🔴 HIGH RISK")
                elif ai_percentage >= 50:
                    st.metric("🤖 AI Phishing Probability", f"{ai_percentage}%", "🟠 MEDIUM")
                else:
                    st.metric("🤖 AI Phishing Probability", f"{ai_percentage}%", "🟢 LOW")
            else:
                st.metric("🤖 AI Analysis", "N/A", "Model unavailable")
        
        with col2:
            # Normalize heuristic score to 0-100
            heuristic_percentage = min(100, int(heuristic_score * 5))
            if heuristic_percentage >= 75:
                st.metric("📊 Heuristic Score", f"{heuristic_percentage}%", "🔴 HIGH")
            elif heuristic_percentage >= 50:
                st.metric("📊 Heuristic Score", f"{heuristic_percentage}%", "🟠 MEDIUM")
            else:
                st.metric("📊 Heuristic Score", f"{heuristic_percentage}%", "🟢 LOW")
        
        with col3:
            # Combined risk level
            if ai_score is not None:
                combined = (ai_score * 100 * 0.7) + (heuristic_percentage * 0.3)
            else:
                combined = heuristic_percentage
            
            if combined >= 70:
                st.metric("⚠️ Overall Risk", "HIGH", "🚨 DANGER")
            elif combined >= 40:
                st.metric("⚠️ Overall Risk", "MEDIUM", "⚠️ CAUTION")
            else:
                st.metric("⚠️ Overall Risk", "LOW", "✅ SAFE")
        
        # Suspicious keywords
        if keywords:
            st.markdown("---")
            st.subheader("🔍 Suspicious Keywords Detected")
            cols = st.columns(5)
            for idx, keyword in enumerate(keywords[:15]):  # Show max 15
                with cols[idx % 5]:
                    st.markdown(f"🔸 `{keyword}`")
        
        # URL extraction and analysis
        urls = extract_urls(full_text)
        if urls:
            st.markdown("---")
            st.subheader("🔗 Extracted URLs")
            st.warning(f"⚠️ Found {len(urls)} URL(s) in email - Verify before clicking!")
            
            for url in urls:
                st.code(url, language=None)
                
                # Check for suspicious patterns in URL
                url_lower = url.lower()
                if any(x in url_lower for x in ['bit.ly', 'tinyurl', 'goo.gl', 'short']):
                    st.error("🚨 Shortened URL detected - High risk!")
                elif re.search(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', url):
                    st.error("🚨 IP address in URL - Very suspicious!")
                elif url.count('-') > 3:
                    st.warning("⚠️ Many hyphens in domain - Suspicious")
        
        # Email domain validation
        if sender:
            st.markdown("---")
            st.subheader("🌐 Sender Domain Validation")
            
            domain = extract_domain_from_email(sender)
            
            if domain:
                with st.spinner(f"Checking MX records for {domain}..."):
                    mx_result = check_mx_records(domain)
                
                # Display result
                if mx_result['valid'] is True:
                    st.success(mx_result['message'])
                    if mx_result['mx_records']:
                        with st.expander("View MX Records"):
                            for mx in mx_result['mx_records']:
                                st.text(f"• {mx}")
                elif mx_result['valid'] is False:
                    st.error(mx_result['message'])
                    st.error("🚨 This is a MAJOR red flag for phishing!")
                else:
                    st.warning(mx_result['message'])
            else:
                st.error("❌ Invalid email format")
        
        # Extract email addresses from body
        body_emails = extract_email_addresses(body)
        if body_emails:
            st.markdown("---")
            st.subheader("📧 Email Addresses in Body")
            st.info(f"Found {len(body_emails)} email address(es)")
            for email in body_emails[:5]:  # Show max 5
                st.code(email)
        
        # Final verdict
        st.markdown("---")
        st.subheader("🎯 Final Verdict")
        
        if combined >= 70:
            st.error("""
            🚨 **HIGH RISK - LIKELY PHISHING**
            
            **DO NOT:**
            - Click any links
            - Download attachments
            - Reply with personal information
            - Enter credentials on linked websites
            
            **ACTION:** Delete this email immediately and report it to your IT security team.
            """)
        elif combined >= 40:
            st.warning("""
            ⚠️ **MEDIUM RISK - SUSPICIOUS**
            
            **Proceed with extreme caution:**
            - Verify sender through alternate communication channel
            - Hover over links without clicking to inspect URLs
            - Look for spelling/grammar errors
            - Check if you were expecting this email
            
            **When in doubt, contact the sender directly using known contact information.**
            """)
        else:
            st.success("""
            ✅ **LOW RISK - APPEARS LEGITIMATE**
            
            **However, always:**
            - Verify unexpected requests
            - Use caution with attachments
            - Check sender address carefully
            - Trust your instincts
            
            **Remember:** Sophisticated phishing attacks can bypass detection!
            """)
    
    # Educational section
    with st.expander("📚 Learn: How to Spot Phishing"):
        st.markdown("""
        ### Common Phishing Indicators:
        
        1. **Urgency/Threats** - "Act now or account will be closed!"
        2. **Generic Greetings** - "Dear Customer" instead of your name
        3. **Suspicious Sender** - Check email address carefully
        4. **Grammar Errors** - Professional companies proofread
        5. **Unexpected Attachments** - Especially .exe, .zip, .js files
        6. **Requests for Information** - Banks never ask for passwords via email
        7. **Too Good to Be True** - You won a lottery you didn't enter
        8. **Mismatched URLs** - Hover to see real destination
        9. **Fake Branding** - Low-quality logos or wrong colors
        10. **Suspicious Links** - Shortened URLs or IP addresses
        
        ### Best Practices:
        - ✅ Enable Two-Factor Authentication (2FA)
        - ✅ Use password managers
        - ✅ Keep software updated
        - ✅ Verify requests through alternate channels
        - ✅ Report phishing to IT/security team
        """)


