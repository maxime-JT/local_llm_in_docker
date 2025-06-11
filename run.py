import argparse
import pandas as pd
from process_queries import process_all


def main():
    parser = argparse.ArgumentParser(description="Traiter un CSV avec plusieurs instances Ollama.")
    parser.add_argument("input_csv", help="Chemin vers le fichier CSV d'entrée (avec une colonne 'query').")
    parser.add_argument("-o", "--output_csv", help="Fichier de sortie", default="resultat.csv")
    parser.add_argument("-i", "--instances", nargs="+", required=True,
                        help="Liste des URLs Ollama (ex: http://localhost:11434 http://localhost:11435)")

    args = parser.parse_args()

    print("📥 Lecture du fichier CSV...")
    df = pd.read_csv(args.input_csv)

    if 'query' not in df.columns:
        raise ValueError("Le fichier CSV doit contenir une colonne nommée 'query'.")

    prompt = (
        "Voici une requête utilisateur.\n"
        "Réponds uniquement par « export » si la demande implique l’extraction de données (fichier, liste, emails, téléphone…).\n"
        "Sinon, réponds par « autre ».\n"
        "Ne fais aucune autre phrase ni explication."
    )

    print(f"🟢 Lancement du traitement sur {len(args.instances)} instance(s) Ollama...")
    df_result = process_all(df, prompt, args.instances)

    print(f"💾 Sauvegarde dans {args.output_csv}...")
    df_result.to_csv(args.output_csv, index=False)
    print("✅ Résultat final enregistré dans", args.output_csv)


if __name__ == "__main__":
    main()
