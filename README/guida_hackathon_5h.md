# Guida Strategica - Hackathon Hackapizza (5-6 ore)

## 🎯 Obiettivo
Sviluppare un sistema MVP di raccomandazione piatti che risponda alle query in linguaggio naturale utilizzando tecniche di Generative AI.

## ⏱️ Pianificazione Temporale Suggerita

### Ora 1: Setup e Comprensione (09:00-10:00)
- [ ] 📋 **Leggere README_PARTECIPANTI.md** (formato submission)
- [ ] Leggere overview.txt e data_description.txt
- [ ] Esplorare la struttura del dataset
- [ ] Configurare ambiente di sviluppo (Python, libraries)
- [ ] Leggere le prime 10 domande per capire la complessità

### Ora 2: Prototipo Base (10:00-11:00)
- [ ] Implementare un semplice parser per dish_mapping.json
- [ ] Creare un sistema di embedding basilare (OpenAI/Sentence-Transformers)
- [ ] Testare con 2-3 menu PDF più piccoli
- [ ] Rispondere alle prime 5 domande più semplici

### Ora 3: Espansione (11:00-12:00)
- [ ] Includere tutti i 15 menu
- [ ] Migliorare il sistema di similarity search
- [ ] Aggiungere parsing per ingredienti e tecniche
- [ ] **Usare `validate_submission.py` per testare formato**
- [ ] Testare su 10-15 domande

### Ora 4: Affinamento (12:00-13:00)
- [ ] Integrare blog post HTML
- [ ] Gestire query con location (ristoranti, pianeti)
- [ ] Implementare filtri per esclusioni ("ma non contiene...")
- [ ] Testare su 25-30 domande

### Ora 5: Ottimizzazione (13:00-14:00)
- [ ] Integrare normative (Codice Galattico.pdf)
- [ ] Gestire licenze chef e certificazioni
- [ ] Testare su tutte le 50 domande
- [ ] Ottimizzare performance e accuracy

### Ora 6: Finalizzazione (14:00-15:00)
- [ ] Generare output CSV finale
- [ ] **Validare con `validate_submission.py --show-mock-eval`**
- [ ] Testing e debugging
- [ ] Documentazione e presentazione
- [ ] **Preparazione file CSV per consegna** (nessun upload online richiesto)

## 🛠️ Stack Tecnologico Consigliato

### Minimal Setup
```python
# Librerie essenziali
pip install openai pandas numpy scikit-learn
pip install sentence-transformers  # alternativa a OpenAI
pip install PyPDF2 pdfplumber  # parsing PDF
pip install beautifulsoup4  # parsing HTML
```

### Approccio Architetturale
1. **Document Loader**: Carica e preprocessa PDF/HTML
2. **Embedding Generator**: Crea embeddings per piatti e descrizioni
3. **Query Processor**: Interpreta query in linguaggio naturale
4. **Similarity Search**: Trova piatti rilevanti
5. **Filter Engine**: Applica filtri e esclusioni
6. **Response Generator**: Formatta output con ID piatti

## 📋 Priorità delle Funzionalità

### 🟢 MUST HAVE (Priorità Alta)
- Parsing di dish_mapping.json
- Estrazione testo da PDF menu
- Sistema di embedding e similarity search
- Gestione query semplici su ingredienti
- Output formato CSV corretto

### 🟡 SHOULD HAVE (Priorità Media)
- Parsing tecniche di cottura
- Filtri per ristoranti/location
- Gestione esclusioni ("ma non contiene")
- Query con operatori logici (AND/OR)

### 🔴 COULD HAVE (Priorità Bassa)
- Integrazione normative complete
- Gestione licenze chef complessa
- Calcoli distanze tra pianeti
- Validazione ordini professionali

## 💡 Suggerimenti Pratici

### Per Risparmiare Tempo:
- Usate librerie pre-esistenti (OpenAI API, Langchain)
- Iniziate con i menu più piccoli (evitate Datapizza.pdf inizialmente)
- Testate incrementalmente: 5→10→25→50 domande
- **Usate `validate_submission.py` spesso per verificare il formato**
- Usate regex semplici per parsing iniziale

### Per Migliorare Accuracy:
- Preprocess text: rimuovere caratteri speciali, normalizzare
- Usate embedding context-aware
- Implementate fuzzy matching per ingredienti
- Gestite sinonimi e varianti di nomi

### Debugging Rapido:
- Stampate sempre i risultati intermedi
- Tenete log delle query che falliscono
- Usate subset di dati per test veloci
- Implementate modalità verbose per debugging

## 🎯 Metriche di Successo

### Minimum Viable Product:
- ✅ Risponde correttamente a 20/50 domande
- ✅ Output CSV formattato correttamente
- ✅ Nessun errore di runtime

### Good Solution:
- ✅ Risponde correttamente a 35/50 domande
- ✅ Gestisce query complesse
- ✅ Performance sotto 30 secondi per tutte le query

### Excellent Solution:
- ✅ Risponde correttamente a 45+/50 domande
- ✅ Gestisce edge cases
- ✅ Architettura pulita e scalabile

## 🚨 Trucchi dell'Ultimo Minuto

Se siete in ritardo:
1. Concentratevi solo sui menu più grandi (L'Etere del Gusto, Datapizza)
2. Usate OpenAI API per query complesse invece di implementare tutto
3. Hardcodate risposte per le domande più difficili se necessario
4. Assicuratevi che l'output CSV sia formattato correttamente

**Buona fortuna! 🚀** 