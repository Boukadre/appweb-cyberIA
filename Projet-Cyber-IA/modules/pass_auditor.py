"""
Module 3: Password Auditor
Professional password strength analysis with breach checking
"""

import streamlit as st
import hashlib
import requests
import re
from typing import Tuple, Dict, List
import plotly.graph_objects as go


def calculate_password_strength(password: str) -> Dict:
    """
    Calculate comprehensive password strength metrics
    
    Args:
        password: Password to analyze
        
    Returns:
        Dictionary with strength metrics
    """
    length = len(password)
    score = 0
    feedback = []
    warnings = []
    
    # Length analysis
    if length < 8:
        warnings.append("⚠️ Password is too short (minimum 8 characters)")
        score += 0
    elif length < 12:
        feedback.append("✓ Acceptable length")
        score += 15
    elif length < 16:
        feedback.append("✓ Good length")
        score += 25
    else:
        feedback.append("✓ Excellent length")
        score += 35
    
    # Character diversity
    has_lower = bool(re.search(r'[a-z]', password))
    has_upper = bool(re.search(r'[A-Z]', password))
    has_digit = bool(re.search(r'[0-9]', password))
    has_special = bool(re.search(r'[!@#$%^&*(),.?":{}|<>_\-+=\[\]\\\/`~;]', password))
    
    if has_lower:
        score += 10
        feedback.append("✓ Contains lowercase letters")
    else:
        warnings.append("⚠️ Add lowercase letters (a-z)")
    
    if has_upper:
        score += 10
        feedback.append("✓ Contains uppercase letters")
    else:
        warnings.append("⚠️ Add uppercase letters (A-Z)")
    
    if has_digit:
        score += 10
        feedback.append("✓ Contains numbers")
    else:
        warnings.append("⚠️ Add numbers (0-9)")
    
    if has_special:
        score += 15
        feedback.append("✓ Contains special characters")
    else:
        warnings.append("⚠️ Add special characters (!@#$...)")
    
    # Complexity bonus
    char_types = sum([has_lower, has_upper, has_digit, has_special])
    if char_types == 4:
        score += 10
        feedback.append("✓ Excellent character diversity")
    
    # Pattern detection (penalties)
    if re.search(r'(.)\1{2,}', password):
        score -= 10
        warnings.append("⚠️ Repeated characters detected")
    
    if re.search(r'(123|234|345|456|567|678|789|890|abc|bcd|cde|def)', password.lower()):
        score -= 15
        warnings.append("⚠️ Sequential patterns detected")
    
    common_words = ['password', 'admin', 'user', 'login', 'welcome', '1234', 'qwerty']
    if any(word in password.lower() for word in common_words):
        score -= 20
        warnings.append("⚠️ Common word/pattern detected")
    
    # Ensure score is between 0-100
    score = max(0, min(100, score))
    
    # Determine strength level
    if score >= 80:
        strength_level = "Excellent"
        strength_color = "#00cc00"
        strength_emoji = "🟢"
    elif score >= 60:
        strength_level = "Strong"
        strength_color = "#66cc00"
        strength_emoji = "🟡"
    elif score >= 40:
        strength_level = "Moderate"
        strength_color = "#ffcc00"
        strength_emoji = "🟠"
    elif score >= 20:
        strength_level = "Weak"
        strength_color = "#ff6600"
        strength_emoji = "🔴"
    else:
        strength_level = "Very Weak"
        strength_color = "#cc0000"
        strength_emoji = "🔴"
    
    # Calculate crack time
    crack_time = estimate_crack_time(password)
    
    return {
        'score': score,
        'strength_level': strength_level,
        'strength_color': strength_color,
        'strength_emoji': strength_emoji,
        'feedback': feedback,
        'warnings': warnings,
        'crack_time': crack_time
    }


def estimate_crack_time(password: str) -> str:
    """
    Estimate time to crack password using brute force
    
    Args:
        password: Password to analyze
        
    Returns:
        Human-readable crack time estimate
    """
    length = len(password)
    
    # Calculate character set size
    charset_size = 0
    if re.search(r'[a-z]', password):
        charset_size += 26
    if re.search(r'[A-Z]', password):
        charset_size += 26
    if re.search(r'[0-9]', password):
        charset_size += 10
    if re.search(r'[!@#$%^&*(),.?":{}|<>_\-+=\[\]\\\/`~;]', password):
        charset_size += 32
    
    if charset_size == 0:
        return "Instantly (empty)"
    
    # Calculate possible combinations
    combinations = charset_size ** length
    
    # Assume 10 billion attempts per second (modern GPU)
    attempts_per_second = 10_000_000_000
    seconds = combinations / attempts_per_second / 2  # Average case
    
    # Convert to human-readable format
    if seconds < 1:
        return "< 1 second"
    elif seconds < 60:
        return f"{int(seconds)} seconds"
    elif seconds < 3600:
        return f"{int(seconds/60)} minutes"
    elif seconds < 86400:
        return f"{int(seconds/3600)} hours"
    elif seconds < 2592000:  # 30 days
        return f"{int(seconds/86400)} days"
    elif seconds < 31536000:  # 1 year
        return f"{int(seconds/2592000)} months"
    elif seconds < 31536000 * 100:
        return f"{int(seconds/31536000)} years"
    elif seconds < 31536000 * 1000000:
        return f"{int(seconds/(31536000*1000)):.1f} thousand years"
    elif seconds < 31536000 * 1000000000:
        return f"{int(seconds/(31536000*1000000)):.1f} million years"
    else:
        return "Billions of years"


def check_password_pwned(password: str) -> Tuple[bool, int, str]:
    """
    Check if password appears in HaveIBeenPwned database
    Uses k-Anonymity model (only first 5 chars of hash sent)
    
    Args:
        password: Password to check
        
    Returns:
        Tuple of (is_pwned, occurrence_count, status_message)
    """
    try:
        # Generate SHA-1 hash
        sha1_hash = hashlib.sha1(password.encode('utf-8')).hexdigest().upper()
        prefix = sha1_hash[:5]
        suffix = sha1_hash[5:]
        
        # Query API with first 5 characters only (k-Anonymity)
        url = f"https://api.pwnedpasswords.com/range/{prefix}"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            # Search for our suffix in the results
            hashes = response.text.split('\r\n')
            for hash_line in hashes:
                if ':' in hash_line:
                    hash_suffix, count = hash_line.split(':')
                    if hash_suffix == suffix:
                        return True, int(count), "Found in breach database"
            
            return False, 0, "Not found in any known breaches"
        else:
            return False, -1, f"API Error: HTTP {response.status_code}"
            
    except requests.exceptions.Timeout:
        return False, -1, "Connection timeout"
    except Exception as e:
        return False, -1, f"Error: {str(e)}"


def create_gauge_chart(score: int, color: str) -> go.Figure:
    """
    Create a professional gauge chart for password strength
    
    Args:
        score: Password strength score (0-100)
        color: Color for the gauge
        
    Returns:
        Plotly figure object
    """
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=score,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': "Password Strength Score", 'font': {'size': 20}},
        number={'suffix': "/100", 'font': {'size': 40}},
        gauge={
            'axis': {'range': [None, 100], 'tickwidth': 1, 'tickcolor': "darkgray"},
            'bar': {'color': color},
            'bgcolor': "white",
            'borderwidth': 2,
            'bordercolor': "gray",
            'steps': [
                {'range': [0, 20], 'color': '#ffcccc'},
                {'range': [20, 40], 'color': '#ffe6cc'},
                {'range': [40, 60], 'color': '#fff9cc'},
                {'range': [60, 80], 'color': '#e6ffcc'},
                {'range': [80, 100], 'color': '#ccffcc'}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 90
            }
        }
    ))
    
    fig.update_layout(
        height=300,
        margin=dict(l=20, r=20, t=50, b=20),
        paper_bgcolor="rgba(0,0,0,0)",
        font={'color': "darkblue", 'family': "Arial"}
    )
    
    return fig


def render_password_auditor():
    """Main rendering function for Password Auditor module"""
    
    st.header("🔑 Password Auditor")
    st.markdown("""
    **Professional password strength analysis and breach detection**
    
    This module provides:
    - 📊 Comprehensive strength scoring (0-100)
    - ⏱️ Realistic crack time estimation
    - 🔍 HaveIBeenPwned breach checking (k-Anonymity)
    - 📈 Visual gauge chart
    - 💡 Actionable security recommendations
    """)
    
    st.info("🔒 **Privacy**: Your password is never stored or transmitted in plain text. Breach checking uses k-Anonymity.")
    
    st.markdown("---")
    
    # Password input
    password = st.text_input(
        "🔐 Enter password to analyze",
        type="password",
        help="Your password is analyzed locally and never stored",
        max_chars=128
    )
    
    # Option to show password
    show_password = st.checkbox("👁️ Show password", value=False)
    
    if show_password and password:
        st.code(password, language=None)
    
    if password:
        # Calculate strength
        with st.spinner("Analyzing password..."):
            strength_data = calculate_password_strength(password)
        
        st.markdown("---")
        
        # Display gauge chart
        col1, col2 = st.columns([2, 1])
        
        with col1:
            gauge_fig = create_gauge_chart(
                strength_data['score'],
                strength_data['strength_color']
            )
            st.plotly_chart(gauge_fig, use_container_width=True)
        
        with col2:
            st.markdown("<br>", unsafe_allow_html=True)
            st.metric(
                "Strength Level",
                strength_data['strength_level'],
                strength_data['strength_emoji']
            )
            st.metric(
                "Crack Time Estimate",
                strength_data['crack_time']
            )
        
        # Feedback section
        st.markdown("---")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if strength_data['feedback']:
                st.subheader("✅ Strengths")
                for item in strength_data['feedback']:
                    st.success(item)
        
        with col2:
            if strength_data['warnings']:
                st.subheader("⚠️ Improvements")
                for item in strength_data['warnings']:
                    st.warning(item)
        
        # HaveIBeenPwned check
        st.markdown("---")
        st.subheader("🔍 Breach Database Check")
        
        with st.spinner("Checking HaveIBeenPwned database (k-Anonymity)..."):
            is_pwned, count, message = check_password_pwned(password)
        
        if count == -1:
            st.warning(f"⚠️ {message}")
            st.info("Could not verify breach status. This doesn't mean the password is safe.")
        elif is_pwned:
            st.error(f"🚨 **CRITICAL ALERT**: This password has been found in **{count:,}** data breaches!")
            st.error("**DO NOT USE THIS PASSWORD ANYWHERE!**")
            st.markdown("""
            ### Immediate Actions Required:
            1. ❌ Never use this password
            2. 🔄 Change it immediately if you're using it anywhere
            3. 🔐 Use a unique password for each account
            4. 📱 Enable Two-Factor Authentication (2FA)
            5. 🛡️ Consider using a password manager
            """)
        else:
            st.success(f"✅ {message}")
            st.info("This password hasn't been found in known data breaches, but that doesn't guarantee it's secure. Check the strength score above.")
        
        # Password recommendations
        st.markdown("---")
        with st.expander("💡 Password Best Practices"):
            st.markdown("""
            ### Creating Strong Passwords:
            
            #### ✅ DO:
            - Use **at least 12-16 characters** (longer is better)
            - Mix **uppercase, lowercase, numbers, and symbols**
            - Use **unique passwords** for each account
            - Consider **passphrases** (e.g., "Coffee!Morning@2024#Sunshine")
            - Use a **password manager** (Bitwarden, 1Password, LastPass)
            - Enable **Two-Factor Authentication (2FA)** everywhere possible
            
            #### ❌ DON'T:
            - Use personal information (birthdays, names, addresses)
            - Use common words or phrases
            - Use sequential patterns (123456, abcdef)
            - Reuse passwords across multiple sites
            - Share passwords via email or text
            - Write passwords on sticky notes
            
            ### Password Manager Benefits:
            - 🔐 Generate strong, unique passwords
            - 💾 Securely store all passwords
            - 🔄 Auto-fill login forms
            - 🔍 Alert you to breached passwords
            - 📱 Sync across devices
            
            ### Recommended Tools:
            - **Bitwarden** (Open source, free)
            - **1Password** (Premium, family plans)
            - **LastPass** (Free tier available)
            - **KeePassXC** (Offline, open source)
            """)
    
    else:
        # Show example passwords
        st.markdown("---")
        st.subheader("🧪 Try These Examples")
        
        examples = [
            ("password123", "Very Weak", "🔴"),
            ("P@ssw0rd", "Weak", "🔴"),
            ("MyDog2024!", "Moderate", "🟠"),
            ("C0mpl3x!P@ssw0rd", "Strong", "🟡"),
            ("Tr0ub4dor&3#Xk9$mQ", "Excellent", "🟢")
        ]
        
        cols = st.columns(len(examples))
        for idx, (pwd, level, emoji) in enumerate(examples):
            with cols[idx]:
                if st.button(f"{emoji} Test", key=f"example_{idx}", use_container_width=True):
                    st.rerun()
                st.caption(f"`{pwd}`")
                st.caption(level)
    
    # Educational footer
    st.markdown("---")
    st.caption("🔒 **Privacy Note**: Password analysis is performed locally. Only a SHA-1 hash prefix (5 chars) is sent to HaveIBeenPwned using k-Anonymity protocol.")


