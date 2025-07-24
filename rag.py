import pandas as pd
import os
from dotenv import load_dotenv

from langchain_community.document_loaders import DirectoryLoader, PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_openai import ChatOpenAI
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
import json
from difflib import get_close_matches
import re
from langchain_core.documents import Document

# 1. Carica .env e la chiave
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
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

# 3. Chunking
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=800,
    chunk_overlap=150
)
docs = text_splitter.split_documents(documents)

# 4. Crea embeddings
embedding = OpenAIEmbeddings()

# 5. Costruisci FAISS
db = FAISS.from_documents(docs, embedding)

# 6. Crea retriever con k=5
retriever = db.as_retriever(search_kwargs={"k": 5})

# 7. Carica dish_mapping.json se esiste
mapping_path = "Hackapizza Dataset/Misc/dish_mapping.json"
if os.path.exists(mapping_path):
    with open(mapping_path, "r", encoding="utf-8") as f:
        dish_mapping = json.load(f)
    dish_names = list(dish_mapping.keys())
else:
    dish_mapping = {}
    dish_names = []

# 8. Prepara il prompt
def make_prompt_template(dish_names):
    piatti_string = "\n".join(dish_names) if dish_names else ""
    return f"""
Sei un assistente che risponde a domande sui menu dei ristoranti.
Questa è la lista completa dei piatti disponibili:
{piatti_string}

Utilizza SOLO i nomi esatti da questa lista per rispondere.
Rispondi elencando ESCLUSIVAMENTE i nomi dei piatti che soddisfano la domanda, separati da virgola.
Se nessun piatto è adatto, rispondi "Nessuno".

Contesto:
{{context}}

Domanda: {{question}}
Risposta:
"""
prompt_template = make_prompt_template(dish_names)
PROMPT = PromptTemplate(
    input_variables=["context", "question"],
    template=prompt_template
)

# 9. Crea LLM e QA chain
llm = ChatOpenAI(model="gpt-3.5-turbo")
qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    chain_type="stuff",
    retriever=retriever,
    return_source_documents=True,
    chain_type_kwargs={"prompt": PROMPT}
)

# 10. Carica domande dal CSV
df_domande = pd.read_csv("Hackapizza Dataset/domande.csv")
if 'domanda' in df_domande.columns:
    domanda_col = 'domanda'
elif 'question' in df_domande.columns:
    domanda_col = 'question'
else:
    domanda_col = df_domande.columns[1]

# 11. Loop sulle domande e stampa risposta, fonti, match e chunk
for n, (idx, row) in enumerate(df_domande.iterrows(), 1):
    query = str(row[domanda_col])
    print(f"\n➡️ Domanda {n}: {query}")
    result = qa_chain.invoke({"query": query})

    # Risposta generata
    print("✅ Risposta:", result['result'])

    # File usati come fonte
    fonti = set()
    for doc in result['source_documents']:
        source = doc.metadata.get("source", "sconosciuto")
        filename = os.path.basename(source)
        fonti.add(filename)
    print("📄 Documenti usati:", ", ".join(sorted(fonti)))

    # Contenuto dei chunk
    print("📦 Chunk recuperati:")
    for i, doc in enumerate(result['source_documents'], 1):
        source = doc.metadata.get("source", "sconosciuto")
        filename = os.path.basename(source)
        print(f"--- Chunk {i} da '{filename}' ---")
        print(doc.page_content.strip())
        print("―" * 40)

    # Matching piatti
    if dish_names:
        risposta = result['result']
        candidate_dishes = [x.strip() for x in risposta.split(",") if x.strip().lower() != "nessuno"]
        if candidate_dishes:
            print("🔎 Matching piatti trovati:")
            for cand in candidate_dishes:
                if cand in dish_mapping:
                    print(f"  '{cand}' → ID: {dish_mapping[cand]}")
                else:
                    print(f"  '{cand}' → nessun match trovato")
        else:
            print("🔎 Matching piatti trovati: Nessuno")

    if n == 4:
        break
