# 🛡️ Blue Team Toolkit

Application web de cyberdéfense développée avec Streamlit, intégrant des APIs tierces pour enrichir l'analyse de sécurité.

## 📋 Description

Blue Team Toolkit est une plateforme complète d'analyse de cybersécurité offrant 4 modules puissants :

### 🔒 Module 1 : SSH Brute-force Detector
- Analyse des logs SSH (`/var/log/auth.log`)
- Détection des tentatives d'authentification échouées
- Identification des IPs malveillantes
- **Intégration AbuseIPDB** : Vérification de la réputation des IPs avec score de confiance et géolocalisation

### 🎣 Module 2 : Phishing Email Classifier
- Analyse d'emails suspects (sujet + corps)
- Détection de mots-clés suspects (urgent, banque, vérification, etc.)
- Extraction automatique des URLs via Regex
- **Intégration VirusTotal** (optionnelle) : Vérification de la malveillance des liens

### 🔑 Module 3 : Password Strength & Breach Check
- Évaluation de la complexité des mots de passe
- Calcul du temps de craquage estimé
- **Intégration HaveIBeenPwned** : Vérification si le mot de passe a été compromis (via k-Anonymity avec hash SHA-1 partiel)

### 💉 Module 4 : HTTP / SQLi Payload Classifier
- Détection de patterns SQL Injection (UNION, SELECT, OR 1=1, etc.)
- Détection de patterns XSS (&lt;script&gt;, javascript:, event handlers)
- Classification automatique : Normal / Suspicious / Likely Attack

## 🚀 Installation

### Prérequis
- Python 3.8 ou supérieur
- pip (gestionnaire de paquets Python)

### Étapes d'installation

1. **Cloner le projet**
```bash
git clone <votre-repo>
cd Projet-Cyber-IA
```

2. **Installer les dépendances**
```bash
pip install -r requirements.txt
```

3. **Configuration des clés API**

#### Option 1 : Utiliser un fichier .env (recommandé)
```bash
# Copier le fichier exemple
cp .env.example .env

# Éditer le fichier .env et ajouter vos clés API
notepad .env  # Windows
nano .env     # Linux/Mac
```

#### Option 2 : Utiliser Streamlit Secrets
```bash
# Créer le dossier de configuration
mkdir .streamlit

# Créer le fichier secrets.toml
notepad .streamlit\secrets.toml  # Windows
nano .streamlit/secrets.toml     # Linux/Mac
```

Contenu du fichier `secrets.toml` :
```toml
ABUSEIPDB_API_KEY = "votre_cle_ici"
VIRUSTOTAL_API_KEY = "votre_cle_ici"
```

## 🔑 Obtenir les clés API

### AbuseIPDB
1. Créez un compte sur [https://www.abuseipdb.com/](https://www.abuseipdb.com/)
2. Accédez à [https://www.abuseipdb.com/api](https://www.abuseipdb.com/api)
3. Générez votre clé API gratuite
4. **Plan gratuit** : 1 000 requêtes/jour

### VirusTotal
1. Créez un compte sur [https://www.virustotal.com/gui/join-us](https://www.virustotal.com/gui/join-us)
2. Accédez à votre profil > API Key
3. Copiez votre clé API
4. **Plan gratuit** : 4 requêtes/minute, 500 requêtes/jour

### HaveIBeenPwned
**Aucune clé API requise** - L'API Pwned Passwords est publique et gratuite !

## ▶️ Lancement de l'application

```bash
streamlit run app.py
```

L'application s'ouvrira automatiquement dans votre navigateur à l'adresse `http://localhost:8501`

## 📖 Utilisation

### Module SSH Brute-force Detector
1. Uploadez un fichier de logs SSH (`auth.log`)
2. L'application identifie automatiquement les IPs suspectes
3. Les 3 IPs les plus actives sont analysées via AbuseIPDB

### Module Phishing Email Classifier
1. Collez le sujet et le corps d'un email suspect
2. Cliquez sur "Analyser l'email"
3. Consultez le score de risque et les URLs extraites
4. (Optionnel) Analysez les URLs avec VirusTotal

### Module Password Strength Checker
1. Entrez un mot de passe dans le champ sécurisé
2. Consultez instantanément :
   - Le score de force
   - Le temps de craquage estimé
   - Le statut de compromission (HaveIBeenPwned)

### Module Payload Classifier
1. Collez une requête HTTP ou un paramètre URL
2. Cliquez sur "Analyser le payload"
3. Consultez les patterns SQLi/XSS détectés

## 🛡️ Sécurité et Confidentialité

- ✅ Les mots de passe testés ne sont **jamais stockés**
- ✅ HaveIBeenPwned utilise le **k-Anonymity model** (seuls les 5 premiers caractères du hash sont envoyés)
- ✅ Les clés API sont stockées localement et ne sont jamais transmises
- ✅ Toutes les communications API utilisent HTTPS

## 📦 Stack Technique

- **Frontend/Backend** : Streamlit
- **Langage** : Python 3.x
- **Bibliothèques** :
  - `pandas` : Analyse de données et logs
  - `requests` : Appels API
  - `re` : Expressions régulières pour le parsing
  - `hashlib` : Hachage SHA-1 pour HaveIBeenPwned

## 🧪 Exemples de fichiers de test

### Exemple auth.log
```
Jan 15 10:23:45 server sshd[1234]: Failed password for root from 192.168.1.100 port 22 ssh2
Jan 15 10:23:46 server sshd[1235]: Failed password for admin from 192.168.1.100 port 22 ssh2
Jan 15 10:24:01 server sshd[1236]: Failed password for root from 203.0.113.50 port 22 ssh2
```

### Exemple email de phishing
```
Sujet : Action Urgente Requise - Votre Compte Banque

Corps : 
Bonjour,

Votre compte a été suspendu. Cliquez immédiatement sur ce lien pour vérifier vos informations :
http://suspicious-bank-verify.com/login

Cordialement,
Votre Banque
```

## 🤝 Contribution

Les contributions sont les bienvenues ! N'hésitez pas à ouvrir une issue ou une pull request.

## 📄 Licence

Ce projet est sous licence MIT.

## 👨‍💻 Auteur

Expert Développeur Python & Ingénieur en Cybersécurité

---

**⚠️ Avertissement** : Cet outil est destiné à des fins éducatives et de sensibilisation à la cybersécurité. Utilisez-le de manière responsable et éthique.

