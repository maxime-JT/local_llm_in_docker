import argparse
import pandas as pd
from process_queries import process_all


def main():
    parser = argparse.ArgumentParser(description="Traitement parallèle avec Ollama sur plusieurs instances Docker")
    parser.add_argument("input_csv", help="Chemin vers le fichier CSV d'entrée avec une colonne 'query'")
    parser.add_argument("-o", "--output_csv", default="resultat.csv", help="Chemin du fichier CSV de sortie")
    parser.add_argument(
        "-i",
        "--instances",
        nargs="+",
        required=True,
        help="Liste des URLs des instances Ollama, par ex. http://localhost:11434 http://localhost:11435",
    )
    args = parser.parse_args()

    print("📥 Lecture du fichier CSV...")
    df = pd.read_csv(args.input_csv)

    print(f"🟢 Lancement du traitement sur {len(args.instances)} instance(s) Ollama...")
    df_result = process_all(df, args.instances)

    print(f"💾 Sauvegarde dans {args.output_csv}...")
    df_result.to_csv(args.output_csv, index=False)

    print(f"✅ Résultat final enregistré dans {args.output_csv}")


if __name__ == "__main__":
    main()
