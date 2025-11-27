"""
Blue Team Toolkit - Web App de Cyber-Défense
Application Streamlit modulaire pour l'analyse de sécurité test
"""

import streamlit as st
import pandas as pd
import requests
import re
import hashlib
from datetime import datetime
from collections import Counter
from typing import List, Dict, Tuple, Optional
import os

# Configuration de la page
st.set_page_config(
    page_title="🛡️ Blue Team Toolkit",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================================
# CONFIGURATION DES CLÉS API
# ============================================================================

def get_api_key(key_name: str) -> Optional[str]:
    """Récupère une clé API depuis secrets ou variables d'environnement"""
    try:
        # Essayer d'abord depuis streamlit secrets
        if hasattr(st, 'secrets') and key_name in st.secrets:
            return st.secrets[key_name]
    except:
        pass
    
    # Essayer depuis les variables d'environnement
    return os.getenv(key_name)

ABUSEIPDB_API_KEY = get_api_key("ABUSEIPDB_API_KEY")
VIRUSTOTAL_API_KEY = get_api_key("VIRUSTOTAL_API_KEY")

# ============================================================================
# MODULE 1 : SSH BRUTE-FORCE DETECTOR & IP REPUTATION
# ============================================================================

def parse_auth_log(log_content: str) -> pd.DataFrame:
    """Parse un fichier auth.log et extrait les tentatives échouées"""
    failed_ips = []
    
    # Pattern pour détecter les échecs d'authentification SSH
    patterns = [
        r'Failed password for .* from ([\d\.]+)',
        r'authentication failure.*rhost=([\d\.]+)',
        r'Invalid user .* from ([\d\.]+)'
    ]
    
    for line in log_content.split('\n'):
        for pattern in patterns:
            match = re.search(pattern, line)
            if match:
                ip = match.group(1)
                failed_ips.append(ip)
                break
    
    if not failed_ips:
        return pd.DataFrame()
    
    # Compter les occurrences
    ip_counts = Counter(failed_ips)
    
    df = pd.DataFrame([
        {"IP Address": ip, "Failed Attempts": count}
        for ip, count in ip_counts.most_common()
    ])
    
    return df

def check_ip_reputation(ip: str) -> Dict:
    """Interroge AbuseIPDB pour obtenir la réputation d'une IP"""
    if not ABUSEIPDB_API_KEY:
        return {"error": "API Key manquante"}
    
    url = "https://api.abuseipdb.com/api/v2/check"
    headers = {
        "Key": ABUSEIPDB_API_KEY,
        "Accept": "application/json"
    }
    params = {
        "ipAddress": ip,
        "maxAgeInDays": 90
    }
    
    try:
        response = requests.get(url, headers=headers, params=params, timeout=10)
        if response.status_code == 200:
            data = response.json()["data"]
            return {
                "ip": ip,
                "abuseConfidenceScore": data.get("abuseConfidenceScore", 0),
                "country": data.get("countryCode", "Unknown"),
                "usageType": data.get("usageType", "Unknown"),
                "totalReports": data.get("totalReports", 0)
            }
        else:
            return {"error": f"HTTP {response.status_code}"}
    except Exception as e:
        return {"error": str(e)}

def module_ssh_bruteforce():
    """Module 1: SSH Brute-force Detector"""
    st.header("🔒 SSH Brute-force Detector & IP Reputation")
    st.markdown("**Analysez vos logs SSH pour détecter les tentatives d'intrusion**")
    
    uploaded_file = st.file_uploader(
        "📁 Uploadez votre fichier de logs (auth.log)",
        type=['log', 'txt'],
        help="Format attendu: /var/log/auth.log ou similaire"
    )
    
    if uploaded_file:
        log_content = uploaded_file.read().decode('utf-8', errors='ignore')
        
        with st.spinner("🔍 Analyse des logs en cours..."):
            df = parse_auth_log(log_content)
        
        if df.empty:
            st.warning("⚠️ Aucune tentative d'authentification échouée détectée dans ce fichier.")
            return
        
        st.success(f"✅ {len(df)} adresses IP uniques détectées avec des tentatives échouées")
        
        # Afficher le tableau des top attackers
        st.subheader("📊 Top Attacking IPs")
        st.dataframe(df, use_container_width=True)
        
        # Analyse de réputation pour les 3 premières IPs
        st.subheader("🌍 Réputation des IPs (via AbuseIPDB)")
        
        if not ABUSEIPDB_API_KEY:
            st.error("❌ Clé API AbuseIPDB manquante. Configurez ABUSEIPDB_API_KEY dans .streamlit/secrets.toml ou .env")
            return
        
        top_ips = df.head(3)["IP Address"].tolist()
        
        col1, col2, col3 = st.columns(3)
        columns = [col1, col2, col3]
        
        for idx, ip in enumerate(top_ips):
            with columns[idx]:
                with st.spinner(f"Vérification de {ip}..."):
                    reputation = check_ip_reputation(ip)
                
                if "error" in reputation:
                    st.error(f"Erreur: {reputation['error']}")
                else:
                    score = reputation["abuseConfidenceScore"]
                    
                    # Déterminer la couleur selon le score
                    if score >= 75:
                        color = "🔴"
                        risk = "CRITIQUE"
                    elif score >= 50:
                        color = "🟠"
                        risk = "ÉLEVÉ"
                    elif score >= 25:
                        color = "🟡"
                        risk = "MOYEN"
                    else:
                        color = "🟢"
                        risk = "FAIBLE"
                    
                    st.metric(
                        label=f"{color} {ip}",
                        value=f"{score}%",
                        delta=risk
                    )
                    st.caption(f"🌍 Pays: {reputation['country']}")
                    st.caption(f"📝 Rapports: {reputation['totalReports']}")

# ============================================================================
# MODULE 2 : PHISHING EMAIL CLASSIFIER
# ============================================================================

def extract_urls(text: str) -> List[str]:
    """Extrait toutes les URLs d'un texte"""
    url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
    urls = re.findall(url_pattern, text)
    return urls

def calculate_phishing_score(subject: str, body: str) -> Tuple[int, List[str]]:
    """Calcule un score de suspicion de phishing"""
    text = (subject + " " + body).lower()
    
    suspicious_keywords = {
        'urgent': 3,
        'immédiat': 3,
        'immediatement': 3,
        'immediately': 3,
        'verify': 2,
        'vérifier': 2,
        'vérification': 2,
        'compte': 2,
        'account': 2,
        'suspended': 3,
        'suspendu': 3,
        'blocked': 3,
        'bloqué': 3,
        'confirm': 2,
        'confirmer': 2,
        'password': 2,
        'mot de passe': 2,
        'banking': 3,
        'banque': 3,
        'paypal': 2,
        'amazon': 2,
        'microsoft': 2,
        'apple': 2,
        'update': 2,
        'mise à jour': 2,
        'click here': 3,
        'cliquez ici': 3,
        'winner': 3,
        'gagnant': 3,
        'prize': 3,
        'prix': 3,
        'lottery': 4,
        'loterie': 4,
        'free': 2,
        'gratuit': 2,
        'inheritance': 4,
        'héritage': 4
    }
    
    score = 0
    found_keywords = []
    
    for keyword, weight in suspicious_keywords.items():
        if keyword in text:
            score += weight
            found_keywords.append(keyword)
    
    return score, found_keywords

def check_url_virustotal(url: str) -> Dict:
    """Vérifie une URL sur VirusTotal"""
    if not VIRUSTOTAL_API_KEY:
        return {"error": "API Key manquante"}
    
    api_url = "https://www.virustotal.com/api/v3/urls"
    headers = {
        "x-apikey": VIRUSTOTAL_API_KEY
    }
    
    try:
        # Soumettre l'URL pour analyse
        response = requests.post(api_url, headers=headers, data={"url": url}, timeout=10)
        if response.status_code == 200:
            data = response.json()
            analysis_id = data.get("data", {}).get("id", "")
            
            # Récupérer les résultats
            analysis_url = f"https://www.virustotal.com/api/v3/analyses/{analysis_id}"
            result = requests.get(analysis_url, headers=headers, timeout=10)
            
            if result.status_code == 200:
                stats = result.json().get("data", {}).get("attributes", {}).get("stats", {})
                return {
                    "url": url,
                    "malicious": stats.get("malicious", 0),
                    "suspicious": stats.get("suspicious", 0),
                    "harmless": stats.get("harmless", 0)
                }
        
        return {"error": f"HTTP {response.status_code}"}
    except Exception as e:
        return {"error": str(e)}

def module_phishing_classifier():
    """Module 2: Phishing Email Classifier"""
    st.header("🎣 Phishing Email Classifier")
    st.markdown("**Analysez un email suspect pour détecter les signes de phishing**")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        subject = st.text_input("📧 Sujet de l'email", placeholder="Ex: Action Urgente Requise!")
    
    with col2:
        st.write("")  # Espaceur
    
    body = st.text_area(
        "📝 Corps de l'email",
        height=200,
        placeholder="Collez le contenu de l'email ici..."
    )
    
    if st.button("🔍 Analyser l'email", type="primary"):
        if not subject and not body:
            st.warning("⚠️ Veuillez entrer au moins le sujet ou le corps de l'email")
            return
        
        # Calculer le score de phishing
        score, keywords = calculate_phishing_score(subject, body)
        
        # Extraire les URLs
        urls = extract_urls(subject + " " + body)
        
        # Déterminer le niveau de risque
        if score >= 15:
            risk_level = "🔴 ÉLEVÉ"
            risk_color = "red"
        elif score >= 8:
            risk_level = "🟠 MOYEN"
            risk_color = "orange"
        else:
            risk_level = "🟢 FAIBLE"
            risk_color = "green"
        
        # Afficher les résultats
        st.subheader("📊 Résultats de l'analyse")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Score de suspicion", score, risk_level)
        
        with col2:
            st.metric("URLs trouvées", len(urls))
        
        with col3:
            st.metric("Mots-clés suspects", len(keywords))
        
        if keywords:
            st.subheader("⚠️ Mots-clés suspects détectés")
            st.write(", ".join(keywords))
        
        if urls:
            st.subheader("🔗 URLs extraites")
            for url in urls:
                st.code(url, language=None)
            
            # Option d'analyse VirusTotal
            if VIRUSTOTAL_API_KEY:
                if st.button("🔬 Analyser les URLs avec VirusTotal"):
                    for url in urls[:3]:  # Limiter à 3 URLs pour ne pas dépasser les quotas
                        with st.spinner(f"Analyse de {url}..."):
                            result = check_url_virustotal(url)
                        
                        if "error" not in result:
                            malicious = result.get("malicious", 0)
                            suspicious = result.get("suspicious", 0)
                            
                            if malicious > 0:
                                st.error(f"❌ {url}: Détecté comme malveillant par {malicious} moteur(s)")
                            elif suspicious > 0:
                                st.warning(f"⚠️ {url}: Marqué comme suspect par {suspicious} moteur(s)")
                            else:
                                st.success(f"✅ {url}: Aucune menace détectée")
            else:
                st.info("💡 Configurez VIRUSTOTAL_API_KEY pour analyser les URLs avec VirusTotal")

# ============================================================================
# MODULE 3 : PASSWORD STRENGTH & BREACH CHECK
# ============================================================================

def calculate_password_strength_simple(password: str) -> Dict:
    """Calcule la force d'un mot de passe (version simplifiée)"""
    score = 0
    feedback = []
    
    # Longueur
    length = len(password)
    if length < 8:
        feedback.append("Trop court (minimum 8 caractères)")
    elif length < 12:
        score += 1
        feedback.append("Longueur acceptable")
    else:
        score += 2
        feedback.append("Bonne longueur")
    
    # Complexité
    if re.search(r'[a-z]', password):
        score += 1
    else:
        feedback.append("Ajoutez des lettres minuscules")
    
    if re.search(r'[A-Z]', password):
        score += 1
    else:
        feedback.append("Ajoutez des lettres majuscules")
    
    if re.search(r'[0-9]', password):
        score += 1
    else:
        feedback.append("Ajoutez des chiffres")
    
    if re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        score += 2
    else:
        feedback.append("Ajoutez des caractères spéciaux")
    
    # Estimation du temps de craquage
    charset_size = 0
    if re.search(r'[a-z]', password):
        charset_size += 26
    if re.search(r'[A-Z]', password):
        charset_size += 26
    if re.search(r'[0-9]', password):
        charset_size += 10
    if re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        charset_size += 32
    
    if charset_size > 0:
        combinations = charset_size ** length
        # Supposons 10 milliards d'essais par seconde
        seconds = combinations / 10_000_000_000
        crack_time = format_crack_time(seconds)
    else:
        crack_time = "Instantané"
    
    # Niveau de force
    if score >= 7:
        strength = "Très Fort"
        strength_emoji = "🟢"
    elif score >= 5:
        strength = "Fort"
        strength_emoji = "🟡"
    elif score >= 3:
        strength = "Moyen"
        strength_emoji = "🟠"
    else:
        strength = "Faible"
        strength_emoji = "🔴"
    
    return {
        "score": score,
        "max_score": 8,
        "strength": strength,
        "strength_emoji": strength_emoji,
        "crack_time": crack_time,
        "feedback": feedback
    }

def format_crack_time(seconds: float) -> str:
    """Formate le temps de craquage en unité lisible"""
    if seconds < 1:
        return "Instantané"
    elif seconds < 60:
        return f"{seconds:.0f} secondes"
    elif seconds < 3600:
        return f"{seconds/60:.0f} minutes"
    elif seconds < 86400:
        return f"{seconds/3600:.0f} heures"
    elif seconds < 31536000:
        return f"{seconds/86400:.0f} jours"
    elif seconds < 31536000 * 100:
        return f"{seconds/31536000:.0f} années"
    elif seconds < 31536000 * 1000000:
        return f"{seconds/(31536000*1000):.0f}k années"
    else:
        return "Plusieurs millions d'années"

def check_password_pwned(password: str) -> Tuple[bool, int]:
    """Vérifie si un mot de passe a été compromis (API HaveIBeenPwned)"""
    # Hash SHA-1 du mot de passe
    sha1_hash = hashlib.sha1(password.encode('utf-8')).hexdigest().upper()
    prefix = sha1_hash[:5]
    suffix = sha1_hash[5:]
    
    try:
        url = f"https://api.pwnedpasswords.com/range/{prefix}"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            hashes = response.text.split('\r\n')
            for hash_line in hashes:
                hash_suffix, count = hash_line.split(':')
                if hash_suffix == suffix:
                    return True, int(count)
            return False, 0
        else:
            return False, -1
    except Exception as e:
        return False, -1

def module_password_strength():
    """Module 3: Password Strength & Breach Check"""
    st.header("🔑 Password Strength & Breach Check")
    st.markdown("**Vérifiez la robustesse de votre mot de passe et s'il a été compromis**")
    
    password = st.text_input(
        "🔒 Entrez un mot de passe à tester",
        type="password",
        help="Votre mot de passe n'est pas stocké et reste confidentiel"
    )
    
    if password:
        # Analyse de la force
        strength_result = calculate_password_strength_simple(password)
        
        st.subheader("📊 Analyse de la force")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                "Force du mot de passe",
                strength_result['strength'],
                strength_result['strength_emoji']
            )
        
        with col2:
            st.metric(
                "Score",
                f"{strength_result['score']}/{strength_result['max_score']}"
            )
        
        with col3:
            st.metric(
                "⏱️ Temps de craquage estimé",
                strength_result['crack_time']
            )
        
        # Barre de progression
        progress = strength_result['score'] / strength_result['max_score']
        st.progress(progress)
        
        # Feedback
        if strength_result['feedback']:
            with st.expander("💡 Recommandations"):
                for item in strength_result['feedback']:
                    st.write(f"- {item}")
        
        # Vérification Have I Been Pwned
        st.subheader("🔍 Vérification de compromission")
        
        with st.spinner("Vérification dans la base HaveIBeenPwned..."):
            is_pwned, count = check_password_pwned(password)
        
        if count == -1:
            st.warning("⚠️ Impossible de vérifier (erreur API)")
        elif is_pwned:
            st.error(f"❌ ALERTE : Ce mot de passe a été trouvé dans **{count:,}** fuites de données !")
            st.error("🚨 N'utilisez JAMAIS ce mot de passe !")
        else:
            st.success("✅ Ce mot de passe n'apparaît pas dans les bases de données de fuites connues")
            st.info("💡 Cela ne signifie pas qu'il est fort, vérifiez le score ci-dessus")

# ============================================================================
# MODULE 4 : HTTP / SQLi PAYLOAD CLASSIFIER
# ============================================================================

def detect_sql_injection(payload: str) -> Dict:
    """Détecte les patterns de SQL Injection"""
    payload_lower = payload.lower()
    
    sqli_patterns = {
        r'\bunion\b.*\bselect\b': 'UNION-based SQLi',
        r'\bor\b.*=.*': 'Boolean-based SQLi (OR)',
        r'\band\b.*=.*': 'Boolean-based SQLi (AND)',
        r'1\s*=\s*1': 'Tautology',
        r"'.*or.*'.*=.*'": 'Authentication bypass',
        r'--': 'SQL Comment',
        r'/\*.*\*/': 'SQL Comment (C-style)',
        r'\bselect\b.*\bfrom\b': 'SELECT statement',
        r'\bdrop\b.*\btable\b': 'DROP TABLE (destructive)',
        r'\binsert\b.*\binto\b': 'INSERT statement',
        r'\bupdate\b.*\bset\b': 'UPDATE statement',
        r'\bdelete\b.*\bfrom\b': 'DELETE statement',
        r'\bexec\b|\bexecute\b': 'Command execution',
        r';.*\b(select|drop|insert|update|delete)\b': 'Stacked queries',
        r'sleep\s*\(': 'Time-based SQLi',
        r'benchmark\s*\(': 'Time-based SQLi (MySQL)',
        r'waitfor\s+delay': 'Time-based SQLi (MSSQL)',
        r"'.*\+.*'|'.*\|\|.*'": 'String concatenation'
    }
    
    detected_patterns = []
    
    for pattern, description in sqli_patterns.items():
        if re.search(pattern, payload_lower):
            detected_patterns.append(description)
    
    return {
        "detected": len(detected_patterns) > 0,
        "patterns": detected_patterns,
        "count": len(detected_patterns)
    }

def detect_xss(payload: str) -> Dict:
    """Détecte les patterns de XSS"""
    payload_lower = payload.lower()
    
    xss_patterns = {
        r'<script': 'Script tag',
        r'javascript:': 'JavaScript protocol',
        r'onerror\s*=': 'onerror event handler',
        r'onload\s*=': 'onload event handler',
        r'onclick\s*=': 'onclick event handler',
        r'<img.*src': 'Image tag with src',
        r'<iframe': 'iFrame tag',
        r'<object': 'Object tag',
        r'<embed': 'Embed tag',
        r'alert\s*\(': 'alert() function',
        r'eval\s*\(': 'eval() function',
        r'document\.cookie': 'Cookie access',
        r'document\.write': 'document.write()',
        r'<svg.*onload': 'SVG with onload'
    }
    
    detected_patterns = []
    
    for pattern, description in xss_patterns.items():
        if re.search(pattern, payload_lower):
            detected_patterns.append(description)
    
    return {
        "detected": len(detected_patterns) > 0,
        "patterns": detected_patterns,
        "count": len(detected_patterns)
    }

def module_payload_classifier():
    """Module 4: HTTP / SQLi Payload Classifier"""
    st.header("💉 HTTP / SQLi Payload Classifier")
    st.markdown("**Détectez les tentatives d'injection SQL et XSS dans les requêtes HTTP**")
    
    payload = st.text_area(
        "🔍 Entrez une requête HTTP ou un paramètre URL",
        height=150,
        placeholder="Ex: ?id=1' OR '1'='1 --\nEx: <script>alert('XSS')</script>"
    )
    
    if st.button("🔬 Analyser le payload", type="primary"):
        if not payload:
            st.warning("⚠️ Veuillez entrer un payload à analyser")
            return
        
        # Détecter SQL Injection
        sqli_result = detect_sql_injection(payload)
        
        # Détecter XSS
        xss_result = detect_xss(payload)
        
        # Classification globale
        total_threats = sqli_result['count'] + xss_result['count']
        
        if total_threats == 0:
            classification = "✅ Normal"
            classification_color = "green"
        elif total_threats <= 2:
            classification = "⚠️ Suspicious"
            classification_color = "orange"
        else:
            classification = "🚨 Likely Attack"
            classification_color = "red"
        
        # Afficher les résultats
        st.subheader("📊 Résultats de l'analyse")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Classification", classification)
        
        with col2:
            st.metric("Patterns SQLi détectés", sqli_result['count'])
        
        with col3:
            st.metric("Patterns XSS détectés", xss_result['count'])
        
        # Détails SQL Injection
        if sqli_result['detected']:
            st.subheader("🗄️ Patterns SQL Injection détectés")
            for pattern in sqli_result['patterns']:
                st.error(f"❌ {pattern}")
        
        # Détails XSS
        if xss_result['detected']:
            st.subheader("🌐 Patterns XSS détectés")
            for pattern in xss_result['patterns']:
                st.error(f"❌ {pattern}")
        
        # Recommandations
        if total_threats > 0:
            with st.expander("🛡️ Recommandations"):
                st.write("**Actions à prendre :**")
                if sqli_result['detected']:
                    st.write("- ✅ Utilisez des requêtes préparées (Prepared Statements)")
                    st.write("- ✅ Validez et nettoyez toutes les entrées utilisateur")
                    st.write("- ✅ Échappez les caractères spéciaux SQL")
                if xss_result['detected']:
                    st.write("- ✅ Encodez toutes les sorties HTML")
                    st.write("- ✅ Utilisez Content Security Policy (CSP)")
                    st.write("- ✅ Sanitisez les entrées utilisateur")
                st.write("- ✅ Loggez cette tentative d'attaque")
                st.write("- ✅ Considérez le blocage de l'adresse IP source")

# ============================================================================
# NAVIGATION & INTERFACE PRINCIPALE
# ============================================================================

def main():
    """Fonction principale de l'application"""
    
    # Titre principal
    st.title("🛡️ Blue Team Toolkit")
    st.markdown("### *Plateforme d'analyse de cybersécurité*")
    st.markdown("---")
    
    # Sidebar pour la navigation
    with st.sidebar:
        st.image("https://img.icons8.com/fluency/96/000000/security-shield-green.png", width=100)
        st.title("Navigation")
        st.markdown("---")
        
        module = st.radio(
            "Choisissez un module :",
            [
                "🏠 Accueil",
                "🔒 SSH Brute-force Detector",
                "🎣 Phishing Email Classifier",
                "🔑 Password Strength Checker",
                "💉 Payload Classifier"
            ]
        )
        
        st.markdown("---")
        st.markdown("### ⚙️ Configuration")
        
        # Statut des API keys
        if ABUSEIPDB_API_KEY:
            st.success("✅ AbuseIPDB API")
        else:
            st.error("❌ AbuseIPDB API")
        
        if VIRUSTOTAL_API_KEY:
            st.success("✅ VirusTotal API")
        else:
            st.error("❌ VirusTotal API")
        
        st.markdown("---")
        st.caption("Made with ❤️ by Blue Team")
        st.caption(f"Version 1.0 | {datetime.now().year}")
    
    # Router vers le bon module
    if module == "🏠 Accueil":
        st.header("🏠 Bienvenue sur Blue Team Toolkit")
        
        st.markdown("""
        Cette application vous offre **4 modules puissants** pour renforcer votre posture de sécurité :
        
        ### 📦 Modules disponibles
        
        #### 🔒 SSH Brute-force Detector
        - Analysez vos logs SSH pour détecter les attaques par force brute
        - Identifiez les adresses IP malveillantes
        - Vérifiez la réputation des IPs avec **AbuseIPDB**
        
        #### 🎣 Phishing Email Classifier
        - Détectez les emails de phishing
        - Analysez les mots-clés suspects
        - Extrayez et vérifiez les URLs avec **VirusTotal**
        
        #### 🔑 Password Strength Checker
        - Évaluez la robustesse de vos mots de passe
        - Estimez le temps de craquage
        - Vérifiez s'ils ont été compromis avec **HaveIBeenPwned**
        
        #### 💉 Payload Classifier
        - Détectez les tentatives d'injection SQL
        - Identifiez les attaques XSS
        - Classifiez automatiquement les payloads malveillants
        
        ---
        
        ### 🚀 Pour commencer
        
        1. Sélectionnez un module dans la barre latérale
        2. Configurez vos clés API si nécessaire (voir statut dans la sidebar)
        3. Suivez les instructions de chaque module
        
        ### 🔑 Configuration des API
        
        Pour profiter de toutes les fonctionnalités, configurez vos clés API :
        
        - **AbuseIPDB** : [https://www.abuseipdb.com/api](https://www.abuseipdb.com/api)
        - **VirusTotal** : [https://www.virustotal.com/gui/join-us](https://www.virustotal.com/gui/join-us)
        
        Voir le fichier `.env.example` pour les instructions de configuration.
        """)
        
        st.info("💡 **Astuce** : Tous les modules peuvent fonctionner en mode dégradé sans clés API, mais certaines fonctionnalités seront limitées.")
        
    elif module == "🔒 SSH Brute-force Detector":
        module_ssh_bruteforce()
    
    elif module == "🎣 Phishing Email Classifier":
        module_phishing_classifier()
    
    elif module == "🔑 Password Strength Checker":
        module_password_strength()
    
    elif module == "💉 Payload Classifier":
        module_payload_classifier()

if __name__ == "__main__":
    main()

