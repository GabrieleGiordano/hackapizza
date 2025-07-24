import os
import openai
import pandas as pd
import json
import difflib
from tqdm import tqdm
from dotenv import load_dotenv

# Carica variabili d'ambiente
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# Percorsi
mapping_path = "Hackapizza Dataset/Misc/dish_mapping.json"
domande_path = "Hackapizza Dataset/domande.csv"
ricette_path = "Hackapizza Dataset/ricette_estratte_agentico.csv"

# Carica i file
df_domande = pd.read_csv(domande_path)
df_ricette = pd.read_csv(ricette_path)
with open(mapping_path, "r", encoding="utf-8") as f:
    dish_mapping = json.load(f)

# Rimuovi colonne inutili
df_ricette = df_ricette.drop(columns=["ristorante"], errors="ignore")

# Prepara lista ricette testuali
lista_piatti = [f"{row['nome_ricetta']}: {row['ingredienti']}" for _, row in df_ricette.iterrows()]

# Funzione per dividere le ricette in blocchi
def chunk_lista(lista, max_words=2500):
    chunks = []
    current_chunk = []
    current_len = 0

    for voce in lista:
        voce_len = len(voce.split())
        if current_len + voce_len > max_words:
            chunks.append(current_chunk)
            current_chunk = [voce]
            current_len = voce_len
        else:
            current_chunk.append(voce)
            current_len += voce_len
    if current_chunk:
        chunks.append(current_chunk)
    return chunks

# Suddividi in blocchi
blocchi = chunk_lista(lista_piatti, max_words=2500)

# Fuzzy matching tra nome predetto e chiavi del mapping
def trova_match(nome_predetto, dish_mapping_keys):
    match = difflib.get_close_matches(nome_predetto, dish_mapping_keys, n=1, cutoff=0.8)
    return match[0] if match else None

# Funzione agentica su ciascun blocco
def chiedi_ai_llm_con_chunk(domanda):
    ricette_rilevanti = set()
    for blocco in blocchi:
        contesto = "\n".join(blocco)
        messaggi = [
            {
                "role": "system",
                "content": (
                    "Sei un assistente che seleziona ricette esatte da una lista.\n"
                    "Ogni riga è nel formato 'nome: ingredienti'.\n"
                    "Devi rispondere alla domanda dell'utente **selezionando da 1 a massimo 7 nomi esattamente come compaiono nella lista**, separati da virgola.\n"
                    "Non inventare nomi. Non riscrivere. Non aggiungere testo.\n\n"
                    f"Ecco le ricette:\n{contesto}"
                )
            },
            {"role": "user", "content": domanda}
        ]

        try:
            response = openai.ChatCompletion.create(
                model="gpt-4o",
                messages=messaggi,
                temperature=0.0,
                max_tokens=150
            )
            risposta = response['choices'][0]['message']['content'].strip()
            nomi = [r.strip() for r in risposta.split(",") if r.strip()]
            ricette_rilevanti.update(nomi)
        except Exception as e:
            print(f"⚠️ Errore nel blocco: {e}")

    return list(ricette_rilevanti)[:7] if ricette_rilevanti else []

# Loop sulle domande
risultati = []

for i, domanda in tqdm(enumerate(df_domande["domanda"]), total=len(df_domande)):
    try:
        nomi_ricette = chiedi_ai_llm_con_chunk(domanda)
        ids = []

        for nome in nomi_ricette:
            match = trova_match(nome, dish_mapping.keys())
            if match:
                ids.append(str(dish_mapping[match]))

        if not ids:
            print(f"❌ Nessuna ricetta trovata per la domanda {i+1}: {domanda}")
            print(f"🔎 GPT ha risposto: {nomi_ricette}")
            result = "1"
        elif len(ids) == 1:
            result = "1"
        else:
            result = ",".join(ids)

        risultati.append({"row_id": i + 1, "result": result})

    except Exception as e:
        print(f"❌ Errore nella riga {i+1}: {e}")
        risultati.append({"row_id": i + 1, "result": "1"})

# Salva il CSV
df_output = pd.DataFrame(risultati)
df_output.to_csv("risposte.csv", index=False)
print("✅ File 'risposte.csv' salvato con successo.")