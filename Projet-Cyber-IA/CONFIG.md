# 🔑 Guide de Configuration - Blue Team Toolkit

## Configuration des Clés API

Pour profiter de toutes les fonctionnalités de l'application, vous devez configurer vos clés API. Deux méthodes sont disponibles :

---

## Méthode 1 : Variables d'Environnement (Recommandé pour le développement)

### Windows (PowerShell)
```powershell
$env:ABUSEIPDB_API_KEY="votre_cle_abuseipdb"
$env:VIRUSTOTAL_API_KEY="votre_cle_virustotal"
```

### Windows (CMD)
```cmd
set ABUSEIPDB_API_KEY=votre_cle_abuseipdb
set VIRUSTOTAL_API_KEY=votre_cle_virustotal
```

### Linux / Mac
```bash
export ABUSEIPDB_API_KEY="votre_cle_abuseipdb"
export VIRUSTOTAL_API_KEY="votre_cle_virustotal"
```

**Note** : Ces variables sont temporaires et seront perdues à la fermeture du terminal.

### Rendre les variables permanentes

#### Windows
Ajoutez les variables dans les paramètres système :
1. Panneau de configuration → Système → Paramètres système avancés
2. Variables d'environnement → Nouveau (Variables utilisateur)

#### Linux / Mac
Ajoutez dans `~/.bashrc` ou `~/.zshrc` :
```bash
echo 'export ABUSEIPDB_API_KEY="votre_cle"' >> ~/.bashrc
echo 'export VIRUSTOTAL_API_KEY="votre_cle"' >> ~/.bashrc
source ~/.bashrc
```

---

## Méthode 2 : Streamlit Secrets (Recommandé pour la production)

### 1. Créer le dossier de configuration
```bash
mkdir .streamlit
```

### 2. Créer le fichier secrets.toml

Créez un fichier `.streamlit/secrets.toml` avec le contenu suivant :

```toml
# Blue Team Toolkit - Configuration API

ABUSEIPDB_API_KEY = "votre_cle_abuseipdb_ici"
VIRUSTOTAL_API_KEY = "votre_cle_virustotal_ici"
```

### 3. Sécurité
⚠️ **IMPORTANT** : Le fichier `secrets.toml` contient des informations sensibles !

- ❌ Ne le commitez JAMAIS sur Git
- ✅ Ajoutez-le au `.gitignore` :
  ```
  .streamlit/secrets.toml
  ```

---

## 📋 Obtenir les Clés API

### 🔍 AbuseIPDB

**Utilisé pour** : Vérifier la réputation des adresses IP

1. **Créer un compte** : [https://www.abuseipdb.com/register](https://www.abuseipdb.com/register)
2. **Obtenir la clé** : [https://www.abuseipdb.com/api](https://www.abuseipdb.com/api)
3. **Limites gratuites** :
   - 1 000 requêtes par jour
   - 1 requête par seconde
   - Données sur 90 jours

**Format de la clé** : `1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef`

---

### 🦠 VirusTotal

**Utilisé pour** : Vérifier la malveillance des URLs

1. **Créer un compte** : [https://www.virustotal.com/gui/join-us](https://www.virustotal.com/gui/join-us)
2. **Obtenir la clé** : Profil → API Key
3. **Limites gratuites** :
   - 4 requêtes par minute
   - 500 requêtes par jour
   - 178 000 requêtes par mois

**Format de la clé** : `abcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890`

---

### 🔐 HaveIBeenPwned

**Utilisé pour** : Vérifier si un mot de passe a été compromis

✅ **Aucune clé API requise !**

L'API Pwned Passwords est publique et gratuite. Elle utilise le modèle k-Anonymity pour préserver la confidentialité.

---

## ✅ Vérifier la Configuration

Après avoir configuré vos clés, lancez l'application :

```bash
streamlit run app.py
```

Dans la barre latérale (sidebar), vous devriez voir :

✅ **Configuration correcte**
```
⚙️ Configuration
✅ AbuseIPDB API
✅ VirusTotal API
```

❌ **Configuration manquante**
```
⚙️ Configuration
❌ AbuseIPDB API
❌ VirusTotal API
```

---

## 🐛 Dépannage

### Les clés API ne sont pas reconnues

1. **Vérifiez le format** : Pas d'espaces, pas de guillemets supplémentaires
2. **Relancez Streamlit** : `Ctrl+C` puis `streamlit run app.py`
3. **Vérifiez les chemins** :
   - Fichier secrets.toml dans `.streamlit/secrets.toml`
   - Exécution depuis le bon répertoire

### Erreur "API Key manquante"

L'application fonctionne en **mode dégradé** sans les clés API :
- Module SSH : ❌ Pas de vérification de réputation
- Module Phishing : ❌ Pas d'analyse VirusTotal
- Module Password : ✅ Fonctionne (HaveIBeenPwned ne nécessite pas de clé)
- Module Payload : ✅ Fonctionne (analyse locale)

### Erreur "Rate limit exceeded"

Vous avez dépassé les limites gratuites :
- **AbuseIPDB** : Attendez 24h ou passez au plan premium
- **VirusTotal** : Attendez 1 minute entre les requêtes

---

## 🔒 Bonnes Pratiques de Sécurité

1. ✅ **Ne partagez jamais vos clés API**
2. ✅ **Ajoutez `secrets.toml` au `.gitignore`**
3. ✅ **Régénérez les clés si elles sont compromises**
4. ✅ **Utilisez des clés différentes pour dev/prod**
5. ✅ **Surveillez votre utilisation sur les dashboards des APIs**

---

## 📞 Support

Si vous rencontrez des problèmes :
1. Vérifiez ce guide de configuration
2. Consultez le README.md
3. Ouvrez une issue sur GitHub

---

**Dernière mise à jour** : Novembre 2025

