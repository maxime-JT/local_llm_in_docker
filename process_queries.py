import requests
import pandas as pd
from tqdm import tqdm
import multiprocessing
import atexit


def infer_request_type(text, instance_url):
    print(f"Process {multiprocessing.current_process().name} querying {instance_url} for text: {text[:30]}...")
    prompt = (
        "Indique si cette demande utilisateur correspond à une requête d'export de données "
        "ou à un autre type de demande. Réponds uniquement par 'export' ou 'autre'.\n\n"
        f"Demande : {text}"
    )
    try:
        response = requests.post(
            f"{instance_url}/api/generate",
            json={
                "model": "llama3",
                "prompt": prompt,
                "stream": False,
            },
            timeout=180
        )
        response.raise_for_status()
        return response.json()["response"].strip().lower()
    except Exception as e:
        return f"[{instance_url}] Erreur : {e}"


def process_partition(df_subset, instance_url, instance_id):
    print(f"Starting process_partition on instance {instance_id} with {len(df_subset)} queries")
    df_subset["type_requete"] = df_subset["query"].apply(
        lambda x: infer_request_type(x, instance_url)
    )
    print(f"Finished process_partition on instance {instance_id}")
    return df_subset


def process_all(df, instance_urls):
    chunks = []
    num_instances = len(instance_urls)
    dfs = [df.iloc[i::num_instances].copy() for i in range(num_instances)]

    with multiprocessing.Pool(processes=num_instances) as pool:
        results = [
            pool.apply_async(process_partition, (dfs[i], instance_urls[i], i + 1))
            for i in range(num_instances)
        ]
        chunks = [r.get() for r in results]

    final_df = pd.concat(chunks).sort_index()
    return final_df


# 🔧 Patch pour nettoyer les sémaphores sur MacOS (facultatif mais propre)
@atexit.register
def cleanup_semaphores():
    try:
        multiprocessing.resource_tracker._resource_tracker.cleanup()
    except Exception:
        pass
