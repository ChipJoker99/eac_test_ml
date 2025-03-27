# Stress Testing API con Locust e Python

Questi script utilizzano **Locust** per eseguire test di carico e stress sull'API in locale. Include tre tipologie di test:

* **Stress Test**: Aumento graduale del numero di utneti fino a un carico elevato.
* **Spike Test**: Carico improvviso di molti utenti in un breve periodo.
* **Flood Test**: Simulazione di richieste continue senza pausa.

## Prerequisiti

1. **Python 3.x** installato (consigliato 3.8 o superiore).
2. **Locust** installato tramite pip:

```bash
pip install locust
```

3. **Assicurati che l'API sia in esecuzione** in locale su `http://0.0.0.0:3308` prima di avviare i test.
4. **File JSON con gli ID delle properietà e delle agenzie (`property_ids.json` e `agency_ids.json`).

## Avvio dei Test

### 1. Eseguire un test specifico
Per avviare un test, usa il seguente comando:
```bash
python3 testApi.py <test_type>
```
Dove `<test_type>` può essere
* `stress` → Esegue lo **Stress Test**
* `flood` → Esegue il **Flood Test**
* `spike` → Esegue lo **Spike Test**

Questo comando avvierà Locust con il test specificato.

### 2. Avviare Locust manualmente

Se vuoi avviare un test specifico senza usare testApi.py, puoi eseguire Locust direttamente:

```bash
locust -f stressTest.py  # Per lo Stress Test
locust -f floodTest.py   # Per il Flood Test
locust -f spikeTest.py   # Per lo Spike Test
```

### 3. Aprire l'interfaccia Locust
Una volta avviato Locust, apri il bropwser e vai su:

```url
http://localhost:8089
```

Da qui è possibile configurare il numero di utenti, la velocità di crescita e visualizzare i risultati in tempo reale.

### 4. Aprire l'interfaccia Locust

#### Modifica dei parametri di test

Puoi modificare i file `stressTest.py`, `floodTest.py` o `spikeTest.py` per personalizzare:

* Il numero di utenti simulati.
* Il tempo di attesa tra le richieste.
* Il tasso di crescita degli utenti.

Esempio di modifica nello **Stress Test**:

```python
stages = [
    {"duration": 30, "users": 100, "spawn_rate": 20},  # Aumenta a 100 utenti in 30s
    {"duration": 60, "users": 500, "spawn_rate": 100}  # Aumenta a 500 utenti in 1 min
]
```

Questo codice rappresenta un elenco di fasi per test di carico di un'API utilizzando uno strumento come Locust. Ogni fase è un dizionario con tre componenti chiave:

- **duration**: La lunghezza del tempo (in secondi) per cui la fase esegue.
- **users**: Il numero di utenti concorrenti da simulare durante la fase.
- **spawn_rate**: La velocità alla quale vengono aggiunti nuovi utenti al secondo, fino a quando non viene raggiunto il numero di utenti target.

Ad esempio, la prima fase esegue per 30 secondi, aumentando a 100 utenti a una velocità di 20 utenti al secondo.

## Analisi dei Risultati

Dopo aver eseguito i test, Locust mostrerà statistiche dettagliate su:

* **Numero di richieste per secondo**
* **Tempi di risposta medi e massimi**
* **Tasso di errore**
* **Percentuale di successo delle richieste**

Per salvare i risultati in un file CSV, puoi eseguire Locust con:

```bash
locust -f stressTest.py --csv=risultati_stress_test
```

Questo genererà file CSV con i dati raccolti.

## Interpretazione dei dati

Ecco alcune metriche chiave da analizzare nei risultati di Locust:

* **Response Time (Tempo di risposta)**: Indica quanto tempo impiega il server a rispondere a una richiesta.
    * 🟢 < 200ms → Ottimale
    * 🟡 200ms - 1s → Accettabile
    * 🔴 > 1s → Problema di performance

* **Requests per Second (RPS)**: Misura quante richieste il server può gestire al secondo. Un valore alto indica una buona scalabilità.

* **Failure Rate (Tasso di errore)**: Se supera il 2-5%, potrebbe indicare che il server è sovraccarico o ci sono errori nei test.

* **Percentile Response Time**:
    * **P50**: Il 50% delle richieste è più veloce di questo valore.
    * **P90**: Il 90% delle richieste è più veloce di questo valore.
    * **P99**: Il 99% delle richieste è più veloce di questo valore.

Questi percentili aiutano a identificare se ci sono colli di bottiglia nelle prestazioni.

## Tabella dei valori

|Utenti Simulati|RPS Atteso |Response Time Ottimale|Response Time Accettabile   |Problema di Performance|
|:--------------|:----------|:---------------------|:---------------------------|:----------------------|
| 100           | 50-100    | < 150ms              | 150ms - 500ms              | > 500ms               |
| 500           | 200-400   | < 200ms              | 200ms - 1s                 | > 1s                  | 
| 1000          | 500-700   | < 300ms              | 300ms - 1.5s               | > 1.5s                | 
| 1500          | 700-900   | < 400ms              | 400ms - 2s                 | > 2s                  | 
| 2000          | 900-1200  | < 500ms              | 500ms - 2.5s               | > 2.5s                |

Questi valori sono indicativi e dipendono dall'infrastruttura del server e dall'ottimizzazione dell'API.