import requests
import json

# ─────────────────────────────────────────────
# CONFIGURAZIONE OLLAMA
# ─────────────────────────────────────────────

URL = "http://localhost:11434/api/chat"
MODELLO = "qwen2.5:1.5b-instruct"
NUM_RISPOSTE = 5

# ─────────────────────────────────────────────
# SYSTEM PROMPT
# ─────────────────────────────────────────────

SYSTEM_RISPOSTA = (
    "Sei un assistente preciso e sintetico. "
    "Rispondi SOLO basandoti sul testo fornito. "
    "Non inventare nulla. Rispondi in italiano."
)

SYSTEM_GIUDICE = (
    "Sei un giudice imparziale. "
    "Valuta la qualità della risposta rispetto al testo e alla domanda. "
    "Dai un punteggio intero da 1 a 10. Rispondi SOLO con il numero."
)

# ─────────────────────────────────────────────
# FUNZIONE: chiamata al modello OLLAMA
# ─────────────────────────────────────────────

def chiama_modello(system_prompt, messaggio_utente):
    payload = {
        "model": MODELLO,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": messaggio_utente}
        ],
        "stream": False
    }

    try:
        risposta = requests.post(URL, json=payload, timeout=60)
        risposta.raise_for_status()
        dati = risposta.json()
        return dati["message"]["content"].strip()

    except requests.exceptions.ConnectionError:
        print("\n❌ Errore: Ollama non è avviato.")
        print("   Avvia Ollama e assicurati che il modello sia installato.")
        return None

    except Exception as e:
        print(f"\n❌ Errore imprevisto: {e}")
        return None

# ─────────────────────────────────────────────
# GENERA RISPOSTA
# ─────────────────────────────────────────────

def genera_risposta(testo, domanda, risposte_precedenti=None):
    messaggio = f"TESTO:\n{testo}\n\nDOMANDA:\n{domanda}"

    if risposte_precedenti:
        messaggio += "\n\nRisposte precedenti:\n"
        for i, (r, p) in enumerate(risposte_precedenti, 1):
            anteprima = r[:150] + "..." if len(r) > 150 else r
            messaggio += f"- Risposta {i} ({p}/10): {anteprima}\n"

    return chiama_modello(SYSTEM_RISPOSTA, messaggio)

# ─────────────────────────────────────────────
# VALUTA RISPOSTA
# ─────────────────────────────────────────────

def valuta_risposta(testo, domanda, risposta):
    messaggio = (
        f"TESTO ORIGINALE:\n{testo}\n\n"
        f"DOMANDA:\n{domanda}\n\n"
        f"RISPOSTA:\n{risposta}\n\n"
        "Dai un punteggio da 1 a 10. SOLO il numero."
    )

    risultato = chiama_modello(SYSTEM_GIUDICE, messaggio)
    if risultato is None:
        return 0

    for parola in risultato.split():
        parola_pulita = parola.strip(".,!?:/")
        if parola_pulita.isdigit():
            return max(1, min(10, int(parola_pulita)))

    return 5

# ─────────────────────────────────────────────
# ELABORA DOMANDA
# ─────────────────────────────────────────────

def elabora_domanda(testo, domanda):
    print(f"\nGenerazione di {NUM_RISPOSTE} risposte...\n")

    risultati = []
    risposte_precedenti = []

    for i in range(1, NUM_RISPOSTE + 1):
        print(f"[{i}/{NUM_RISPOSTE}] Genero risposta...", end=" ", flush=True)
        risposta = genera_risposta(testo, domanda, risposte_precedenti if i > 1 else None)

        if risposta is None:
            print("ERRORE.")
            return

        print("Valuto...", end=" ", flush=True)
        punteggio = valuta_risposta(testo, domanda, risposta)
        print(f"{punteggio}/10")

        risultati.append((risposta, punteggio))
        risposte_precedenti.append((risposta, punteggio))

    print("\nTutte le risposte generate:")
    for i, (r, p) in enumerate(risultati, 1):
        print(f"\nRisposta {i} ({p}/10):\n{r}")

    migliore, punteggio = max(risultati, key=lambda x: x[1])
    print("\n────────────────────────────────────────────")
    print(f"🏆 MIGLIORE ({punteggio}/10):\n{migliore}")
    print("────────────────────────────────────────────")

# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────

def main():
    print("Sistema di generazione e valutazione risposte (Ollama)")

    while True:
        print("\nInserisci il testo (scrivi FINE per terminare):")
        righe = []
        while True:
            r = input()
            if r.strip().upper() == "FINE":
                break
            righe.append(r)

        testo = "\n".join(righe).strip()
        if not testo:
            print("Testo vuoto.")
            continue

        domanda = input("\nDomanda: ").strip()
        if not domanda:
            print("Domanda vuota.")
            continue

        elabora_domanda(testo, domanda)

        if input("\nPremi invio per continuare, 'exit' per uscire: ").lower() == "exit":
            break

if __name__ == "__main__":
    main()
