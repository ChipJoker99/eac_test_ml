import sys
import os

"""
python3 testApi.py stress      # Esegue lo Stress Test
python3 testApi.py flood       # Esegue il Flood Test
python3 testApi.py spike       # Esegue il Spike Test
"""

def run_locust_test(test_type):
    """
    Avvia il test Locust specificato in base all'opzione scelta.
    """
    test_files = {
        "stress": "stressTest.py",
        "flood": "floodTest.py",
        "spike": "spikeTest.py"
    }

    if test_type in test_files:
        os.system(f"locust -f {test_files[test_type]}")
    else:
        print("Errore: Opzione non valida. Usa 'stress', 'flood' o 'spike'.")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python3 testApi.py <stress|flood|spike>")
        sys.exit(1)

    run_locust_test(sys.argv[1])
