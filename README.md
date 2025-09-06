#  Network Scanner Pro

Une application moderne et complète de scanning réseau avec interface web professionnelle, base de données intégrée et analytics avancés.

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)
![SQLite](https://img.shields.io/badge/SQLite-3.0+-orange.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

##  Fonctionnalités Principales

###  Scanning Réseau Avancé
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
git clone https://github.com/anis-metref/network-scanport.git
cd network-scanport
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

##  Guide d'Utilisation

###  Page Principale (Scanner)
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

###  Page Analytics
Tableau de bord complet avec :
- **Statistiques globales** : Total des scans, hôtes découverts, taux de succès
- **Graphiques** : Évolution des scans dans le temps
- **Top services** : Services les plus fréquemment découverts
- **Activité récente** : Derniers scans effectués

###  Carte Réseau
Visualisation interactive des réseaux :
- **Vue graphique** : Représentation visuelle des hôtes et réseaux
- **Légende interactive** : Distinction hôtes en ligne/hors ligne
- **Détails d'hôte** : Informations détaillées au clic
- **Statistiques en temps réel** : Compteurs dynamiques

###  Historique
Gestion complète de l'historique :
- **Liste des sessions** : Toutes les sessions de scan avec détails
- **Recherche avancée** : Filtrage par IP, statut, date
- **Détails de session** : Vue complète des résultats de chaque scan
- **Suppression** : Gestion individuelle ou en masse



*Développé avec ❤️ pour la communauté open source*

</div>
