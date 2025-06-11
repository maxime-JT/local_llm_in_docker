import argparse
from process_queries import process_csv

def main():
    parser = argparse.ArgumentParser(description="Traitement de requêtes via Ollama")
    parser.add_argument("input_csv", help="Fichier CSV d'entrée avec une colonne 'query'")
    parser.add_argument("-o", "--output", default="query_with_type.csv", help="Nom du fichier CSV de sortie")
    parser.add_argument("-m", "--model", default="llama3", help="Nom du modèle Ollama à utiliser")
    parser.add_argument("-i", "--instances", nargs="+", default=[
        "http://localhost:11434",
        "http://localhost:11435",
        "http://localhost:11436"
    ], help="Liste des URLs des instances Ollama")
    parser.add_argument("--prompt", default=None, help="Prompt personnalisé (optionnel)")

    args = parser.parse_args()
    prompt = args.prompt or "Dis-moi s'il s'agit d'une requête d'export ou d'un autre type de demande."

    process_csv(
        csv_path=args.input_csv,
        output_path=args.output,
        model=args.model,
        instances=args.instances,
        base_prompt=prompt
    )

if __name__ == "__main__":
    main()
