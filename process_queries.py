import pandas as pd
import requests
import time
import multiprocessing
from tqdm import tqdm

DEFAULT_PROMPT = "Dis-moi s'il s'agit d'une requête d'export ou d'un autre type de demande."

def query_ollama(prompt, base_url, model):
    try:
        response = requests.post(f"{base_url}/api/generate", json={
            "model": model,
            "prompt": prompt,
            "stream": False
        }, timeout=60)
        response.raise_for_status()
        return response.json()["response"].strip()
    except Exception as e:
        print(f"[{base_url}] Erreur : {e}")
        return "Erreur"

def process_partition(partition_df, instance_url, return_dict, idx, model, base_prompt):
    output = []
    print(f"🟢 Début du traitement sur {instance_url} ({len(partition_df)} requêtes)")
    for _, row in tqdm(partition_df.iterrows(), total=len(partition_df), desc=f"Instance {idx+1}", position=idx):
        full_prompt = f"{row['query']}\n\n{base_prompt}"
        response = query_ollama(full_prompt, instance_url, model)
        output.append(response)
        time.sleep(0.5)
    partition_df = partition_df.copy()
    partition_df["type_requete"] = output
    return_dict[idx] = partition_df

def process_csv(csv_path, output_path, model, instances, base_prompt=DEFAULT_PROMPT):
    df = pd.read_csv(csv_path)
    nb_instances = len(instances)
    partitions = [df.iloc[i::nb_instances].copy() for i in range(nb_instances)]

    manager = multiprocessing.Manager()
    return_dict = manager.dict()
    processes = []

    for i, instance_url in enumerate(instances):
        p = multiprocessing.Process(
            target=process_partition,
            args=(partitions[i], instance_url, return_dict, i, model, base_prompt)
        )
        p.start()
        processes.append(p)

    for p in processes:
        p.join()

    df_final = pd.concat([return_dict[i] for i in range(nb_instances)]).sort_index()
    df_final.to_csv(output_path, index=False, sep=";")
    print(f"\n✅ Résultat final enregistré dans {output_path}")
