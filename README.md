# Texte2Audio

**Texte2Audio** est une application web basée sur Flask et l'IA pour convertir du texte en audio de haute qualité. Avec une interface conviviale et des fonctionnalités avancées, comme le clonage vocal et la gestion des fichiers audio, ce projet est idéal pour intégrer des solutions de Text-to-Speech dans vos applications.

---

## 🚀 Fonctionnalités principales

- Génération d'audio multilingue (anglais, français, espagnol, italien, etc.).
- Clonage vocal avec enregistrement et utilisation de voix personnalisées.
- Interface web simple et intuitive.
- Gestion de l'historique des audios générés avec téléchargement et copie en base64.

---

## 🛠️ Installation et démarrage rapide

### Prérequis
- **Python 3.8+**
- **pip** (installé avec Python)
- **Git** (pour cloner le projet)
- Un environnement virtuel (recommandé)

### Étapes d'installation

1. **Clonez le projet depuis GitHub :**
   ```bash
   git clone https://github.com/tomDeprez/-Texte2Audio-.git
   cd texte2audio
   ```

2. **Créez et activez un environnement virtuel :**
   ```bash
   python -m venv venv
   source venv/bin/activate    # Linux/MacOS
   venv\Scripts\activate       # Windows
   ```

3. **Installez les dépendances nécessaires :**
   ```bash
   pip install -r requirements.txt
   ```

4. **Lancez l'application Flask :**
   ```bash
   python app.py
   ```

5. **Accédez à l'application dans votre navigateur :**
   Ouvrez [http://localhost:5000](http://localhost:5000).

---

## 📂 Structure du projet

```plaintext
texte2audio/
├── app.py                 # Script principal pour lancer le serveur Flask
├── requirements.txt       # Dépendances du projet
├── static/                # Fichiers statiques générés (audios, etc.)
├── voices/                # Voix enregistrées pour le clonage vocal
└── templates/             # Fichiers HTML (optionnel si nécessaires plus tard)
```

---

## ⚙️ Exemple d'utilisation

1. **Convertir du texte en audio :**
   - Entrez un texte dans le champ dédié.
   - Choisissez une langue et cliquez sur "Générer l'audio".
   - Téléchargez ou écoutez directement le fichier généré.

2. **Clonage vocal :**
   - Enregistrez une voix personnalisée via le formulaire.
   - Utilisez cette voix pour générer des audios avec un ton unique.

---

## 🧰 Dépendances principales

- **Flask** : Serveur web léger.
- **TTS** : Module pour la synthèse vocale.
- **Werkzeug** : Gestion sécurisée des fichiers téléchargés.

---

## 🤝 Contribuer

Les contributions sont les bienvenues ! N'hésitez pas à soumettre une issue ou une pull request.

---

## 📧 Contact

Si vous avez des questions ou des suggestions, contactez-moi sur github.
