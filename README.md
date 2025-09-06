# 🛡️ Network Scanner Pro

Une application moderne et complète de scanning réseau avec interface web professionnelle, base de données intégrée et analytics avancés.

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)
![SQLite](https://img.shields.io/badge/SQLite-3.0+-orange.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

## ✨ Fonctionnalités Principales

### 🎯 Scanning Réseau Avancé
- **Types de scan multiples** : Rapide, complet, par plage personnalisée
- **Support de formats** : CIDR (`192.168.1.0/24`), plages (`192.168.1.1-254`), IP individuelles
- **Détection de ports intelligente** : Scan automatique ou ports personnalisés
- **Identification de services** : Reconnaissance automatique des services sur ports ouverts
- **Scan asynchrone** : Performance optimisée avec gestion de la concurrence

### 🖥️ Interface Utilisateur Moderne
- **Design GNOME/Adwaita** : Interface élégante et professionnelle
- **Temps réel** : Mise à jour instantanée via WebSockets
- **Multi-pages** : Scanner, Historique, Analytics, Carte réseau
- **Responsive** : Adapté à tous les écrans (desktop, tablet, mobile)
- **Contrôles avancés** : Arrêt de scan, filtres, recherche

### 📊 Base de Données et Persistance
- **SQLite intégré** : Stockage automatique de tous les scans
- **Historique complet** : Conservation de toutes les sessions de scan
- **Recherche avancée** : Recherche dans l'historique par IP, service, etc.
- **Statistiques détaillées** : Métriques et analytics sur les scans
- **Gestion des bookmarks** : Sauvegarde de cibles favorites

### 📈 Analytics et Visualisation
- **Tableau de bord** : Vue d'ensemble des statistiques
- **Carte réseau interactive** : Visualisation graphique des réseaux scannés
- **Métriques en temps réel** : Progression, hôtes découverts, services actifs
- **Historique détaillé** : Consultation et gestion des scans précédents

## 🚀 Installation et Démarrage

### Prérequis
- **Python 3.8+** (recommandé : Python 3.9+)
- **Système Linux/Unix** (optimisé pour Linux, compatible macOS)
- **Privilèges réseau** (pour certains types de scans)

### Installation Rapide

1. **Cloner le projet** :
```bash
git clone https://github.com/votre-username/network-scanner-pro.git
cd network-scanner-pro
```

2. **Créer un environnement virtuel** (recommandé) :
```bash
python3 -m venv venv
source venv/bin/activate  # Linux/macOS
# ou
venv\Scripts\activate     # Windows
```

3. **Installer les dépendances** :
```bash
pip install -r requirements.txt
```

4. **Lancer l'application** :
```bash
python3 app.py
```

5. **Accéder à l'interface** :
Ouvrez votre navigateur sur : **http://localhost:5000**

### Installation Automatique
```bash
chmod +x install.sh
./install.sh
```

## 📖 Guide d'Utilisation

### 🏠 Page Principale (Scanner)
L'interface principale offre un accès direct aux fonctionnalités de scan :

1. **Panneau de Configuration** :
   - **Cible** : Saisissez l'IP, réseau CIDR ou plage à scanner
   - **Type de scan** : Choisissez entre Rapide, Complet ou Plage personnalisée
   - **Ports** : Spécifiez des ports personnalisés ou laissez en automatique
   - **Interfaces réseau** : Détection automatique des interfaces disponibles

2. **Zone de Résultats** :
   - **Progression en temps réel** : Barre de progression et statistiques
   - **Liste des hôtes** : Affichage détaillé des hôtes découverts
   - **Informations des ports** : Services identifiés sur chaque port ouvert

### 📊 Page Analytics
Tableau de bord complet avec :
- **Statistiques globales** : Total des scans, hôtes découverts, taux de succès
- **Graphiques** : Évolution des scans dans le temps
- **Top services** : Services les plus fréquemment découverts
- **Activité récente** : Derniers scans effectués

### 🗺️ Carte Réseau
Visualisation interactive des réseaux :
- **Vue graphique** : Représentation visuelle des hôtes et réseaux
- **Légende interactive** : Distinction hôtes en ligne/hors ligne
- **Détails d'hôte** : Informations détaillées au clic
- **Statistiques en temps réel** : Compteurs dynamiques

### 📚 Historique
Gestion complète de l'historique :
- **Liste des sessions** : Toutes les sessions de scan avec détails
- **Recherche avancée** : Filtrage par IP, statut, date
- **Détails de session** : Vue complète des résultats de chaque scan
- **Suppression** : Gestion individuelle ou en masse

### 🎯 Types de Scan Disponibles

| Type | Description | Ports Scannés | Durée Estimée |
|------|-------------|----------------|---------------|
| **Rapide** | Scan des ports les plus courants | 1-1024 | 30s - 2min |
| **Complet** | Scan exhaustif de tous les ports | 1-65535 | 5-30min |
| **Plage** | Scan d'une plage personnalisée | 1-10000 | 2-10min |

### 📝 Formats de Cible Supportés

```bash
# IP unique
192.168.1.1

# Réseau CIDR
192.168.1.0/24          # Scan de 192.168.1.1 à 192.168.1.254
10.0.0.0/16             # Scan de 10.0.0.1 à 10.0.255.254

# Plage d'IP
192.168.1.1-254         # Scan de 192.168.1.1 à 192.168.1.254
10.0.1.100-200          # Scan de 10.0.1.100 à 10.0.1.200
```

### 🔧 Configuration des Ports

```bash
# Ports automatiques (recommandé)
auto

# Ports personnalisés
22,80,443,8080,3389

# Plages de ports
1-1000
80-90,443,8080-8090

# Ports spécifiques avec services courants
21,22,23,25,53,80,110,143,443,993,995,3389,5432,3306
```

## 🏗️ Architecture Technique

### 🔧 Backend (Python/FastAPI)
```
app.py                  # Application principale FastAPI
├── WebSocket Server    # Communication temps réel
├── API REST           # Endpoints pour configuration et contrôle
├── Scanner Engine     # Moteur de scan asynchrone
└── Database Manager   # Gestionnaire SQLite

database.py            # Gestionnaire de base de données
├── Session Management # Gestion des sessions de scan
├── Results Storage    # Stockage des résultats
├── Search Engine      # Moteur de recherche
└── Analytics Engine   # Calcul des statistiques
```

### 🎨 Frontend (HTML5/CSS3/JavaScript)
```
static/
├── index.html         # Page principale (Scanner)
├── history.html       # Page historique
├── analytics.html     # Page analytics
├── network-map.html   # Carte réseau interactive
├── styles.css         # Styles principaux (Design GNOME)
├── database-styles.css # Styles pour les pages de données
└── app.js             # Logique JavaScript (2700+ lignes)
```

### 🗄️ Base de Données (SQLite)
```sql
scan_sessions          # Sessions de scan
├── id, target, scan_type, ports
├── status, total_hosts, hosts_up
└── created_at, completed_at

scan_results          # Résultats détaillés
├── session_id, host, status
├── ports (JSON), os_info
└── scan_time

bookmarks            # Cibles favorites
├── name, target, description
├── scan_type, ports
└── created_at
```

### 🎨 Design System GNOME/Adwaita
- **Palette de couleurs** : Bleu primary (#3584e4), gris neutres
- **Typographie** : Police Inter avec hiérarchie claire
- **Composants** : Boutons, cartes, modales cohérents
- **Animations** : Transitions fluides et micro-interactions
- **Responsive** : Grid CSS et Flexbox pour tous les écrans

## 🔒 Sécurité et Bonnes Pratiques

### 🛡️ Mesures de Sécurité
- **Validation stricte** : Vérification des formats IP/CIDR/ports
- **Limitation de charge** : Protection contre les scans trop larges (max 254 hôtes)
- **Timeouts adaptatifs** : Limitation du temps de scan par hôte
- **Gestion d'erreurs** : Capture et logging des exceptions
- **Permissions système** : Utilisation sécurisée des outils réseau

### ⚡ Optimisations Performance
- **Scan asynchrone** : Utilisation d'asyncio pour la concurrence
- **Limitation de connexions** : Semaphore pour éviter la surcharge
- **Batch processing** : Traitement par lots des hôtes
- **Mise en cache** : Optimisation des requêtes base de données

## 🛠️ Développement et Personnalisation

### 📁 Structure Complète du Projet
```
network-scanner-pro/
├── app.py                    # 🐍 Application FastAPI principale
├── database.py               # 🗄️ Gestionnaire de base de données
├── requirements.txt          # 📦 Dépendances Python
├── install.sh               # 🚀 Script d'installation
├── README.md                # 📖 Documentation
├── venv/                    # 🔒 Environnement virtuel Python
└── static/                  # 🌐 Frontend
    ├── index.html           # 🏠 Page principale
    ├── history.html         # 📚 Page historique
    ├── analytics.html       # 📊 Page analytics
    ├── network-map.html     # 🗺️ Carte réseau
    ├── styles.css           # 🎨 Styles principaux
    ├── database-styles.css  # 🎨 Styles base de données
    ├── app.js              # ⚡ Logique JavaScript
    └── favicon.ico         # 🔖 Icône du site
```

### 🎛️ Configuration et Personnalisation
```python
# Dans app.py - Configuration des timeouts
SCAN_TIMEOUT = 0.8          # Timeout par port (secondes)
MAX_CONCURRENT = 30         # Connexions simultanées
BATCH_SIZE = 10            # Hôtes traités par lot

# Dans styles.css - Variables CSS personnalisables
:root {
    --primary-color: #3584e4;     # Couleur principale
    --success-color: #26a269;     # Couleur succès
    --warning-color: #f5c211;     # Couleur avertissement
    --danger-color: #e01b24;      # Couleur danger
}
```

## 🚀 Fonctionnalités Avancées

### 📊 Analytics et Métriques
- **Statistiques en temps réel** : Compteurs dynamiques pendant les scans
- **Historique détaillé** : Conservation de tous les scans avec horodatage
- **Recherche avancée** : Filtrage par IP, service, statut, date
- **Export de données** : Possibilité d'export JSON des résultats

### 🗺️ Visualisation Réseau
- **Carte interactive** : Représentation graphique des réseaux scannés
- **Détection automatique** : Identification des passerelles et sous-réseaux
- **Légende dynamique** : Distinction visuelle des états d'hôtes
- **Zoom et navigation** : Interface intuitive pour explorer les réseaux

## ⚠️ Limitations et Considérations

### 🔧 Limitations Techniques
- **Privilèges système** : Certains scans avancés nécessitent des droits administrateur
- **Performance réseau** : Vitesse limitée par la bande passante et latence
- **Compatibilité OS** : Optimisé pour Linux/Unix (commandes système spécifiques)
- **Taille des réseaux** : Limitation à 254 hôtes par scan pour éviter la surcharge

### 🎯 Cas d'Usage Recommandés
- **Audit de sécurité** : Découverte de services exposés
- **Inventaire réseau** : Cartographie des équipements
- **Monitoring** : Surveillance de la disponibilité des services
- **Dépannage** : Diagnostic de problèmes de connectivité

## 🗺️ Roadmap et Évolutions

### ✅ Fonctionnalités Actuelles
- [x] Scanner réseau multi-format (CIDR, plages, IP)
- [x] Interface web moderne et responsive
- [x] Base de données SQLite intégrée
- [x] Historique et analytics complets
- [x] Carte réseau interactive
- [x] Gestion des bookmarks
- [x] WebSocket temps réel

### 🔮 Fonctionnalités Futures
- [ ] **Support UDP** : Scan des ports UDP en plus du TCP
- [ ] **Détection d'OS** : Identification avancée des systèmes d'exploitation
- [ ] **Graphiques avancés** : Charts et visualisations des tendances
- [ ] **Notifications** : Alertes système et email
- [ ] **API publique** : Endpoints pour intégration externe
- [ ] **Mode sombre** : Thème sombre pour l'interface
- [ ] **Multi-langue** : Support français/anglais/autres langues
- [ ] **Plugins** : Système d'extensions pour fonctionnalités custom

## 🤝 Contribution et Support

### 💡 Comment Contribuer
1. **Fork** le projet sur GitHub
2. **Créer** une branche feature (`git checkout -b feature/nouvelle-fonctionnalite`)
3. **Commiter** vos changements (`git commit -am 'Ajout nouvelle fonctionnalité'`)
4. **Pousser** vers la branche (`git push origin feature/nouvelle-fonctionnalite`)
5. **Ouvrir** une Pull Request avec description détaillée

### 🐛 Signaler des Bugs
- **Issues GitHub** : Utilisez les templates d'issues
- **Logs détaillés** : Incluez les logs d'erreur complets
- **Environnement** : Précisez OS, version Python, etc.
- **Reproduction** : Étapes pour reproduire le problème

### 📞 Support et Aide
- **Documentation** : Consultez ce README et les commentaires du code
- **Issues GitHub** : Pour questions techniques et bugs
- **Discussions** : Pour suggestions et idées d'amélioration

## 📄 Licence et Crédits

### 📜 Licence MIT
Ce projet est distribué sous licence MIT. Vous êtes libre de :
- ✅ Utiliser le code à des fins commerciales et personnelles
- ✅ Modifier et distribuer le code
- ✅ Inclure dans des projets propriétaires
- ⚠️ Obligation de conserver la notice de copyright

### 🙏 Crédits et Remerciements
- **Design** : Inspiré du design system GNOME/Adwaita
- **Icons** : Icônes personnalisées CSS pures
- **Fonts** : Police Inter de Google Fonts
- **Technologies** : FastAPI, SQLite, WebSockets, HTML5/CSS3/JS

---

<div align="center">

**🛡️ Network Scanner Pro** - *Scanning réseau moderne et professionnel*

[![GitHub](https://img.shields.io/badge/GitHub-Repository-black?logo=github)](https://github.com/votre-username/network-scanner-pro)
[![Python](https://img.shields.io/badge/Made%20with-Python-blue?logo=python)](https://python.org)
[![FastAPI](https://img.shields.io/badge/Powered%20by-FastAPI-green?logo=fastapi)](https://fastapi.tiangolo.com)

*Développé avec ❤️ pour la communauté open source*

</div>