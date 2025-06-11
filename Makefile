# Nom du fichier d'entrée
INPUT_CSV ?= query.csv
OUTPUT_CSV ?= query_with_type.csv
MODEL ?= llama3
PROMPT ?= Dis-moi s'il s'agit d'une requête d'export ou d'un autre type de demande.
INSTANCES ?= http://localhost:11434 http://localhost:11435 http://localhost:11436

.PHONY: help venv install run docker-start docker-stop clean

help:
	@echo ""
	@echo "Commandes disponibles :"
	@echo "  make venv           → Crée un environnement virtuel (./venv)"
	@echo "  make install        → Active venv et installe les dépendances"
	@echo "  make run            → Lance le script sur $(INPUT_CSV) avec $(INSTANCES)"
	@echo "  make docker-start   → Lance 3 containers Ollama (ports 11434-11436)"
	@echo "  make docker-stop    → Stoppe et supprime les containers Ollama"
	@echo "  make clean          → Supprime venv et fichiers temporaires"
	@echo ""

venv:
	python3 -m venv venv

install: venv
	source venv/bin/activate && pip install --upgrade pip && pip install -r requirements.txt

run:
	source venv/bin/activate && python run.py $(INPUT_CSV) -o $(OUTPUT_CSV) -m $(MODEL) -i $(INSTANCES) --prompt "$(PROMPT)"

docker-start:
	docker run -d -p 11434:11434 --name ollama1 ollama/ollama
	docker run -d -p 11435:11434 --name ollama2 ollama/ollama
	docker run -d -p 11436:11434 --name ollama3 ollama/ollama
	sleep 5
	docker exec -it ollama1 ollama pull $(MODEL)
	docker exec -it ollama2 ollama pull $(MODEL)
	docker exec -it ollama3 ollama pull $(MODEL)

docker-stop:
	docker rm -f ollama1 ollama2 ollama3 || true

clean:
	rm -rf venv __pycache__ *.pyc *.pyo query_with_type.csv