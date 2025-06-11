import argparse
import json
import pandas as pd
from tqdm import tqdm
import multiprocessing
import requests
import hashlib


def infer(text, prompt, instance_url):
    try:
        full_prompt = f"{prompt}\n\nDemande : {text}"
        print(f"\n🔹 Envoi du prompt à {instance_url}\n   ➤ Texte de la requête : {text}\n   ➤ Prompt utilisé       : {prompt[:80]}{'...' if len(prompt) > 80 else ''}")
        response = requests.post(
            f"{instance_url}/api/generate",
            json={"model": "llama3", "prompt": full_prompt, "stream": False},
            timeout=180
        )
        response.raise_for_status()
        return response.json()["response"].strip().lower()
    except Exception as e:
        return f"[{instance_url}] Erreur : {e}"


def safe_col_name(output_col_name):
    return "response_" + output_col_name


def process_partition(df_subset, prompts_config, instance_url, instance_id):
    for config in prompts_config:
        column = config["column"]
        prompt = config["prompt"]
        output_col = f"{safe_col_name(config["output_column"])}"

        df_subset[output_col] = df_subset[column].progress_apply(
            lambda x: infer(x, prompt, instance_url)
        )

    return df_subset


def process_all(df, prompts_config, instance_urls):
    num_instances = len(instance_urls)
    dfs = [df.iloc[i::num_instances].copy() for i in range(num_instances)]

    with multiprocessing.Pool(processes=num_instances) as pool:
        results = [
            pool.apply_async(process_partition, (dfs[i], prompts_config, instance_urls[i], i + 1))
            for i in range(num_instances)
        ]
        return pd.concat([r.get() for r in results]).sort_index()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("input_csv", help="Fichier CSV d'entrée")
    parser.add_argument("-o", "--output", default="resultat.csv", help="Fichier CSV de sortie")
    parser.add_argument("-q", "--queries", default="queries.json", help="Fichier JSON des prompts")
    parser.add_argument("-i", "--instances", nargs="+", required=True, help="Liste des URLs des instances")
    args = parser.parse_args()

    print("📥 Lecture du fichier CSV...")
    df = pd.read_csv(args.input_csv)

    with open(args.queries, encoding="utf-8") as f:
        prompts_config = json.load(f)

    print(f"🟢 Lancement du traitement sur {len(args.instances)} instance(s) Ollama...")
    df_result = process_all(df, prompts_config, args.instances)

    print("💾 Sauvegarde dans", args.output, "...")
    df_result.to_csv(args.output, index=False)
    print("✅ Terminé.")
