import pandas as pd
import requests
from multiprocessing import Pool
from tqdm import tqdm
import multiprocessing



def call_ollama(base_url, prompt, input_text, timeout=60):
    """
    Envoie une requête à une instance Ollama et retourne la réponse ou une erreur.
    """
    try:
        response = requests.post(
            f"{base_url}/api/generate",
            json={
                "model": "llama3",
                "prompt": prompt,
                "stream": False,
                "messages": [
                    {"role": "user", "content": input_text}
                ]
            },
            timeout=timeout
        )
        response.raise_for_status()
        return response.json()["response"]
    except Exception as e:
        return f"[{base_url}] Erreur : {e}"


def process_queries(df, base_url, prompt, instance_index):
    """
    Traite les requêtes de la portion de DataFrame avec une instance Ollama donnée.
    """
    results = []
    for i, row in enumerate(tqdm(df.itertuples(), total=len(df), desc=f"Instance {instance_index+1}")):
        query = row.query
        result = call_ollama(base_url, prompt, query)
        results.append(result)
    return results


def split_dataframe(df, n):
    """
    Divise un DataFrame en n parties de taille (quasi-)égale.
    """
    return [df.iloc[i::n].copy().reset_index(drop=True) for i in range(n)]


def process_all(df, prompt, base_urls):
    """
    Orchestration parallèle du traitement.
    """
    n = len(base_urls)
    sub_dfs = split_dataframe(df, n)

    print(f"📊 CSV divisé en {n} sous-ensembles. Lancement du traitement parallèle...\n")

    args = [
        (sub_dfs[i], base_urls[i], prompt, i)
        for i in range(n)
    ]

    with Pool(processes=n) as pool:
        results = pool.starmap(process_queries, args)

    # Fusion des sous-ensembles de résultats
    final_df = pd.concat([
        sub_dfs[i].assign(type_requete=results[i])
        for i in range(n)
    ], ignore_index=True)

    return final_df

    multiprocessing.resource_tracker._resource_tracker.cleanup()
