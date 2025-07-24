import os
import json
import pandas as pd
from dotenv import load_dotenv

from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import FAISS
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from langchain.schema import BaseRetriever
from pydantic import Field
from langchain_core.documents import Document

# === 1. Carica API Key ===
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY_OPENAI")
if not api_key:
    raise ValueError("⚠️ La variabile OPENAI_API_KEY non è stata trovata nel file .env")
os.environ["OPENAI_API_KEY"] = api_key

# === 2. Configurazioni ===
menu_dir = "Hackapizza Dataset/Menu"
faiss_path = "vectorstore/hackapizza_faiss"
embedding = OpenAIEmbeddings()


# === 3. Caricamento documenti PDF ===
def load_documents_from_pdfs(folder):
    docs = []
    for root, dirs, files in os.walk(folder):
        for file in files:
            if file.lower().endswith('.pdf'):
                path = os.path.join(root, file)
                loader = PyPDFLoader(path)
                docs.extend(loader.load())
    return docs


# === 4. Costruzione o caricamento FAISS ===
if os.path.exists(faiss_path):
    print("✅ Carico il vector store FAISS salvato.")
    db = FAISS.load_local(faiss_path, embedding, allow_dangerous_deserialization=True)

    # Carica anche i chunk associati da file di supporto
    chunks_path = os.path.join(faiss_path, "chunks.json")
    if not os.path.exists(chunks_path):
        raise FileNotFoundError("⚠️ Mancano i metadati dei chunk: 'chunks.json'")
    with open(chunks_path, "r", encoding="utf-8") as f:
        docs_data = json.load(f)
        all_docs_map = {
            int(k): Document(page_content=v["page_content"], metadata=v["metadata"])
            for k, v in docs_data.items()
        }
else:
    print("🛠️ Creo il vector store da zero.")
    raw_docs = load_documents_from_pdfs(menu_dir)

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=900, chunk_overlap=200)
    docs = text_splitter.split_documents(raw_docs)

    for idx, doc in enumerate(docs):
        doc.metadata['chunk_id'] = idx

    all_docs_map = {doc.metadata['chunk_id']: doc for doc in docs}

    db = FAISS.from_documents(list(all_docs_map.values()), embedding)
    db.save_local(faiss_path)

    # Salva anche i chunk con contenuto e metadati
    os.makedirs(faiss_path, exist_ok=True)
    chunks_path = os.path.join(faiss_path, "chunks.json")
    with open(chunks_path, "w", encoding="utf-8") as f:
        json.dump({
            k: {
                "page_content": v.page_content,
                "metadata": v.metadata
            }
            for k, v in all_docs_map.items()
        }, f, ensure_ascii=False, indent=2)

    print(f"💾 Vector store e chunk salvati in '{faiss_path}'.")

# === 5. Retriever personalizzato ===
base_retriever = db.as_retriever(search_kwargs={"k": 10})

class NeighborRetriever(BaseRetriever):
    base_retriever: BaseRetriever = Field(...)
    docs_map: dict = Field(...)

    def _get_relevant_documents(self, query: str):
        top_docs = self.base_retriever.get_relevant_documents(query)
        extended = []
        for d in top_docs:
            cid = d.metadata['chunk_id']
            for neighbor_cid in (cid - 1, cid, cid + 1):
                if neighbor_cid in self.docs_map:
                    extended.append(self.docs_map[neighbor_cid])
        seen = set()
        unique_docs = []
        for d in extended:
            cid = d.metadata['chunk_id']
            if cid not in seen:
                seen.add(cid)
                unique_docs.append(d)
        return unique_docs


retriever = NeighborRetriever(
    base_retriever=base_retriever,
    docs_map=all_docs_map
)
retriever = base_retriever


# === 6. Prompt personalizzato ===
def make_prompt_template(dish_mapping: dict):
    options = "\n".join(
        f"{name} ({code})" for name, code in dish_mapping.items()) if dish_mapping else "Nessun piatto disponibile."
    return f"""
Sei un assistente esperto nella ricerca di ricette all'interno di un menu strutturato.

Tutte le ricette possibili hanno un nome associato, qui riportato:
--- NOMI DEI PIATTI ---
{options}
--- FINE ---

Ricevi una domanda sul menu e una descrizione di alcune ricette che potrebbero essere rilevanti. La tua risposta deve essere un elenco di nomi di piatti che rispondono alla domanda, separati da virgola. Se non trovi nessun piatto che risponde, rispondi "Nessuno".

Ad esempio, se la domanda riguarda un ingrediente specifico, cerca nella sezione "Ingredienti" delle ricette e stabilisci se il piatto contiene tale elemento.

RICETTE POSSIBILI:
{{context}}

DOMANDA:
{{question}}

RISPOSTA:
"""


# === 7. Carica dish_mapping.json ===
dish_mapping = {}
dish_names = []
map_path = "Hackapizza Dataset/Misc/dish_mapping.json"
if os.path.exists(map_path):
    with open(map_path, "r", encoding="utf-8") as f:
        dish_mapping = json.load(f)
    dish_names = list(dish_mapping.keys())

PROMPT = PromptTemplate(
    input_variables=["context", "question"],
    template=make_prompt_template(dish_mapping)
)

# === 8. Crea LLM e RetrievalQA ===
llm = ChatOpenAI(model="gpt-3.5-turbo")
qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    chain_type="stuff",
    retriever=retriever,
    return_source_documents=True,
    chain_type_kwargs={"prompt": PROMPT}
)

# === 9. Carica CSV domande ===
df = pd.read_csv("Hackapizza Dataset/domande.csv")
if 'domanda' in df.columns:
    qcol = 'domanda'
elif 'question' in df.columns:
    qcol = 'question'
else:
    qcol = df.columns[1]

selected_indices = range(15)

try:
    df = df.loc[selected_indices]
except KeyError:
    print(f"Attenzione: alcuni indici {selected_indices} non esistono. Elaboro tutte le domande.")

# === 10. Loop sulle domande ===
for i, row in df.iterrows():
    query = str(row[qcol])
    print(f"\n➡️ Domanda [{i}]: {query}")
    result = qa_chain.invoke({"query": query})
    print("✅ Risposta:", result['result'])

    # mostra i chunk (precedente, corrente, successivo)
    print("📦 Chunk passati all'LLM:")
    for doc in result['source_documents']:
        cid = doc.metadata['chunk_id']
        # print(f"--- chunk_id {cid} ---")
        # print(doc.page_content.strip())
        # print("―" * 30)

    if dish_names:
        found = [p.strip() for p in result['result'].split(',') if p.strip().lower() != 'nessuno']
        if found:
            print("🔎 Matching:")
            for p in found:
                print(f"  {p} → {dish_mapping.get(p, 'nessun match')}")
        else:
            print("🔎 Matching: Nessuno")
