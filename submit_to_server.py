#!/usr/bin/env python3
"""
Script per Sottomettere Predictions al Server di Valutazione
Converte CSV in JSON e invia al server per valutazione in tempo reale
"""

import pandas as pd
import requests
import json
import argparse
import sys
from pathlib import Path
import time


def convert_csv_to_json(csv_path: str, team_name: str) -> dict:
    """Converte CSV submission in formato JSON per il server"""
    try:
        df = pd.read_csv(csv_path)
        
        if 'row_id' not in df.columns or 'result' not in df.columns:
            raise ValueError("CSV deve avere colonne 'row_id' e 'result'")
        
        predictions = {}
        
        for _, row in df.iterrows():
            row_id = str(int(row['row_id']))
            result = row['result']
            
            # Gestisce result vuoto
            if pd.isna(result) or result == '':
                predictions[row_id] = []
            else:
                # Converte stringa CSV in lista
                if isinstance(result, str):
                    dish_ids = [int(x.strip()) for x in result.split(',')]
                else:
                    dish_ids = [int(result)]
                
                predictions[row_id] = dish_ids
        
        return {
            "team_name": team_name,
            "predictions": predictions
        }
        
    except Exception as e:
        print(f"❌ Errore nella conversione CSV: {e}")
        sys.exit(1)


def submit_predictions(server_url: str, payload: dict) -> dict:
    """Sottomette predictions al server"""
    try:
        # Aggiunge /submit se non presente
        if not server_url.endswith('/submit'):
            server_url = server_url.rstrip('/') + '/submit'
        
        headers = {'Content-Type': 'application/json'}
        
        print(f"📤 Sottomettendo a: {server_url}")
        print(f"👥 Team: {payload['team_name']}")
        print(f"📊 Domande: {len(payload['predictions'])}")
        
        response = requests.post(
            server_url,
            json=payload,
            headers=headers,
            timeout=30
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"❌ Errore HTTP {response.status_code}: {response.text}")
            return None
            
    except requests.RequestException as e:
        print(f"❌ Errore di connessione: {e}")
        return None
    except Exception as e:
        print(f"❌ Errore nella submission: {e}")
        return None


def display_results(result: dict):
    """Visualizza i risultati della submission"""
    if not result or not result.get('success'):
        print("❌ Submission fallita")
        return
    
    print("\n🎉 SUBMISSION COMPLETATA!")
    print("=" * 50)
    print(f"👥 Team: {result['team_name']}")
    print(f"📊 Punteggio: {result['score']:.2f}%")
    print(f"🏆 Posizione: {result['position']}/{result['total_teams']}")
    print(f"📈 Submissions totali: {result['submissions_count']}")
    print(f"⏰ Timestamp: {result['timestamp']}")
    print("=" * 50)
    
    # Statistiche dettagliate
    print(f"✅ Risposte perfette: {result['perfect_answers']}")
    print(f"❌ Risposte sbagliate: {result['zero_answers']}")
    print(f"📝 Domande valutate: {result['questions_evaluated']}")
    
    if result['improvement']:
        print("📈 MIGLIORAMENTO rispetto alla submission precedente!")
    
    print(f"\n💡 Visita la dashboard per la classifica completa!")


def main():
    parser = argparse.ArgumentParser(
        description='Sottometti predictions al server di valutazione',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Esempi di utilizzo:
  python submit_to_server.py predictions.csv --team "Team Alpha" --server http://localhost:5000
  python submit_to_server.py my_results.csv --team "DataWizards" --server http://192.168.1.100:5000
  python submit_to_server.py results.csv --team "Team Beta"  # usa server di default
        '''
    )
    
    parser.add_argument('csv_file', help='File CSV con le predictions')
    parser.add_argument('--team', required=True, help='Nome del team')
    parser.add_argument('--server', default='http://localhost:5000', 
                       help='URL del server (default: http://localhost:5000)')
    parser.add_argument('--no-validate', action='store_true',
                       help='Salta la validazione locale del CSV')
    parser.add_argument('--retry', type=int, default=3,
                       help='Numero di tentativi in caso di errore (default: 3)')
    parser.add_argument('--delay', type=int, default=2,
                       help='Secondi di attesa tra tentativi (default: 2)')
    
    args = parser.parse_args()
    
    # Verifica esistenza file
    csv_path = Path(args.csv_file)
    if not csv_path.exists():
        print(f"❌ File non trovato: {csv_path}")
        sys.exit(1)
    
    # Validazione opzionale
    if not args.no_validate:
        print("🔍 Validazione locale del CSV...")
        
        try:
            df = pd.read_csv(csv_path)
            
            if len(df) != 50:
                print(f"⚠️  Attenzione: trovate {len(df)} righe invece di 50")
            
            if 'row_id' not in df.columns or 'result' not in df.columns:
                print("❌ CSV deve avere colonne 'row_id' e 'result'")
                sys.exit(1)
            
            print("✅ CSV validato localmente")
            
        except Exception as e:
            print(f"❌ Errore nella validazione: {e}")
            sys.exit(1)
    
    # Converte CSV in JSON
    print("🔄 Convertendo CSV in formato JSON...")
    payload = convert_csv_to_json(str(csv_path), args.team)
    
    # Sottomette con retry
    result = None
    for attempt in range(args.retry):
        if attempt > 0:
            print(f"🔄 Tentativo {attempt + 1}/{args.retry}...")
            time.sleep(args.delay)
        
        result = submit_predictions(args.server, payload)
        
        if result:
            break
        
        if attempt < args.retry - 1:
            print(f"⏳ Attendo {args.delay} secondi prima del prossimo tentativo...")
    
    if result:
        display_results(result)
        
        # Suggerimenti
        print(f"\n💡 SUGGERIMENTI:")
        print(f"   📊 Dashboard: {args.server}")
        print(f"   🔍 Statistiche team: {args.server}/team/{args.team}")
        print(f"   📈 API Leaderboard: {args.server}/api/leaderboard")
        
    else:
        print("❌ Submission fallita dopo tutti i tentativi")
        sys.exit(1)


if __name__ == "__main__":
    main() 