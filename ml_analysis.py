import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score
import matplotlib.pyplot as plt

# Carica i dati
df = pd.read_csv("ml_performance_data.csv")
# Crea una nuova colonna 'failure': 1 se status_code != 200, 0 altrimenti
df["failure"] = (df["status_code"] != 200).astype(int)

# Visualizza alcuni dati
print(df.head())

# Utilizza il tempo di risposta per prevedere la probabilità di fallimento
X = df[["response_time"]]
y = df["failure"]

# Dividi il dataset in train e test
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Crea e allena il modello
model = LinearRegression()
model.fit(X_train, y_train)

# Previsioni e valutazione
predictions = model.predict(X_test)
r2 = r2_score(y_test, predictions)

print("Coefficiente (trend):", model.coef_[0])
print("Intercept:", model.intercept_)
print("R^2:", r2)

# Visualizza la relazione con un grafico
plt.scatter(X_test, y_test, color='blue', label='Dati reali')
plt.plot(X_test, predictions, color='red', linewidth=2, label='Regressione')
plt.xlabel("Tempo di risposta (ms)")
plt.ylabel("Probabilità di fallimento")
plt.title("Analisi ML delle Prestazioni")
plt.legend()
plt.savefig("ml_performance_analysis.png")
plt.show()