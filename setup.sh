#!/bin/bash

set -e

echo "🚀 Installation de l'environnement Python..."
python3 -m venv venv
source venv/bin/activate

echo "📦 Installation des dépendances..."
pip install --upgrade pip
pip install -r requirements.txt

echo ""
read -p "Souhaitez-vous lancer les instances Docker d'Ollama maintenant ? (y/n) " answer
if [[ "$answer" == "y" || "$answer" == "Y" ]]; then
    echo "🐳 Lancement des containers Docker Ollama..."
    docker run -d -p 11434:11434 --name ollama1 ollama/ollama
    docker run -d -p 11435:11434 --name ollama2 ollama/ollama
    docker run -d -p 11436:11434 --name ollama3 ollama/ollama

    echo "⏳ Attente 5 secondes pour démarrage des containers..."
    sleep 5

    echo "⬇️ Téléchargement du modèle llama3 dans chaque container..."
    docker exec -it ollama1 ollama pull llama3
    docker exec -it ollama2 ollama pull llama3
    docker exec -it ollama3 ollama pull llama3
fi

echo ""
echo "✅ Installation terminée."
echo "➡️ Vous pouvez maintenant activer votre environnement avec :"
echo "   source venv/bin/activate"
echo "➡️ Et exécuter :"
echo "   python run.py query.csv -o resultat.csv -i http://localhost:11434 http://localhost:11435 http://localhost:11436"
echo ""
