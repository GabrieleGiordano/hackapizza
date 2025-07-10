# 🍕 Hackathon Hackapizza

Benvenuti all'hackathon di data science **Hackapizza**! Un'esperienza immersiva nel mondo della ristorazione galattica dove dovrete sviluppare un sistema intelligente per rispondere a domande sui piatti di ristoranti intergalattici.

## 🌟 Panoramica

Il vostro compito è sviluppare un sistema che, utilizzando i dati forniti, riesca a rispondere correttamente a 50 domande sui piatti disponibili nei ristoranti del **Pizzaverse**. Il sistema deve essere in grado di interpretare richieste in linguaggio naturale e restituire gli ID dei piatti appropriati.

## 🎯 Obiettivo

Creare un sistema intelligente che:
- Analizza i menu dei ristoranti galattici
- Interpreta le domande sui piatti
- Restituisce gli ID corretti dei piatti che soddisfano i criteri richiesti
- Ottimizza le risposte per il **punteggio Jaccard Similarity**

## 📊 Sistema di Valutazione

### 🔢 Metrica: Jaccard Similarity

Il punteggio viene calcolato utilizzando la **Jaccard Similarity** per ogni domanda:

```
Jaccard = |Intersezione| / |Unione|
```

### 📈 Esempio Pratico

**Domanda**: "Esempio generico di ricerca piatti"

**Risposta Corretta**: `[100, 200, 300, 400]`
**Tua Risposta**: `[100, 200, 300, 500]`

- **Intersezione**: `[100, 200, 300]` = 3 elementi
- **Unione**: `[100, 200, 300, 400, 500]` = 5 elementi  
- **Jaccard**: `3/5 = 0.60` (60%)

### 🎯 Interpretazione dei Punteggi

| Punteggio | Qualità | Descrizione |
|-----------|---------|-------------|
| **90-100%** | 🏆 Eccellente | Risposta quasi perfetta |
| **70-89%** | 🥇 Molto buona | Maggioranza corretta |
| **50-69%** | 🥈 Buona | Metà corretta |
| **30-49%** | 🥉 Media | Alcuni elementi corretti |
| **10-29%** | ⚠️ Scarsa | Pochi elementi corretti |
| **0-9%** | ❌ Molto scarsa | Quasi nessun elemento corretto |

### 🔄 Modalità di Valutazione

#### 📊 **Public Mode** (Durante l'hackathon)
- Valuta solo le **25 domande pubbliche**
- Fornisce feedback immediato ai team
- Permette miglioramenti iterativi

#### 🔒 **Private Mode** (Risultato finale)
- Valuta solo le **25 domande private**
- Non visibile durante l'hackathon
- Determina la classifica finale

#### 🌐 **All Mode** (Analisi completa)
- Valuta tutte le **50 domande**
- Punteggio medio delle due modalità
- Usato per analisi post-hackathon

## 📝 Formato Submission

### CSV Richiesto
```csv
row_id,result
1,"101,102,103"
2,"104"
3,"105,106"
4,"107,108"
5,"109"
```

### 📋 Specifiche
- **50 righe esatte** (domande 1-50)
- **ID numerici** dei piatti (usa `dish_mapping.json`)
- **Virgolette** attorno al campo result: `"101,102,103"`
- **Nessun campo vuoto** - ogni domanda deve avere una risposta

**IMPORTANTE**: Il campo `result` non può essere mai vuoto. C'è sempre almeno un piatto che soddisfa ogni query.

## 🚀 Sistema di Valutazione in Tempo Reale

### 🌐 **Sistema Ngrok con Auto-Switch** (RACCOMANDATO)

Il sistema utilizza **ngrok** con un tunnel manager intelligente che:
- ✅ **Riavvio automatico** quando il tunnel cade
- ✅ **Switch URL automatico** senza interruzioni
- ✅ **Notifiche automatiche** dei cambi URL
- ✅ **Link interni sempre aggiornati** nella dashboard

#### **URL Dinamico**
L'URL del sistema cambia automaticamente quando necessario. Controllerai sempre:
- **File URL corrente**: `current_tunnel_url.txt`
- **Dashboard**: Sempre accessibile all'URL attuale
- **Notifiche**: `NUOVO_URL.txt` quando cambia

#### **Comandi per l'Organizzatore**

**Avvio sistema completo**:
```bash
# Durante l'hackathon (Public Mode)
python auto_tunnel_manager.py \
  --port 5000 \
  --evaluation-type Public \
  --check-interval 10
```

**Cambio modalità durante l'evento**:
```bash
# Modalità Private (valutazione finale)
python auto_tunnel_manager.py \
  --port 5000 \
  --evaluation-type Private \
  --check-interval 10

# Modalità All (analisi completa)
python auto_tunnel_manager.py \
  --port 5000 \
  --evaluation-type All \
  --check-interval 10
```

#### **Sistema di Recovery Automatico**
- **Monitoring**: Controlla tunnel e server ogni 10 secondi
- **Auto-restart**: Riavvia automaticamente componenti in errore  
- **URL tracking**: Salva e condivide automaticamente i nuovi URL
- **Zero downtime**: I partecipanti non devono fare nulla

### 📱 **Come Ottenere l'URL Attuale**

Durante l'hackathon, i partecipanti possono sempre trovare l'URL corrente:

1. **File di stato**:
   ```bash
   cat current_tunnel_url.txt
   ```

2. **Notifiche automatiche**:
   ```bash
   cat NUOVO_URL.txt
   ```

3. **Status JSON**:
   ```bash
   cat tunnel_status.json
   ```

## 🎮 Come Partecipare

### 1. **Analizza il Dataset**
- Studia i menu PDF in `Hackapizza Dataset/Menu/`
- Leggi i blog post in `Hackapizza Dataset/Blogpost/`
- Consulta il `Codice Galattico` per le regole

### 2. **Sviluppa il Sistema**
- Usa `dish_mapping.json` per gli ID dei piatti
- Leggi `domande.csv` per capire i tipi di query
- Ottimizza per il punteggio Jaccard

### 3. **Sottometti in Tempo Reale**

⚠️ **IMPORTANTE**: L'URL del server può cambiare durante l'hackathon. Controlla sempre `current_tunnel_url.txt` per l'URL più recente.

**Opzione A - Script automatico**:
```bash
# Controlla l'URL attuale
URL=$(cat current_tunnel_url.txt)

# Sottometti con l'URL corrente
python submit_to_server.py \
  --team "Nome Team" \
  --server $URL \
  nome_team.csv
```

**Opzione B - Dashboard web**:
Visita l'URL contenuto in `current_tunnel_url.txt` nel browser

### 4. **Monitora Progressi**
- **Dashboard**: Classifica in tempo reale all'URL corrente
- **API**: `/api/leaderboard` per integrazioni  
- **Feedback**: Punteggi immediati dopo ogni submission

## 🔄 Gestione Cambio URL

### Per i Partecipanti

Quando l'URL cambia (raro ma possibile), il sistema:

1. **Crea automaticamente** `NUOVO_URL.txt` con istruzioni
2. **Aggiorna** `current_tunnel_url.txt` con l'URL nuovo
3. **I link nella dashboard** si aggiornano automaticamente

**Cosa fare quando cambia l'URL**:
```bash
# 1. Controlla l'URL nuovo
cat current_tunnel_url.txt

# 2. Usa il nuovo URL per le submission
python submit_to_server.py \
  --team "Nome Team" \
  --server $(cat current_tunnel_url.txt) \
  nome_team.csv
```

**La dashboard continua a funzionare normalmente** - tutti i link interni si aggiornano automaticamente!

## 📊 Criteri di Valutazione Completi

### 🎯 **Correttezza (Quantitativa)**
Basata su **Jaccard Similarity**:
- **Precisione**: Evita piatti sbagliati
- **Completezza**: Trova tutti i piatti corretti
- **Bilanciamento**: Ottimizza il rapporto intersezione/unione

### 🎨 **Originalità (Qualitativa)**
- **Approccio innovativo** al problema
- **Uso creativo** dei dati disponibili
- **Soluzione elegante** e robusta

### 💡 **Suggerimenti per Migliorare il Punteggio**

#### **Precisione > Quantità**
- Meglio 3 piatti corretti che 6 con errori
- La Jaccard penalizza i falsi positivi

#### **Gestione dei Filtri**
- Domande con "ma non contengono" sono cruciali
- Prestare attenzione ai dettagli nelle richieste

#### **Analisi Multi-fonte**
- Combina informazioni da menu, blog e codice galattico
- Verifica coerenza tra fonti diverse

## 🛠️ Strumenti di Supporto

### **Validazione Locale**
```bash
python validate_submission.py --submission nome_team.csv
```

### **Test del Sistema**
```bash
python create_test_submissions.py
python evaluate_submissions.py \
  --ground-truth ground_truth.csv \
  --submissions-dir test_submissions/ \
  --evaluation-type All
```

### **Monitoraggio in Tempo Reale**
- **Dashboard**: Classifica live
- **API**: Integrazione con sistemi esterni
- **Notifiche**: Aggiornamenti automatici URL

## 📚 Documentazione Completa

### 📖 **Guide Principali**
- **[README_submission_and_evaluation.md](README_submission_and_evaluation.md)** - Guida completa sistema
- **[README_dataset.md](README_dataset.md)** - Descrizione dataset
- **[guida_hackathon_5h.md](guida_hackathon_5h.md)** - Timeline hackathon

### 🔧 **Script di Supporto**
- `realtime_evaluation_server.py` - Server di valutazione
- `auto_tunnel_manager_localtunnel.py` - Gestione tunnel localtunnel
- `auto_tunnel_manager.py` - Gestione tunnel ngrok
- `submit_to_server.py` - Submission automatica
- `validate_submission.py` - Validazione formato

## 🏆 Buona Fortuna!

Il **Pizzaverse** vi aspetta! Che la forza della Jaccard Similarity sia con voi! 🍕✨

---

**Supporto**: Per problemi tecnici consulta la documentazione completa o testa il sistema con i file di esempio forniti.
