# 🍕 Hackathon Hackapizza - Guida Completa Sistema di Valutazione

## 📖 Indice
1. [🎯 Panoramica Sistema](#-panoramica-sistema)
2. [🔧 Setup Organizzatore](#-setup-organizzatore)
3. [👥 Guida Partecipanti](#-guida-partecipanti)
4. [📊 Sistema di Valutazione](#-sistema-di-valutazione)
5. [🚀 Sistema Tunnel Intelligente](#-sistema-tunnel-intelligente)
6. [🛠️ Troubleshooting](#-troubleshooting)

---

## 🎯 Panoramica Sistema

### Architettura Completa
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Partecipanti  │───▶│  Auto Tunnel    │───▶│  Server Python  │
│   (Remoti)      │    │   Manager       │    │   (Flask)       │
└─────────────────┘    │   (Ngrok)       │    └─────────────────┘
                       └─────────────────┘           │
                                │                    │
                                ▼                    ▼
                       ┌─────────────────┐    ┌─────────────────┐
                       │  URL Dinamico   │    │  Ground Truth   │
                       │ Auto-Recovery   │    │   (Sicuro)      │
                       │  Smart Links    │    └─────────────────┘
                       └─────────────────┘
```

### 🔄 Modalità di Valutazione

#### 📊 **Public Mode** (Durante l'hackathon)
- **Scopo**: Feedback immediato ai team
- **Domande**: Solo le 25 domande marcate come "Public"
- **Vantaggio**: Permette miglioramenti iterativi
- **Uso**: Modalità primaria durante l'hackathon

#### 🔒 **Private Mode** (Valutazione finale)
- **Scopo**: Classifica finale non influenzabile
- **Domande**: Solo le 25 domande marcate come "Private"
- **Vantaggio**: Previene overfitting
- **Uso**: Risultato finale dell'hackathon

#### 🌐 **All Mode** (Analisi completa)
- **Scopo**: Analisi post-hackathon
- **Domande**: Tutte le 50 domande
- **Calcolo**: Media matematica dei punteggi Public e Private
- **Uso**: Report completi e analisi dettagliate

---

## 🔧 Setup Organizzatore

### 🚀 **Sistema Auto-Tunnel Manager (RACCOMANDATO)**

#### **Vantaggi del Sistema Intelligente**
- ✅ **Riavvio automatico** quando il tunnel si disconnette
- ✅ **Switch URL automatico** senza interruzioni di servizio
- ✅ **Notifiche automatiche** dei cambi URL ai partecipanti
- ✅ **Link interni dinamici** sempre aggiornati nella dashboard
- ✅ **Recovery completo** di server e tunnel in caso di errori
- ✅ **Monitoring continuo** ogni 10 secondi

#### **Prerequisiti**
```bash
# Controlla che ngrok sia installato
ngrok version

# Se non installato:
# macOS: brew install ngrok
# Linux: snap install ngrok
# Windows: Download da https://ngrok.com/download
```

#### **Avvio Sistema Completo**

**Durante l'hackathon (Public Mode)**:
```bash
python auto_tunnel_manager.py \
  --port 5000 \
  --evaluation-type Public \
  --check-interval 10
```

**Output di avvio**:
```
🚀 Avvio Auto Tunnel Manager...
🍕 Avvio server di valutazione...
✅ Server di valutazione avviato
🚀 Avvio tunnel ngrok...
✅ Tunnel attivo: https://esempio-hackathon.ngrok-free.app
✅ Servizi avviati. Inizio monitoring...
```

#### **Cambio Modalità Durante l'Evento**

Per cambiare modalità **senza perdere dati**:

1. **Ferma il sistema corrente**: `CTRL+C`
2. **Riavvia con nuova modalità**:

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

**I dati delle submission vengono preservati** tra i cambi di modalità.

### 📋 **Parametri di Configurazione**

| Parametro | Descrizione | Valori | Default |
|-----------|-------------|---------|---------|
| `--port` | Porta server Flask | 5000-9999 | 5000 |
| `--evaluation-type` | Modalità evaluation | Public/Private/All | Public |
| `--check-interval` | Intervallo monitoring (s) | 5-60 | 10 |

### 📁 **File di Stato Generati**

Il sistema crea automaticamente questi file per il monitoraggio:

| File | Contenuto | Uso |
|------|-----------|-----|
| `current_tunnel_url.txt` | URL attuale del tunnel | Partecipanti |
| `NUOVO_URL.txt` | Istruzioni cambio URL | Notifiche |
| `tunnel_status.json` | Status completo sistema | Monitoring |
| `tunnel_history.json` | Cronologia URL | Debug |
| `url_change_notification.json` | Dettagli tecnici cambi | Integrations |

---

## 👥 Guida Partecipanti

### 📝 **Formato Submission**

#### **Struttura CSV Richiesta**
```csv
row_id,result
1,"101,102,103"
2,"104"
3,"105,106"
4,"107,108"
5,"109"
```

#### **Specifiche Tecniche**
- **Righe**: Esattamente 50 (domande 1-50)
- **Colonne**: `row_id,result`
- **Encoding**: UTF-8
- **Separatore**: Virgola
- **Virgolette**: Sempre attorno al campo `result`

#### **Regole di Validazione**
✅ **OBBLIGATORIO**:
- Nessun campo `result` vuoto
- Solo ID numerici (usa `dish_mapping.json`)
- Formato: `"101,102,103"` (virgolette incluse)

❌ **ERRORI COMUNI**:
```csv
# SBAGLIATO - senza virgolette
1,101,102,103

# SBAGLIATO - campo vuoto
2,

# SBAGLIATO - nomi invece di ID
3,"Pizza Margherita,Pasta Carbonara"

# CORRETTO
1,"101,102,103"
2,"104"
3,"105,106"
```

### 🚀 **Modalità di Submission**

#### **Opzione A: Script Automatico (RACCOMANDATO)**

**Con URL dinamico** (gestisce automaticamente i cambi):
```bash
# Ottieni URL corrente e sottometti
URL=$(cat current_tunnel_url.txt)
python submit_to_server.py \
  --team "Nome Team" \
  --server $URL \
  nome_team.csv
```

**Con URL fisso** (richiede aggiornamento manuale):
```bash
python submit_to_server.py \
  --team "Nome Team" \
  --server https://esempio.ngrok-free.app \
  nome_team.csv
```

**Output di successo**:
```
🎉 SUBMISSION COMPLETATA!
==================================================
👥 Team: Nome Team
📊 Punteggio: 65.43%
🏆 Posizione: 2/5
📈 Submissions totali: 3
⏰ Timestamp: 14:32:15
==================================================
✅ Risposte perfette: 18
❌ Risposte sbagliate: 5
📝 Domande valutate: 25
📈 MIGLIORAMENTO rispetto alla submission precedente!

💡 SUGGERIMENTI:
   📊 Dashboard: https://esempio.ngrok-free.app
   🔍 Statistiche team: https://esempio.ngrok-free.app/team/Nome Team
   📈 API Leaderboard: https://esempio.ngrok-free.app/api/leaderboard
```

#### **Opzione B: Dashboard Web**
1. Visita l'URL in `current_tunnel_url.txt`
2. Usa l'interfaccia web per upload CSV
3. Monitora la leaderboard in tempo reale

#### **Opzione C: API diretta**
```bash
# Per sviluppatori esperti
curl -X POST $(cat current_tunnel_url.txt)/submit \
  -H "Content-Type: application/json" \
  -d @submission.json
```

### 🔄 **Gestione Cambio URL**

#### **Scenario: L'URL cambia durante l'hackathon**

**Il sistema notifica automaticamente**:
1. Crea `NUOVO_URL.txt` con istruzioni
2. Aggiorna `current_tunnel_url.txt`
3. I link nella dashboard si aggiornano automaticamente

**Cosa fare come partecipante**:
```bash
# 1. Controlla se c'è un nuovo URL
cat current_tunnel_url.txt

# 2. Se è cambiato, verifica le notifiche
cat NUOVO_URL.txt

# 3. Usa il nuovo URL per le submission
python submit_to_server.py \
  --team "Nome Team" \
  --server $(cat current_tunnel_url.txt) \
  nome_team.csv
```

**La dashboard continua a funzionare** - tutti i link interni si aggiornano automaticamente!

---

## 📊 Sistema di Valutazione

### 🔢 **Metrica: Jaccard Similarity**

Per ogni domanda, il punteggio viene calcolato come:

```
Jaccard = |Risposta ∩ Ground Truth| / |Risposta ∪ Ground Truth|
```

#### **Esempio Dettagliato**

**Domanda 1**: "Piatti con pollo ma senza aglio"

| Aspetto | Valore |
|---------|--------|
| **Ground Truth** | `[101, 205, 308, 412]` |
| **Tua Risposta** | `[101, 205, 999]` |
| **Intersezione** | `[101, 205]` = 2 elementi |
| **Unione** | `[101, 205, 308, 412, 999]` = 5 elementi |
| **Jaccard Score** | `2/5 = 0.40` (40%) |

### 📈 **Calcolo Punteggio Finale**

#### **Per ogni modalità**:
```
Punteggio_Modalità = (Σ Jaccard_i) / N_domande
```

#### **Esempi Pratici**:

**Public Mode** (25 domande):
- Domande 1-25: Jaccard scores vari
- Punteggio finale: `(0.8 + 0.6 + 0.9 + ...) / 25 = 0.732` (73.2%)

**Private Mode** (25 domande):  
- Domande 26-50: Jaccard scores vari
- Punteggio finale: `(0.7 + 0.5 + 0.8 + ...) / 25 = 0.668` (66.8%)

**All Mode** (50 domande):
- Tutte le domande: Media aritmetica
- Punteggio finale: `(73.2% + 66.8%) / 2 = 70.0%`

---

## 🚀 Sistema Tunnel Intelligente

### 🔧 **Auto-Recovery System**

Il sistema monitora continuamente:

#### **Monitoring Tunnel**
```bash
# Ogni 10 secondi controlla:
1. Tunnel ngrok attivo?
2. Server Flask risponde?
3. URL accessibile dall'esterno?
```

#### **Auto-Restart Logic**
```bash
# Se trova problemi:
1. 🚨 Rileva disconnessione
2. 🔄 Termina processi zombie
3. 🚀 Riavvia tunnel ngrok
4. 📡 Ottiene nuovo URL
5. 📢 Notifica i partecipanti
6. ✅ Resume monitoring
```

#### **Smart URL Management**
```bash
# Il sistema gestisce automaticamente:
- current_tunnel_url.txt    # URL sempre aggiornato
- NUOVO_URL.txt            # Istruzioni cambio
- tunnel_history.json      # Cronologia completa
- url_change_notification.json  # Notifiche strutturate
```

### 📱 **Dashboard Links Dinamici**

**Problema risolto**: I link interni della dashboard si aggiornano automaticamente.

**Prima** (problematico):
```html
<!-- Link fissi che non funzionano dopo cambio URL -->
<a href="http://localhost:5000/api/leaderboard">API</a>
```

**Ora** (dinamico):
```html
<!-- Link che leggono automaticamente l'URL corrente -->
<a href="https://nuovo-url.ngrok-free.app/api/leaderboard">API</a>
```

### 🛡️ **Robustezza del Sistema**

#### **Scenari Gestiti Automaticamente**
- ✅ Disconnessione ngrok (limite 2h)
- ✅ Crash del server Flask
- ✅ Perdita connessione internet
- ✅ Cambio IP locale
- ✅ Riavvio del computer organizzatore

#### **Zero Configuration per Partecipanti**
- ✅ URL sempre disponibile in `current_tunnel_url.txt`
- ✅ Dashboard funziona sempre
- ✅ API sempre accessibile
- ✅ Notifiche automatiche dei cambi

---

## 🛠️ Troubleshooting

### 🔍 **Problemi Comuni**

#### **Server Non Si Avvia**
```bash
# Controlla se porta è occupata
lsof -i :5000

# Usa porta diversa
python auto_tunnel_manager_localtunnel.py \
  --port 5001 \
  --evaluation-type Public \
  --subdomain esempio-hackathon
```

#### **Localtunnel Non Funziona**
```bash
# Verifica Node.js
node --version
npm --version

# Reinstalla localtunnel
npm install -g localtunnel

# Prova manualmente
npx localtunnel --port 5000 --subdomain esempio-hackathon
```

#### **Submissions Respinte**
```bash
# Errore formato CSV
python validate_submission.py --submission file.csv

# Errore ID piatti
grep -v "^[0-9,\"]*$" file.csv
```

### 📋 **Checklist Pre-Hackathon**

#### **Per Organizzatori**
- [ ] ✅ Node.js installato
- [ ] ✅ Ground truth validato
- [ ] ✅ Sistema testato con file di esempio
- [ ] ✅ URL comunicato ai partecipanti
- [ ] ✅ Modalità impostata su "Public"

#### **Per Partecipanti**
- [ ] ✅ CSV validato localmente
- [ ] ✅ Formato corretto (50 righe)
- [ ] ✅ ID numerici verificati
- [ ] ✅ URL server testato
- [ ] ✅ Script submission funzionante

### 🚨 **Emergenze Durante l'Hackathon**

#### **Tunnel Cade**
```bash
# Il sistema riavvia automaticamente
# Controlla i log per conferma
tail -f tunnel_manager.log
```

#### **Cambio URL Necessario**
```bash
# Ferma sistema attuale
CTRL+C

# Riavvia con nuovo subdomain
python auto_tunnel_manager_localtunnel.py \
  --port 5000 \
  --evaluation-type Public \
  --subdomain esempio-hackathon-backup
```

#### **Passaggio a Ngrok**
```bash
# Se localtunnel ha problemi
python auto_tunnel_manager.py \
  --port 5000 \
  --evaluation-type Public \
  --check-interval 5
```

---

## 📈 **Monitoraggio e Analytics**

### 📊 **Dashboard Real-time**
- **URL**: `https://esempio-hackathon.loca.lt`
- **Classifica**: Aggiornamento automatico
- **Statistiche**: Submissions per team
- **Timeline**: Ultimi aggiornamenti

### 🔍 **API Endpoints**
```bash
# Leaderboard JSON
curl https://esempio-hackathon.loca.lt/api/leaderboard

# Statistiche team
curl https://esempio-hackathon.loca.lt/api/team/Nome%20Team

# Stato server
curl https://esempio-hackathon.loca.lt/api/status
```

### 📋 **Report Finali**
Al termine dell'hackathon, il sistema genera:
- **Classifica finale** (Private mode)
- **Report dettagliati** per ogni team
- **Analisi domande** più difficili
- **Statistiche complete** (All mode)

---

## 🎯 **Best Practices**

### 🚀 **Per Organizzatori**
1. **Testa sempre** il sistema prima dell'hackathon
2. **Comunica URL** con anticipo ai partecipanti
3. **Monitora log** durante l'evento
4. **Prepara backup** (ngrok se localtunnel ha problemi)
5. **Documenta** eventuali problemi per eventi futuri

### 👥 **Per Partecipanti**
1. **Valida sempre** CSV prima di sottomettere
2. **Testa connessione** all'URL fornito
3. **Sottometti frequentemente** durante l'hackathon
4. **Monitora classifica** per feedback
5. **Ottimizza per Jaccard** non solo per accuratezza

### 🔧 **Per Sviluppatori**
1. **Usa script automatici** per submission
2. **Integra validazione** nel workflow
3. **Monitora API** per automazione
4. **Testa edge cases** nelle risposte
5. **Ottimizza** per precision e recall

---

## 🎉 Pronto per l'Hackathon!

Il sistema è completamente configurato e testato. Con **localtunnel** come soluzione principale e **ngrok** come backup, avete un sistema robusto e affidabile per gestire l'hackathon.

**URL finale**: `https://esempio-hackathon.loca.lt`

Che inizino le danze! 🍕🚀 