# Progetto-AI-Python-Prompt-Engineering  
Realizzare un sistema che generi più risposte a una domanda e selezioni automaticamente quella ritenuta migliore.  
Il programma deve:  
- Generare più risposte alla domanda tramite chiamate successive a un modello linguistico
- Ripetere il processo per 5 iterazioni, generando quindi 5 risposte indipendenti
- Valutare ogni risposta assegnando un punteggio di correttezza tramite un sistema automatico di valutazione basato su IA
- Confrontare i punteggi ottenuti
- Selezionare la risposta con il punteggio più alto  

## Vincoli:  
- Ogni iterazione del processo di generazione deve essere indipendente dalle altre
- Il punteggio deve essere calcolato automaticamente
- La risposta deve basarsi esclusivamente sul testo fornito

## Output:  
Il programma deve mostrare a terminale:
- la domanda inserita
- l'elenco delle 5 risposte generate
Per ogni rispsota devono esser mostrati:
- il testo della rispsota
- il punteggio assegnato
Infine deve essere mostrata:
- la risposta con il punteggio più alto

**Estensione facoltativa**  
Modificare il prompt a ogni iterazione utilizzando informazioni sulle risposte generate nelle iterazioni precedenti.  
Analizzare e cambiare il punteggio delle risposte in tempo reale.
