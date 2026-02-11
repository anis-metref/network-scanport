#!/bin/bash

# Network Scanner - Script d'installation
# Installation automatique des dépendances et lancement de l'application

echo "Installation de Network Scanner"
echo "=================================="

# Vérifier Python
if ! command -v python3 &> /dev/null; then
    echo "Python 3 n'est pas installé"
    echo "Veuillez installer Python 3.8+ avant de continuer"
    exit 1
fi

echo "Python 3 détecté: $(python3 --version)"

# Vérifier pip
if ! command -v pip3 &> /dev/null; then
    echo "pip3 n'est pas installé"
    echo "Installation de pip..."
    sudo apt update && sudo apt install -y python3-pip
fi

echo "pip3 disponible"

# Créer un environnement virtuel (optionnel)
read -p "Voulez-vous créer un environnement virtuel ? (y/N): " create_venv
if [[ $create_venv =~ ^[Yy]$ ]]; then
    echo "Création de l'environnement virtuel..."
    python3 -m venv venv
    source venv/bin/activate
    echo "Environnement virtuel activé"
fi

# Installer les dépendances
echo "Installation des dépendances Python..."
pip3 install -r requirements.txt

if [ $? -eq 0 ]; then
    echo "Dépendances installées avec succès"
else
    echo "Erreur lors de l'installation des dépendances"
    exit 1
fi

# Vérifier les outils système nécessaires
echo "Vérification des outils système..."

if ! command -v ping &> /dev/null; then
    echo "ping n'est pas disponible - installation recommandée"
    sudo apt update && sudo apt install -y iputils-ping
fi

if ! command -v ip &> /dev/null; then
    echo "ip n'est pas disponible - installation recommandée"
    sudo apt update && sudo apt install -y iproute2
fi

echo "Outils système vérifiés"

# Créer le dossier static s'il n'existe pas
mkdir -p static

echo ""
echo "Installation terminée avec succès"
echo ""
echo "Pour lancer l'application :"
echo "  python3 app.py"
echo ""
echo "Puis ouvrez votre navigateur sur :"
echo "  http://localhost:8000"
echo ""

# Proposer de lancer l'application
read -p "Voulez-vous lancer l'application maintenant ? (y/N): " launch_now
if [[ $launch_now =~ ^[Yy]$ ]]; then
    echo "Lancement de Network Scanner..."
    python3 app.py
fi
