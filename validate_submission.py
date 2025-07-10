#!/usr/bin/env python3
"""
Script di Validazione Submission - Per Partecipanti
Valida il formato della submission senza rivelare le risposte corrette
"""

import pandas as pd
import json
import argparse
from pathlib import Path
from typing import List, Dict, Tuple, Set


def load_dish_mapping(filepath: str) -> Dict[str, int]:
    """Carica il mapping piatti -> ID"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"❌ Errore nel caricamento di {filepath}: {e}")
        return {}


def validate_submission_format(filepath: str) -> Tuple[bool, List[str], Dict[int, List[int]]]:
    """
    Valida il formato della submission
    
    Returns:
        (is_valid, errors, parsed_data)
    """
    errors = []
    parsed_data = {}
    
    try:
        df = pd.read_csv(filepath)
    except Exception as e:
        errors.append(f"❌ Impossibile leggere il file CSV: {e}")
        return False, errors, {}
    
    # Verifica colonne
    expected_columns = ['row_id', 'result']
    if list(df.columns) != expected_columns:
        errors.append(f"❌ Colonne errate. Attese: {expected_columns}, Trovate: {list(df.columns)}")
        return False, errors, {}
    
    # Verifica numero righe
    if len(df) != 50:
        errors.append(f"❌ Numero righe errato. Attese: 50, Trovate: {len(df)}")
    
    # Verifica row_ids
    expected_row_ids = set(range(1, 51))
    actual_row_ids = set(df['row_id'].tolist())
    
    if actual_row_ids != expected_row_ids:
        missing = expected_row_ids - actual_row_ids
        extra = actual_row_ids - expected_row_ids
        if missing:
            errors.append(f"❌ row_id mancanti: {sorted(missing)}")
        if extra:
            errors.append(f"❌ row_id extra: {sorted(extra)}")
    
    # Verifica risultati
    for idx, row in df.iterrows():
        row_id = row['row_id']
        result = row['result']
        
        # Verifica campo non vuoto
        if pd.isna(result) or result == '':
            errors.append(f"❌ Domanda {row_id}: campo result vuoto")
            continue
        
        # Parsing IDs
        try:
            if isinstance(result, str):
                # Rimuovi virgolette se presenti
                result_clean = result.strip('"\'')
                dish_ids = [int(x.strip()) for x in result_clean.split(',')]
            else:
                dish_ids = [int(result)]
            
            parsed_data[row_id] = dish_ids
            
        except ValueError as e:
            errors.append(f"❌ Domanda {row_id}: formato result invalido '{result}' - {e}")
            continue
    
    is_valid = len(errors) == 0
    return is_valid, errors, parsed_data


def validate_dish_ids(parsed_data: Dict[int, List[int]], 
                     dish_mapping: Dict[str, int]) -> List[str]:
    """Valida che tutti gli ID esistano nel dish_mapping"""
    errors = []
    valid_ids = set(dish_mapping.values())
    
    for row_id, dish_ids in parsed_data.items():
        for dish_id in dish_ids:
            if dish_id not in valid_ids:
                errors.append(f"⚠️  Domanda {row_id}: ID {dish_id} non esiste in dish_mapping.json")
    
    return errors


def generate_validation_report(filepath: str, 
                             is_valid: bool, 
                             format_errors: List[str],
                             id_errors: List[str],
                             parsed_data: Dict[int, List[int]]) -> str:
    """Genera un report di validazione"""
    
    report = f"\n{'='*60}\n"
    report += f"🔍 VALIDAZIONE SUBMISSION: {Path(filepath).name}\n"
    report += f"{'='*60}\n\n"
    
    # Status generale
    if is_valid and not id_errors:
        report += "✅ SUBMISSION VALIDA! Pronta per la consegna.\n\n"
    elif is_valid and id_errors:
        report += "⚠️  SUBMISSION CON AVVISI (comunque valida)\n\n"
    else:
        report += "❌ SUBMISSION NON VALIDA - Correggere gli errori\n\n"
    
    # Statistiche
    report += f"📊 STATISTICHE:\n"
    report += f"   • Domande processate: {len(parsed_data)}/50\n"
    if parsed_data:
        total_dishes = sum(len(dishes) for dishes in parsed_data.values())
        avg_dishes = total_dishes / len(parsed_data)
        report += f"   • Piatti totali predetti: {total_dishes}\n"
        report += f"   • Media piatti per domanda: {avg_dishes:.1f}\n"
    
    # Errori di formato (critici)
    if format_errors:
        report += f"\n🚨 ERRORI DI FORMATO (DA CORREGGERE):\n"
        for error in format_errors:
            report += f"   {error}\n"
    
    # Errori ID (avvisi)
    if id_errors:
        report += f"\n⚠️  AVVISI ID PIATTI:\n"
        for error in id_errors[:10]:  # Mostra solo i primi 10
            report += f"   {error}\n"
        if len(id_errors) > 10:
            report += f"   ... e altri {len(id_errors) - 10} avvisi\n"
    
    # Esempi
    if parsed_data:
        report += f"\n📝 ESEMPI DELLE TUE RISPOSTE:\n"
        sample_questions = list(parsed_data.keys())[:5]
        for row_id in sample_questions:
            dishes = parsed_data[row_id]
            report += f"   Domanda {row_id}: {dishes} ({len(dishes)} piatti)\n"
    
    return report


def mock_evaluation(parsed_data: Dict[int, List[int]]) -> str:
    """
    Simulazione valutazione (senza ground truth)
    Mostra come funzionerà la valutazione reale
    """
    report = f"\n{'='*60}\n"
    report += "🎯 SIMULAZIONE VALUTAZIONE (SENZA GROUND TRUTH)\n"
    report += f"{'='*60}\n\n"
    
    report += "📊 COME FUNZIONERÀ LA VALUTAZIONE REALE:\n\n"
    
    # Simula alcuni scenari
    scenarios = [
        ("Risposta Perfetta", [1, 2, 3], [1, 2, 3], 1.0),
        ("Risposta Parziale", [1, 2, 3], [1, 2, 4], 0.5),
        ("Risposta Scarsa", [1, 2, 3], [4, 5, 6], 0.0),
    ]
    
    for name, correct, predicted, jaccard in scenarios:
        report += f"🔹 {name}:\n"
        report += f"   Risposta Corretta: {correct}\n"
        report += f"   Tua Risposta: {predicted}\n"
        report += f"   Jaccard Similarity: {jaccard:.2f} ({jaccard*100:.0f}%)\n\n"
    
    # Statistiche sulla submission
    if parsed_data:
        total_predictions = sum(len(dishes) for dishes in parsed_data.values())
        avg_predictions = total_predictions / len(parsed_data)
        
        report += f"📈 ANALISI DELLA TUA SUBMISSION:\n"
        report += f"   • Media piatti per domanda: {avg_predictions:.1f}\n"
        
        if avg_predictions < 2:
            report += "   💡 Suggerimento: Forse sei troppo conservativo? La maggior parte delle domande ha 2-3 risposte corrette.\n"
        elif avg_predictions > 5:
            report += "   ⚠️  Attenzione: Troppi piatti per domanda potrebbero penalizzare il tuo punteggio Jaccard.\n"
        else:
            report += "   ✅ Numero di piatti per domanda sembra ragionevole.\n"
    
    return report


def main():
    parser = argparse.ArgumentParser(description='Valida la tua submission per l\'hackathon Hackapizza')
    parser.add_argument('--submission', required=True,
                       help='Path al tuo file CSV di submission')
    parser.add_argument('--dish-mapping', 
                       default='Hackapizza Dataset/Misc/dish_mapping.json',
                       help='Path al file dish_mapping.json')
    parser.add_argument('--show-mock-eval', action='store_true',
                       help='Mostra simulazione della valutazione')
    
    args = parser.parse_args()
    
    print("🍕 VALIDATORE SUBMISSION HACKATHON HACKAPIZZA")
    print("=" * 50)
    
    # Carica dish mapping
    dish_mapping = load_dish_mapping(args.dish_mapping)
    if not dish_mapping:
        print("❌ Impossibile procedere senza dish_mapping.json")
        return
    
    print(f"✅ Caricato dish_mapping con {len(dish_mapping)} piatti")
    
    # Valida formato
    is_valid, format_errors, parsed_data = validate_submission_format(args.submission)
    
    # Valida IDs
    id_errors = []
    if parsed_data:
        id_errors = validate_dish_ids(parsed_data, dish_mapping)
    
    # Genera report
    report = generate_validation_report(args.submission, is_valid, format_errors, id_errors, parsed_data)
    print(report)
    
    # Simulazione valutazione
    if args.show_mock_eval and parsed_data:
        mock_report = mock_evaluation(parsed_data)
        print(mock_report)
    
    # Suggerimenti finali
    print("💡 SUGGERIMENTI:")
    if is_valid and not id_errors:
        print("   🎉 La tua submission è pronta! Puoi consegnarla all'organizzatore.")
    elif is_valid:
        print("   ⚠️  Submission valida ma con alcuni ID non riconosciuti.")
        print("   📝 Controlla dish_mapping.json per verificare gli ID corretti.")
    else:
        print("   🔧 Correggi gli errori di formato prima della consegna.")
    
    print("\n🔥 Per testare con simulazione valutazione:")
    print(f"   python {__file__} --submission {args.submission} --show-mock-eval")


if __name__ == "__main__":
    main() 