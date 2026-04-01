"""
Progetto: Generazione multipla e selezione della miglior risposta
Gruppo 2: Lobianco, Madonia, Poma, Impalà
Classe: 4° superiore

Funzionamento:
- L'utente inserisce un testo e una domanda
- Il programma genera 5 risposte indipendenti usando il modello caricato in LM Studio
- Ogni risposta viene valutata con un punteggio da 1 a 10
- Viene mostrata la risposta migliore
- La chat continua finché l'utente non scrive "exit"

REQUISITI:
- LM Studio aperto con un modello caricato (es. Qwen2.5 1.5B Instruct)
- Server locale avviato in LM Studio (sezione Local Server → Start Server)
- libreria requests: pip install requests
"""

import requests

# ─────────────────────────────────────────────
# CONFIGURAZIONE
# ─────────────────────────────────────────────

# URL del server locale di LM Studio (default)
URL = "http://localhost:1234/v1/chat/completions"

# Nome del modello: LM Studio accetta qualsiasi stringa qui,
# usa quello che è caricato nel server indipendentemente dal nome
MODELLO = "local-model"

# Numero di risposte da generare per ogni domanda
NUM_RISPOSTE = 5

# ─────────────────────────────────────────────
# SYSTEM PROMPT per la generazione delle risposte
# ─────────────────────────────────────────────
SYSTEM_RISPOSTA = (
    "Sei un assistente preciso e sintetico. "
    "Il tuo compito è rispondere a domande basandoti SOLO sul testo fornito dall'utente. "
    "Non aggiungere informazioni esterne al testo. "
    "Rispondi in italiano, in modo chiaro e diretto."
)

# ─────────────────────────────────────────────
# SYSTEM PROMPT per il giudice (valutazione)
# ─────────────────────────────────────────────
SYSTEM_GIUDICE = (
    "Sei un giudice imparziale. "
    "Valuta la qualità di una risposta rispetto a una domanda e al testo originale. "
    "Assegna un punteggio intero da 1 a 10 dove: "
    "1 = risposta sbagliata o fuori tema, "
    "10 = risposta perfetta, corretta e basata sul testo. "
    "Rispondi SOLO con il numero del punteggio, nient'altro."
)


# ─────────────────────────────────────────────
# FUNZIONE: invia un messaggio al modello e ritorna la risposta
# ─────────────────────────────────────────────
def chiama_modello(system_prompt, messaggio_utente):
    """
    Manda una richiesta al server di LM Studio e ritorna il testo della risposta.
    Usa il formato compatibile con OpenAI (lo stesso usato da LM Studio).
    """

    # Costruiamo il "corpo" della richiesta HTTP
    payload = {
        "model": MODELLO,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user",   "content": messaggio_utente}
        ],
        "temperature": 0.7,   # Creatività: 0 = deterministico, 1 = molto creativo
        "max_tokens": 512     # Lunghezza massima della risposta
    }

    try:
        # Inviamo la richiesta POST al server di LM Studio
        risposta_http = requests.post(URL, json=payload, timeout=60)
        risposta_http.raise_for_status()  # Solleva un errore se lo status HTTP non è 200

        # Estraiamo il testo dalla risposta JSON
        dati = risposta_http.json()
        testo = dati["choices"][0]["message"]["content"].strip()
        return testo

    except requests.exceptions.ConnectionError:
        # LM Studio non è avviato o il server non è partito
        print("\n❌ Errore: non riesco a connettermi a LM Studio.")
        print("   Assicurati di aver:")
        print("   1. Aperto LM Studio")
        print("   2. Caricato un modello (es. Qwen2.5 1.5B Instruct)")
        print("   3. Avviato il server dalla sezione 'Local Server' → 'Start Server'")
        return None

    except KeyError:
        # La risposta JSON non ha il formato atteso
        print("\n❌ Errore: risposta inattesa da LM Studio.")
        return None

    except Exception as e:
        print(f"\n❌ Errore imprevisto: {e}")
        return None


# ─────────────────────────────────────────────
# FUNZIONE: genera una risposta alla domanda
# ─────────────────────────────────────────────
def genera_risposta(testo, domanda, risposte_precedenti=None):
    """
    Chiede al modello di rispondere alla domanda basandosi sul testo.

    ESTENSIONE FACOLTATIVA:
    Se ci sono risposte precedenti, le mostriamo al modello
    così può cercare di migliorarle nelle iterazioni successive.
    """

    # Messaggio base: testo + domanda
    messaggio = f"TESTO:\n{testo}\n\nDOMANDA:\n{domanda}"

    # Dalla seconda iterazione in poi, aggiungiamo le risposte precedenti
    if risposte_precedenti:
        messaggio += "\n\nATTENZIONE: queste sono le risposte generate finora con i loro punteggi."
        messaggio += " Cerca di fare meglio, sii più preciso e completo:\n"
        for i, (r, p) in enumerate(risposte_precedenti, 1):
            # Mostriamo solo i primi 150 caratteri per non appesantire troppo il prompt
            anteprima = r[:150] + "..." if len(r) > 150 else r
            messaggio += f"- Risposta {i} (punteggio {p}/10): {anteprima}\n"

    return chiama_modello(SYSTEM_RISPOSTA, messaggio)


# ─────────────────────────────────────────────
# FUNZIONE: valuta una risposta (LLM-as-a-Judge)
# ─────────────────────────────────────────────
def valuta_risposta(testo, domanda, risposta):
    """
    Usa il modello come "giudice" per dare un punteggio da 1 a 10 alla risposta.
    """

    messaggio = (
        f"TESTO ORIGINALE:\n{testo}\n\n"
        f"DOMANDA:\n{domanda}\n\n"
        f"RISPOSTA DA VALUTARE:\n{risposta}\n\n"
        "Dai un punteggio intero da 1 a 10. Rispondi SOLO con il numero."
    )

    risultato = chiama_modello(SYSTEM_GIUDICE, messaggio)

    if risultato is None:
        return 0

    # Cerchiamo un numero nella risposta del giudice
    # (a volte il modello scrive "Punteggio: 8" invece di solo "8")
    for parola in risultato.split():
        parola_pulita = parola.strip(".,!?:/")
        if parola_pulita.isdigit():
            punteggio = int(parola_pulita)
            return max(1, min(10, punteggio))  # Forziamo il range 1-10

    # Se non troviamo nessun numero, punteggio neutro
    print(f"   ⚠️  Il giudice ha risposto in modo strano: '{risultato}' → assegno 5")
    return 5


# ─────────────────────────────────────────────
# FUNZIONE: gestisce una sessione completa
# ─────────────────────────────────────────────
def elabora_domanda(testo, domanda):
    """
    Genera NUM_RISPOSTE risposte, le valuta tutte e mostra i risultati.
    """

    print(f"\n{'='*60}")
    print(f"❓ DOMANDA: {domanda}")
    print(f"{'='*60}")
    print(f"\n⏳ Genero {NUM_RISPOSTE} risposte e le valuto...\n")

    risultati = []            # Lista di tuple: (testo_risposta, punteggio)
    risposte_precedenti = []  # Per l'estensione facoltativa

    for i in range(1, NUM_RISPOSTE + 1):

        print(f"  [{i}/{NUM_RISPOSTE}] Genero risposta {i}...", end=" ", flush=True)

        # Generiamo la risposta
        # Dalla seconda iterazione passiamo le precedenti (estensione facoltativa)
        risposta = genera_risposta(
            testo,
            domanda,
            risposte_precedenti if i > 1 else None
        )

        if risposta is None:
            print("ERRORE - interrompo.")
            return

        print("✓  Valuto...", end=" ", flush=True)

        # Valutiamo la risposta con il giudice
        punteggio = valuta_risposta(testo, domanda, risposta)

        print(f"Punteggio: {punteggio}/10")

        # Salviamo il risultato
        risultati.append((risposta, punteggio))
        risposte_precedenti.append((risposta, punteggio))

    # ── Mostra tutte le risposte ──────────────────────────────
    print(f"\n{'─'*60}")
    print("📋 TUTTE LE RISPOSTE GENERATE:")
    print(f"{'─'*60}")

    for i, (risposta, punteggio) in enumerate(risultati, 1):
        print(f"\n🔹 Risposta {i}  [Punteggio: {punteggio}/10]")
        print(f"   {risposta}")

    # ── Trova e mostra la risposta migliore ───────────────────
    migliore_risposta, miglior_punteggio = max(risultati, key=lambda x: x[1])
    indice_migliore = risultati.index((migliore_risposta, miglior_punteggio)) + 1

    print(f"\n{'='*60}")
    print(f"🏆 RISPOSTA MIGLIORE  (n°{indice_migliore} - Punteggio: {miglior_punteggio}/10):")
    print(f"{'='*60}")
    print(f"\n{migliore_risposta}\n")

    # ── Analisi andamento punteggi (estensione facoltativa) ───
    punteggi = [p for _, p in risultati]
    print(f"📊 Andamento punteggi: {' → '.join(str(p) for p in punteggi)}")

    if punteggi[-1] > punteggi[0]:
        print("   📈 I punteggi sono migliorati grazie al feedback iterativo!")
    elif punteggi[-1] < punteggi[0]:
        print("   📉 I punteggi sono diminuiti nel tempo.")
    else:
        print("   ➡️  I punteggi sono rimasti stabili.")


# ─────────────────────────────────────────────
# AVVIO DEL PROGRAMMA - Loop principale
# ─────────────────────────────────────────────
def main():
    print("╔══════════════════════════════════════════════════════════╗")
    print("║     Sistema di Generazione e Valutazione Risposte        ║")
    print("║     Gruppo 2 - Lobianco, Madonia, Poma, Impalà           ║")
    print("╚══════════════════════════════════════════════════════════╝")
    print()
    print("Benvenuto! Il programma funziona così:")
    print("  1. Inserisci un testo di riferimento")
    print("  2. Inserisci una domanda sul testo")
    print("  3. Il sistema genera 5 risposte e sceglie la migliore")
    print()
    print("Scrivi 'exit' in qualsiasi momento per uscire.")

    # Loop principale: riparte finché l'utente non scrive exit
    while True:

        # ── Passo 1: inserimento del testo ────────────────────
        print(f"\n{'─'*60}")
        print("📄 Inserisci il TESTO di riferimento.")
        print("   Scrivi su una o più righe.")
        print("   Quando hai finito, scrivi FINE su una riga vuota.")
        print("   (oppure scrivi 'exit' per uscire)")
        print(f"{'─'*60}")

        righe = []
        while True:
            riga = input()
            if riga.strip().lower() == "exit":
                print("\nArrivederci! 👋")
                return
            if riga.strip().upper() == "FINE":
                break
            righe.append(riga)

        testo = "\n".join(righe).strip()

        if not testo:
            print("⚠️  Non hai inserito nessun testo. Riprova.")
            continue

        # ── Passo 2: inserimento della domanda ────────────────
        print("\n❓ Inserisci la DOMANDA sul testo (oppure 'exit' per uscire):")
        domanda = input("> ").strip()

        if domanda.lower() == "exit":
            print("\nArrivederci! 👋")
            return

        if not domanda:
            print("⚠️  Non hai inserito nessuna domanda. Riprova.")
            continue

        # ── Passo 3: elaborazione ─────────────────────────────
        elabora_domanda(testo, domanda)

        # ── Passo 4: continua o esci ──────────────────────────
        print("\nPremi INVIO per fare una nuova domanda, oppure scrivi 'exit' per uscire.")
        scelta = input("> ").strip().lower()
        if scelta == "exit":
            print("\nArrivederci! 👋")
            break

        print()


# Punto di ingresso del programma
if __name__ == "__main__":
    main()