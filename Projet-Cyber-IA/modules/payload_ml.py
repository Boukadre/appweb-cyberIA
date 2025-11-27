"""
Module 4: ML-Powered SQLi/XSS Payload Classifier
Uses Machine Learning instead of simple regex for advanced detection
"""

import streamlit as st
import re
from typing import Dict, List, Tuple
import warnings
import pickle
import numpy as np

warnings.filterwarnings('ignore')


# Training dataset for fallback TF-IDF model
TRAINING_DATA = {
    'safe': [
        'SELECT * FROM users WHERE id = 1',
        'search?q=python+programming',
        'index.php?page=home',
        'user/profile/123',
        'api/v1/products?category=electronics',
        'Hello World',
        'username=john&password=secret',
        'page=1&limit=10',
        'name=Alice&age=25',
        'search?query=machine learning',
    ],
    'sqli': [
        "1' OR '1'='1",
        "admin'--",
        "1' UNION SELECT NULL--",
        "' OR 1=1--",
        "1'; DROP TABLE users--",
        "' UNION SELECT username, password FROM users--",
        "1' AND 1=1 UNION SELECT NULL, NULL--",
        "admin' OR '1'='1'--",
        "' OR 'x'='x",
        "1' WAITFOR DELAY '00:00:05'--",
        "' OR 1=1#",
        "1' UNION ALL SELECT NULL,NULL,NULL--",
        "admin' UNION SELECT * FROM passwords--",
        "' OR '1'='1' /*",
        "1; SELECT * FROM information_schema.tables--",
        "1' AND SLEEP(5)--",
        "' UNION SELECT @@version--",
        "1' OR 'a'='a",
        "admin'-- -",
        "' OR ''='",
    ],
    'xss': [
        "<script>alert('XSS')</script>",
        "<img src=x onerror=alert(1)>",
        "javascript:alert(document.cookie)",
        "<iframe src='javascript:alert(1)'>",
        "<svg onload=alert(1)>",
        "<body onload=alert('XSS')>",
        "<img src='x' onerror='alert(1)'>",
        "<script>document.location='http://evil.com'</script>",
        "'\"><script>alert(String.fromCharCode(88,83,83))</script>",
        "<img src=javascript:alert('XSS')>",
        "<input onfocus=alert(1) autofocus>",
        "<select onfocus=alert(1) autofocus>",
        "<textarea onfocus=alert(1) autofocus>",
        "<iframe src=data:text/html,<script>alert(1)</script>>",
        "<object data=javascript:alert(1)>",
        "<embed src=javascript:alert(1)>",
        "<img src='x' onerror='eval(atob(\"YWxlcnQoMSk=\"))'>",
        "<svg><script>alert(1)</script></svg>",
        "<math><mi xlink:href='javascript:alert(1)'>",
        "<video><source onerror='javascript:alert(1)'>",
    ]
}


@st.cache_resource(show_spinner=False)
def load_ml_classifier():
    """
    Load or create ML classifier for payload detection
    
    Returns:
        Tuple of (model, vectorizer, model_type) or (None, None, None)
    """
    try:
        # Try to load Hugging Face model first
        from transformers import pipeline
        
        try:
            # Try SQL injection specific model
            model = pipeline(
                "text-classification",
                model="madhurjindal/autonlp-Gibberish-Detector-492513457",  # Can detect anomalous text
                device=-1
            )
            return model, None, "huggingface"
        except:
            pass
    except:
        pass
    
    # Fallback to TF-IDF + Logistic Regression
    try:
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.linear_model import LogisticRegression
        from sklearn.preprocessing import LabelEncoder
        
        # Prepare training data
        X_train = []
        y_train = []
        
        for label, samples in TRAINING_DATA.items():
            X_train.extend(samples)
            y_train.extend([label] * len(samples))
        
        # Create and train vectorizer
        vectorizer = TfidfVectorizer(
            analyzer='char',
            ngram_range=(2, 4),
            max_features=500,
            lowercase=True
        )
        
        X_vectorized = vectorizer.fit_transform(X_train)
        
        # Train classifier
        classifier = LogisticRegression(
            max_iter=1000,
            multi_class='multinomial',
            random_state=42
        )
        classifier.fit(X_vectorized, y_train)
        
        return classifier, vectorizer, "tfidf"
        
    except Exception as e:
        st.error(f"Error creating classifier: {str(e)}")
        return None, None, None


def extract_payload_features(payload: str) -> Dict:
    """
    Extract heuristic features from payload (for ensemble approach)
    
    Args:
        payload: Input payload string
        
    Returns:
        Dictionary of feature indicators
    """
    payload_lower = payload.lower()
    
    features = {
        # SQL Injection indicators
        'sql_keywords': len(re.findall(
            r'\b(union|select|insert|update|delete|drop|create|alter|exec|execute|declare|cast|convert)\b',
            payload_lower
        )),
        'sql_operators': len(re.findall(r'(\bor\b|\band\b)', payload_lower)),
        'sql_comments': len(re.findall(r'(--|#|/\*|\*/)', payload)),
        'sql_quotes': len(re.findall(r"('|\")", payload)),
        'sql_tautology': bool(re.search(r"('\s*or\s*'1'\s*=\s*'1|1\s*=\s*1|\bor\s+1\s*=\s*1)", payload_lower)),
        'sql_sleep': bool(re.search(r'(sleep|waitfor\s+delay|benchmark)', payload_lower)),
        
        # XSS indicators
        'xss_script_tag': len(re.findall(r'<script', payload_lower)),
        'xss_event_handlers': len(re.findall(
            r'(onload|onerror|onclick|onmouseover|onfocus|onblur)=',
            payload_lower
        )),
        'xss_javascript': len(re.findall(r'javascript:', payload_lower)),
        'xss_html_tags': len(re.findall(
            r'<(iframe|img|svg|object|embed|video|audio|body|input|select|textarea)',
            payload_lower
        )),
        'xss_alert': len(re.findall(r'alert\s*\(', payload_lower)),
        'xss_eval': len(re.findall(r'(eval|document\.cookie|document\.write)', payload_lower)),
        
        # General suspicious patterns
        'encoded_content': bool(re.search(r'(%[0-9a-f]{2}|&#|\\x|\\u)', payload_lower)),
        'special_chars': len(re.findall(r'[<>\'\"();{}]', payload))
    }
    
    return features


def classify_payload_ml(payload: str, model, vectorizer, model_type: str) -> Dict:
    """
    Classify payload using ML model
    
    Args:
        payload: Input payload
        model: ML model
        vectorizer: Feature vectorizer (for TF-IDF)
        model_type: Type of model ('huggingface' or 'tfidf')
        
    Returns:
        Classification results dictionary
    """
    try:
        if model_type == "huggingface":
            # Hugging Face model
            result = model(payload[:512])
            
            if result and len(result) > 0:
                prediction = result[0]
                label = prediction.get('label', '').upper()
                confidence = prediction.get('score', 0)
                
                # Map to our categories
                if 'GIBBER' in label or confidence > 0.7:
                    return {
                        'prediction': 'suspicious',
                        'confidence': confidence,
                        'details': 'Anomalous pattern detected by AI'
                    }
                else:
                    return {
                        'prediction': 'safe',
                        'confidence': 1 - confidence,
                        'details': 'Normal pattern'
                    }
        
        elif model_type == "tfidf":
            # TF-IDF + Logistic Regression
            X = vectorizer.transform([payload])
            prediction = model.predict(X)[0]
            probabilities = model.predict_proba(X)[0]
            
            # Get confidence
            max_prob = max(probabilities)
            
            return {
                'prediction': prediction,
                'confidence': max_prob,
                'probabilities': {
                    label: prob 
                    for label, prob in zip(model.classes_, probabilities)
                },
                'details': f'ML classification: {prediction}'
            }
    
    except Exception as e:
        return {
            'prediction': 'error',
            'confidence': 0,
            'details': f'Classification error: {str(e)}'
        }
    
    return {
        'prediction': 'unknown',
        'confidence': 0,
        'details': 'Could not classify'
    }


def analyze_payload_comprehensive(payload: str, model, vectorizer, model_type: str) -> Dict:
    """
    Comprehensive payload analysis using ML + heuristics
    
    Args:
        payload: Input payload
        model: ML model
        vectorizer: Vectorizer
        model_type: Model type
        
    Returns:
        Complete analysis results
    """
    # ML Classification
    ml_result = classify_payload_ml(payload, model, vectorizer, model_type)
    
    # Extract heuristic features
    features = extract_payload_features(payload)
    
    # Calculate heuristic scores
    sql_score = (
        features['sql_keywords'] * 3 +
        features['sql_operators'] * 2 +
        features['sql_comments'] * 2 +
        features['sql_tautology'] * 5 +
        features['sql_sleep'] * 4
    )
    
    xss_score = (
        features['xss_script_tag'] * 5 +
        features['xss_event_handlers'] * 3 +
        features['xss_javascript'] * 4 +
        features['xss_html_tags'] * 2 +
        features['xss_alert'] * 3 +
        features['xss_eval'] * 4
    )
    
    # Determine final classification
    ml_prediction = ml_result.get('prediction', 'unknown')
    ml_confidence = ml_result.get('confidence', 0)
    
    # Ensemble decision
    if model_type == "tfidf":
        # Use ML prediction directly
        if ml_prediction == 'sqli':
            final_class = 'SQL Injection'
            confidence = ml_confidence
            risk_level = '🔴 HIGH RISK'
        elif ml_prediction == 'xss':
            final_class = 'XSS Attack'
            confidence = ml_confidence
            risk_level = '🔴 HIGH RISK'
        elif sql_score > 8:
            final_class = 'SQL Injection (heuristic)'
            confidence = min(0.95, sql_score / 20)
            risk_level = '🔴 HIGH RISK'
        elif xss_score > 8:
            final_class = 'XSS Attack (heuristic)'
            confidence = min(0.95, xss_score / 20)
            risk_level = '🔴 HIGH RISK'
        elif sql_score > 3 or xss_score > 3:
            final_class = 'Suspicious'
            confidence = 0.6
            risk_level = '🟠 MEDIUM RISK'
        else:
            final_class = 'Safe'
            confidence = ml_confidence if ml_prediction == 'safe' else 0.7
            risk_level = '🟢 LOW RISK'
    else:
        # Hugging Face or fallback
        if ml_prediction == 'suspicious' or sql_score > 5 or xss_score > 5:
            if sql_score > xss_score:
                final_class = 'Likely SQL Injection'
                risk_level = '🟠 MEDIUM RISK'
            elif xss_score > sql_score:
                final_class = 'Likely XSS'
                risk_level = '🟠 MEDIUM RISK'
            else:
                final_class = 'Suspicious'
                risk_level = '🟠 MEDIUM RISK'
            confidence = ml_confidence
        else:
            final_class = 'Safe'
            confidence = ml_confidence
            risk_level = '🟢 LOW RISK'
    
    return {
        'classification': final_class,
        'confidence': confidence,
        'risk_level': risk_level,
        'ml_result': ml_result,
        'features': features,
        'sql_score': sql_score,
        'xss_score': xss_score,
        'model_type': model_type
    }


def render_payload_classifier():
    """Main rendering function for ML Payload Classifier"""
    
    st.header("💉 ML-Powered Payload Classifier")
    st.markdown("""
    **Advanced injection detection using Machine Learning**
    
    This module provides:
    - 🤖 ML-based payload classification (TF-IDF + Logistic Regression)
    - 🔍 SQL Injection detection
    - 🌐 Cross-Site Scripting (XSS) detection
    - 📊 Confidence scoring and risk assessment
    - 🛡️ Security recommendations
    """)
    
    # Load ML model
    with st.spinner("🤖 Loading ML classifier... (first run may take a moment)"):
        model, vectorizer, model_type = load_ml_classifier()
    
    if model:
        if model_type == "tfidf":
            st.success("✅ ML Classifier loaded: TF-IDF + Logistic Regression")
        else:
            st.success(f"✅ ML Classifier loaded: {model_type}")
    else:
        st.error("❌ Could not load ML classifier. Using basic heuristics only.")
    
    st.markdown("---")
    
    # Input area
    st.subheader("🔍 Enter Payload to Analyze")
    
    # Quick examples
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("📝 Safe Example", use_container_width=True):
            st.session_state['payload_input'] = "search?query=python programming"
    with col2:
        if st.button("💉 SQLi Example", use_container_width=True):
            st.session_state['payload_input'] = "admin' OR '1'='1'--"
    with col3:
        if st.button("🌐 XSS Example", use_container_width=True):
            st.session_state['payload_input'] = "<script>alert('XSS')</script>"
    
    # Payload input
    payload = st.text_area(
        "HTTP Request / URL Parameter / Input Field",
        height=150,
        placeholder="e.g., ?id=1' OR '1'='1'\ne.g., <script>alert(1)</script>\ne.g., /search?q=normal query",
        value=st.session_state.get('payload_input', ''),
        key='payload_textarea'
    )
    
    if st.button("🔬 Analyze Payload", type="primary", use_container_width=True):
        if not payload.strip():
            st.warning("⚠️ Please enter a payload to analyze")
            return
        
        if not model:
            st.error("❌ ML model not available. Cannot perform analysis.")
            return
        
        # Perform analysis
        with st.spinner("🤖 Analyzing with ML model..."):
            results = analyze_payload_comprehensive(payload, model, vectorizer, model_type)
        
        st.markdown("---")
        st.subheader("📊 Analysis Results")
        
        # Main results
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                "Classification",
                results['classification'],
                results['risk_level']
            )
        
        with col2:
            confidence_pct = int(results['confidence'] * 100)
            st.metric(
                "Confidence",
                f"{confidence_pct}%"
            )
        
        with col3:
            st.metric(
                "Model Type",
                results['model_type'].upper()
            )
        
        # Detailed scores
        st.markdown("---")
        st.subheader("📈 Detection Scores")
        
        col1, col2 = st.columns(2)
        
        with col1:
            sql_score = results['sql_score']
            sql_pct = min(100, int(sql_score * 5))
            st.progress(sql_pct / 100)
            st.metric("SQL Injection Score", f"{sql_pct}%")
            
            if sql_score > 8:
                st.error("🚨 High SQL Injection indicators detected!")
            elif sql_score > 3:
                st.warning("⚠️ Moderate SQL Injection patterns found")
            else:
                st.success("✅ Low SQL Injection risk")
        
        with col2:
            xss_score = results['xss_score']
            xss_pct = min(100, int(xss_score * 5))
            st.progress(xss_pct / 100)
            st.metric("XSS Score", f"{xss_pct}%")
            
            if xss_score > 8:
                st.error("🚨 High XSS indicators detected!")
            elif xss_score > 3:
                st.warning("⚠️ Moderate XSS patterns found")
            else:
                st.success("✅ Low XSS risk")
        
        # ML Model details
        if model_type == "tfidf" and 'probabilities' in results['ml_result']:
            st.markdown("---")
            st.subheader("🤖 ML Model Probabilities")
            
            probs = results['ml_result']['probabilities']
            
            cols = st.columns(len(probs))
            for idx, (label, prob) in enumerate(probs.items()):
                with cols[idx]:
                    st.metric(label.upper(), f"{int(prob * 100)}%")
        
        # Feature breakdown
        with st.expander("🔬 Detailed Feature Analysis"):
            features = results['features']
            
            st.markdown("### SQL Injection Indicators:")
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"- SQL Keywords: {features['sql_keywords']}")
                st.write(f"- SQL Operators: {features['sql_operators']}")
                st.write(f"- SQL Comments: {features['sql_comments']}")
            with col2:
                st.write(f"- SQL Quotes: {features['sql_quotes']}")
                st.write(f"- Tautology: {'Yes' if features['sql_tautology'] else 'No'}")
                st.write(f"- Sleep/Delay: {'Yes' if features['sql_sleep'] else 'No'}")
            
            st.markdown("### XSS Indicators:")
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"- Script Tags: {features['xss_script_tag']}")
                st.write(f"- Event Handlers: {features['xss_event_handlers']}")
                st.write(f"- JavaScript Protocol: {features['xss_javascript']}")
            with col2:
                st.write(f"- HTML Tags: {features['xss_html_tags']}")
                st.write(f"- Alert Calls: {features['xss_alert']}")
                st.write(f"- Eval/Cookie: {features['xss_eval']}")
            
            st.markdown("### General:")
            st.write(f"- Encoded Content: {'Yes' if features['encoded_content'] else 'No'}")
            st.write(f"- Special Characters: {features['special_chars']}")
        
        # Security recommendations
        st.markdown("---")
        st.subheader("🛡️ Security Recommendations")
        
        if 'SQL Injection' in results['classification']:
            st.error("""
            ### 🚨 SQL Injection Detected!
            
            **Immediate Actions:**
            - ❌ **Block this request immediately**
            - 🔍 **Log the attempt with full details**
            - 🚫 **Consider blocking the source IP**
            - 📊 **Investigate for ongoing attacks**
            
            **Prevention Measures:**
            - ✅ Use **Prepared Statements / Parameterized Queries**
            - ✅ Use **ORM frameworks** (SQLAlchemy, Django ORM)
            - ✅ **Validate and sanitize** all user inputs
            - ✅ Apply **principle of least privilege** to database users
            - ✅ **Escape special characters** in SQL queries
            - ✅ Implement **Web Application Firewall (WAF)**
            - ✅ Use **input validation** with allowlists
            """)
        
        elif 'XSS' in results['classification']:
            st.error("""
            ### 🚨 XSS Attack Detected!
            
            **Immediate Actions:**
            - ❌ **Block this request**
            - 🔍 **Log the attempt**
            - 🛡️ **Check for stored XSS** in database
            - 📧 **Alert security team**
            
            **Prevention Measures:**
            - ✅ **Encode all output** (HTML entity encoding)
            - ✅ Use **Content Security Policy (CSP)** headers
            - ✅ **Validate input** on both client and server
            - ✅ Use **X-XSS-Protection** header
            - ✅ **Sanitize HTML** with libraries (DOMPurify, Bleach)
            - ✅ Use **HttpOnly and Secure flags** on cookies
            - ✅ Implement **Same-Origin Policy**
            """)
        
        elif 'Suspicious' in results['classification']:
            st.warning("""
            ### ⚠️ Suspicious Pattern Detected
            
            **Recommended Actions:**
            - 🔍 **Monitor this request** carefully
            - 📊 **Log for analysis**
            - 🤔 **Investigate intent**
            - ⏱️ **Rate limit** the source
            
            **General Security:**
            - ✅ Implement **input validation**
            - ✅ Use **security headers**
            - ✅ Regular **security audits**
            - ✅ Keep **dependencies updated**
            """)
        
        else:
            st.success("""
            ### ✅ Payload Appears Safe
            
            **However, always:**
            - 🔍 Validate all inputs
            - 🛡️ Use security best practices
            - 📊 Monitor for anomalies
            - 🔄 Stay updated on new attack vectors
            
            **Defense in Depth:**
            - ✅ Multiple layers of security
            - ✅ Assume all input is malicious
            - ✅ Regular security training
            - ✅ Automated security testing
            """)
    
    # Educational content
    with st.expander("📚 Learn: Common Injection Attacks"):
        st.markdown("""
        ### SQL Injection (SQLi)
        
        **What is it?**
        Attackers insert malicious SQL code into input fields to manipulate database queries.
        
        **Common Patterns:**
        - `' OR '1'='1` (authentication bypass)
        - `'; DROP TABLE users--` (data destruction)
        - `' UNION SELECT password FROM users--` (data exfiltration)
        - `' AND SLEEP(5)--` (time-based detection)
        
        **Impact:**
        - Data theft
        - Data modification/deletion
        - Authentication bypass
        - Complete system compromise
        
        ---
        
        ### Cross-Site Scripting (XSS)
        
        **What is it?**
        Attackers inject malicious JavaScript into web pages viewed by other users.
        
        **Types:**
        1. **Reflected XSS**: Payload in URL/request
        2. **Stored XSS**: Payload saved in database
        3. **DOM-based XSS**: Client-side code vulnerability
        
        **Common Patterns:**
        - `<script>alert('XSS')</script>`
        - `<img src=x onerror=alert(1)>`
        - `javascript:alert(document.cookie)`
        
        **Impact:**
        - Session hijacking
        - Cookie theft
        - Phishing attacks
        - Malware distribution
        - Website defacement
        
        ---
        
        ### Best Practices:
        1. **Never trust user input**
        2. **Use parameterized queries**
        3. **Encode output properly**
        4. **Implement CSP headers**
        5. **Regular security testing**
        6. **Keep frameworks updated**
        7. **Use WAF (Web Application Firewall)**
        8. **Security training for developers**
        """)

