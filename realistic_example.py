#!/usr/bin/env python3
"""
Esempio realistico di come funziona la Jaccard Similarity
"""

def jaccard_similarity(set1, set2):
    """Calcola Jaccard Similarity tra due set"""
    s1 = set(set1)
    s2 = set(set2)
    
    if len(s1) == 0 and len(s2) == 0:
        return 1.0
    
    intersection = len(s1.intersection(s2))
    union = len(s1.union(s2))
    
    return intersection / union if union > 0 else 0.0

# Esempio realistico: "Quali piatti contengono Erba Pipa?"
print("🍕 ESEMPIO REALISTICO: Quali piatti contengono Erba Pipa?")
print("=" * 60)

# Risposta corretta (supponiamo che ci siano 4 piatti con Erba Pipa)
ground_truth = [45, 78, 156, 203]
print(f"📋 Risposta Corretta: {ground_truth}")

# Team A: Risposta molto buona (3 su 4 corretti + 1 sbagliato)
team_a = [45, 78, 156, 99]  # 3 corretti, 1 sbagliato
jaccard_a = jaccard_similarity(team_a, ground_truth)
print(f"🥇 Team A: {team_a} → Jaccard = {jaccard_a:.3f} ({jaccard_a*100:.1f}%)")

# Team B: Risposta media (2 su 4 corretti + 2 sbagliati)
team_b = [45, 203, 12, 67]  # 2 corretti, 2 sbagliati
jaccard_b = jaccard_similarity(team_b, ground_truth)
print(f"🥈 Team B: {team_b} → Jaccard = {jaccard_b:.3f} ({jaccard_b*100:.1f}%)")

# Team C: Risposta scarsa (1 su 4 corretti + 3 sbagliati)
team_c = [78, 11, 22, 33]  # 1 corretto, 3 sbagliati
jaccard_c = jaccard_similarity(team_c, ground_truth)
print(f"🥉 Team C: {team_c} → Jaccard = {jaccard_c:.3f} ({jaccard_c*100:.1f}%)")

# Team D: Risposta perfetta
team_d = [45, 78, 156, 203]  # Tutti corretti
jaccard_d = jaccard_similarity(team_d, ground_truth)
print(f"🏆 Team D: {team_d} → Jaccard = {jaccard_d:.3f} ({jaccard_d*100:.1f}%)")

print("\n📊 ANALISI DETTAGLIATA:")
print("-" * 40)

def analyze_response(team_name, prediction, ground_truth):
    s1 = set(prediction)
    s2 = set(ground_truth)
    
    intersection = s1.intersection(s2)
    only_pred = s1 - s2
    only_gt = s2 - s1
    
    print(f"\n{team_name}:")
    print(f"  ✅ Piatti corretti: {list(intersection)} ({len(intersection)} piatti)")
    print(f"  ❌ Piatti sbagliati: {list(only_pred)} ({len(only_pred)} piatti)")
    print(f"  ⚠️  Piatti mancanti: {list(only_gt)} ({len(only_gt)} piatti)")
    print(f"  🎯 Jaccard: {len(intersection)} / {len(s1.union(s2))} = {jaccard_similarity(prediction, ground_truth):.3f}")

analyze_response("Team A", team_a, ground_truth)
analyze_response("Team B", team_b, ground_truth)
analyze_response("Team C", team_c, ground_truth)
analyze_response("Team D", team_d, ground_truth) 