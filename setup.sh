#!/bin/bash

set -e

echo "🚀 Installation de l'environnement Python..."
python3 -m venv venv
source venv/bin/activate

echo "📦 Installation des dépendances..."
pip install --upgrade pip
pip install -r requirements.txt

echo "✅ Containers lancés."
docker ps --filter "name=ollama"

echo ""
read -p "Souhaitez-vous lancer les instances Docker d'Ollama maintenant ? (y/n) " answer
if [[ "$answer" == "y" || "$answer" == "Y" ]]; then

    echo "🧹 Suppression des containers ollama1, ollama2 s'ils existent..."
    docker rm -f ollama1 ollama2 2>/dev/null || true

    echo "🐳 Lancement des containers Docker Ollama..."
    echo "🚀 Démarrage des containers avec 3 CPU max chacun..."
    docker run --name ollama1 --cpus=4 --memory=6g -p 11434:11434 -d ollama/ollama
    docker run --name ollama2 --cpus=4 --memory=6g -p 11435:11434 -d ollama/ollama

    echo "⏳ Attente 5 secondes pour démarrage des containers..."
    sleep 5

    echo "⬇️ Téléchargement du modèle llama3 dans chaque container..."
    docker exec -it ollama1 ollama pull llama3
    docker exec -it ollama2 ollama pull llama3

    echo "⏳ Téléchargement et chargement initial du modèle sur chaque instance..."

    curl -s -X POST http://localhost:11434/api/pull \
      -H "Content-Type: application/json" \
      -d '{"name": "llama3"}' > /dev/null && echo "✅ Modèle chargé sur port 11434"

    curl -s -X POST http://localhost:11435/api/pull \
      -H "Content-Type: application/json" \
      -d '{"name": "llama3"}' > /dev/null && echo "✅ Modèle chargé sur port 11435"

fi

echo ""
echo "✅ Installation terminée."
echo "➡️ Vous pouvez maintenant activer votre environnement avec :"
echo "   source venv/bin/activate"
echo "➡️ Et exécuter :"
echo "   python run.py query.csv -o resultat.csv -i http://localhost:11434 http://localhost:11435"
echo ""
