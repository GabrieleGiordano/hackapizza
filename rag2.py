import pandas as pd
import os
from dotenv import load_dotenv

from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import FAISS
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from langchain.schema import BaseRetriever
from pydantic import Field
import json
from langchain_core.documents import Document

# 1. Carica .env e la chiave
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY_OPENAI")
if not api_key:
    raise ValueError("⚠️ La variabile OPENAI_API_KEY non è stata trovata nel file .env")
os.environ["OPENAI_API_KEY"] = api_key

# 2. Carica tutti i menu (PDF)
menu_dir = "Hackapizza Dataset/Menu"
documents = []
for root, dirs, files in os.walk(menu_dir):
    for file in files:
        if file.lower().endswith('.pdf'):
            path = os.path.join(root, file)
            loader = PyPDFLoader(path)
            documents.extend(loader.load())

# 3. Chunking classico + assegnazione chunk_id
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=150
)
docs = text_splitter.split_documents(documents)
for idx, doc in enumerate(docs):
    doc.metadata['chunk_id'] = idx

# Mappa globale di tutti i chunk
all_docs_map = {d.metadata['chunk_id']: d for d in docs}

# 4. Crea embeddings e FAISS
embedding = OpenAIEmbeddings()
db = FAISS.from_documents(list(all_docs_map.values()), embedding)

# 5. Retriever base con k=5
base_retriever = db.as_retriever(search_kwargs={"k": 3})


# 6. Implementa NeighborRetriever ereditando BaseRetriever correttamente
class NeighborRetriever(BaseRetriever):
    base_retriever: BaseRetriever = Field(...)
    docs_map: dict = Field(...)

    def _get_relevant_documents(self, query: str):
        # recupera i top k chunk
        top_docs = self.base_retriever.get_relevant_documents(query)
        extended = []
        for d in top_docs:
            cid = d.metadata['chunk_id']
            for neighbor_cid in (cid - 1, cid, cid + 1):
                if neighbor_cid in self.docs_map:
                    extended.append(self.docs_map[neighbor_cid])
        # rimuove duplicati mantenendo l'ordine
        seen = set()
        unique_docs = []
        for d in extended:
            cid = d.metadata['chunk_id']
            if cid not in seen:
                seen.add(cid)
                unique_docs.append(d)
        return unique_docs


# 7. Instanzia NeighborRetriever
retriever = NeighborRetriever(
    base_retriever=base_retriever,
    docs_map=all_docs_map
)

# 8. Carica dish_mapping.json se esiste
dish_mapping = {}
dish_names = []
map_path = "Hackapizza Dataset/Misc/dish_mapping.json"
if os.path.exists(map_path):
    with open(map_path, "r", encoding="utf-8") as f:
        dish_mapping = json.load(f)
    dish_names = list(dish_mapping.keys())


# 9. Prompt template aggiornato per includere nome e codice
def make_prompt_template(dish_mapping: dict):
    """
    Crea un prompt in cui:
    - Viene mostrato l'elenco di piatti con nome e codice tra parentesi.
    - Si istruisce l'LLM a cercare nei chunk il piatto corrispondente, anche basandosi su ingredienti.
    """
    # Prepara le righe "NomePiatti (Codice)"
    options = "".join(f"{name} ({code})" for name, code in dish_mapping.items()) if dish_mapping else ""
    return f"""
Sei un assistente esperto nella ricerca di ricette all'interno di un menu strutturato.
Di seguito l'elenco completo dei piatti disponibili, con il loro codice univoco:
--- PIATTI DISPONIBILI ---
{options}
--- FINE ELENCO ---

ISTRUZIONI:
1. Leggi attentamente il CONTESTO fornito.
2. Se la domanda riguarda un ingrediente specifico, cerca nella sezione "Ingredienti:" il piatto il cui elenco di ingredienti lo contiene.
3. Se la domanda riguarda altre caratteristiche (prezzo, descrizione, ecc.), trova il piatto nell'elenco che meglio risponde.
4. Rispondi ESCLUSIVAMENTE elencando il nome del piatto (con il codice), separati da virgola.
5. NON aggiungere spiegazioni o commenti extra: se nessun piatto soddisfa la domanda, rispondi unicamente "Nessuno".

CONTESTO:
{{context}}

DOMANDA:
{{question}}

RISPOSTA:
"""


# Aggiorna PromptTemplate con dish_mapping
PROMPT = PromptTemplate(
    input_variables=["context", "question"],
    template=make_prompt_template(dish_mapping)
)

# 10. Crea LLM e RetrievalQA
llm = ChatOpenAI(model="gpt-3.5-turbo")
qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    chain_type="stuff",
    retriever=retriever,
    return_source_documents=True,
    chain_type_kwargs={"prompt": PROMPT}
)

# 11. Carica domande e seleziona in codice quali processare
import pandas as pd

df = pd.read_csv("Hackapizza Dataset/domande.csv")
if 'domanda' in df.columns:
    qcol = 'domanda'
elif 'question' in df.columns:
    qcol = 'question'
else:
    qcol = df.columns[1]

# Specifica qui gli indici da processare
selected_indices = [0, 2, 5]

# Filtra il DataFrame in base agli indici
try:
    df = df.loc[selected_indices]
except KeyError:
    print(f"Attenzione: alcuni indici {selected_indices} non esistono. Elaboro tutte le domande.")

# Loop sulle domande selezionate
for i, row in df.iterrows():
    query = str(row[qcol])
    print(f"\n➡️ Domanda [{i}]: {query}")
    result = qa_chain.invoke({"query": query})
    print("✅ Risposta:", result['result'])

    # mostra i chunk (precedente, corrente, successivo)
    print("📦 Chunk passati all'LLM:")
    for doc in result['source_documents']:
        cid = doc.metadata['chunk_id']
        print(f"--- chunk_id {cid} ---")
        print(doc.page_content.strip())
        print("―" * 30)

    # match piatti e codice
    if dish_names:
        found = [p.strip() for p in result['result'].split(',') if p.strip().lower() != 'nessuno']
        if found:
            print("🔎 Matching:")
            for p in found:
                print(f"  {p} → {dish_mapping.get(p, 'nessun match')}")
        else:
            print("🔎 Matching: Nessuno")
