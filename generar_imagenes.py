import json
import os
from urllib.request import urlopen
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

sns.set_theme(style="whitegrid")
os.makedirs("images", exist_ok=True)

# Carga de datos
DATA_URL = "https://raw.githubusercontent.com/ingridcristh/challenge2-data-science-LATAM/main/TelecomX_Data.json"
with urlopen(DATA_URL) as response:
    datos = json.load(response)

df = pd.json_normalize(datos, sep="_")

# Transformación
df_limpio = df.copy()
columnas_texto = df_limpio.select_dtypes(include=["object", "string"]).columns
df_limpio[columnas_texto] = df_limpio[columnas_texto].apply(lambda s: s.str.strip())
df_limpio[columnas_texto] = df_limpio[columnas_texto].replace({"": pd.NA})
df_limpio["account_Charges_Total"] = pd.to_numeric(df_limpio["account_Charges_Total"], errors="coerce")
df_limpio = df_limpio.dropna(subset=["Churn"]).copy()
df_limpio.loc[
    df_limpio["account_Charges_Total"].isna() & (df_limpio["customer_tenure"] == 0),
    "account_Charges_Total",
] = 0
df_limpio["Cuentas_Diarias"] = (df_limpio["account_Charges_Monthly"] / 30).round(2)
mapeo_binario = {"Yes": 1, "No": 0}
for col in ["Churn", "customer_Partner", "customer_Dependents", "account_PaperlessBilling"]:
    df_limpio[f"{col}_binario"] = df_limpio[col].map(mapeo_binario)

palette = ["#1f77b4", "#d62728"]

# --- Gráfica 1: Distribución de evasión ---
churn_distribucion = df_limpio["Churn"].value_counts()
fig, axes = plt.subplots(1, 2, figsize=(12, 4))
sns.countplot(data=df_limpio, x="Churn", hue="Churn", palette=palette, ax=axes[0], legend=False)
axes[0].set_title("Cantidad de clientes por churn")
axes[0].set_xlabel("Churn")
axes[0].set_ylabel("Clientes")
axes[1].pie(churn_distribucion.values, labels=churn_distribucion.index, autopct="%1.1f%%", colors=palette)
axes[1].set_title("Proporción de churn")
plt.tight_layout()
plt.savefig("images/01_distribucion_churn.png", dpi=120)
plt.close()
print("OK: 01_distribucion_churn.png")

# --- Gráfica 2: Evasión por variables categóricas ---
variables_categoricas = [
    "customer_gender",
    "account_Contract",
    "account_PaymentMethod",
    "internet_InternetService",
]
fig, axes = plt.subplots(2, 2, figsize=(14, 10))
axes = axes.flatten()
for eje, columna in zip(axes, variables_categoricas):
    tabla = pd.crosstab(df_limpio[columna], df_limpio["Churn"])
    tabla.plot(kind="bar", stacked=True, ax=eje, color=palette)
    eje.set_title(f"Churn por {columna}")
    eje.set_xlabel(columna)
    eje.set_ylabel("Clientes")
    eje.tick_params(axis="x", rotation=20)
plt.tight_layout()
plt.savefig("images/02_churn_categoricas.png", dpi=120)
plt.close()
print("OK: 02_churn_categoricas.png")

# --- Gráfica 3: Distribución de variables numéricas por churn ---
variables_numericas = [
    "customer_tenure",
    "account_Charges_Monthly",
    "account_Charges_Total",
    "Cuentas_Diarias",
]
fig, axes = plt.subplots(2, 2, figsize=(14, 10))
axes = axes.flatten()
for eje, columna in zip(axes, variables_numericas):
    sns.histplot(data=df_limpio, x=columna, hue="Churn", kde=True, stat="density", common_norm=False, ax=eje)
    eje.set_title(f"Distribución de {columna} por churn")
plt.tight_layout()
plt.savefig("images/03_distribucion_numericas.png", dpi=120)
plt.close()
print("OK: 03_distribucion_numericas.png")

# --- Gráfica 4: Heatmap de correlación ---
columnas_servicios = [
    "phone_PhoneService",
    "internet_OnlineSecurity",
    "internet_OnlineBackup",
    "internet_DeviceProtection",
    "internet_TechSupport",
    "internet_StreamingTV",
    "internet_StreamingMovies",
]
df_limpio["Total_Servicios"] = df_limpio[columnas_servicios].isin(["Yes"]).sum(axis=1)
correlacion_df = df_limpio[[
    "customer_tenure",
    "account_Charges_Monthly",
    "account_Charges_Total",
    "Cuentas_Diarias",
    "Total_Servicios",
    "Churn_binario",
]].corr()
plt.figure(figsize=(8, 6))
sns.heatmap(correlacion_df, annot=True, cmap="Blues", fmt=".2f")
plt.title("Correlación entre variables numéricas y churn")
plt.tight_layout()
plt.savefig("images/04_correlacion.png", dpi=120)
plt.close()
print("OK: 04_correlacion.png")

# --- Exportar tablas como CSV para el README ---
# Tabla: análisis descriptivo
columnas_num = ["customer_tenure", "account_Charges_Monthly", "account_Charges_Total", "Cuentas_Diarias"]
analisis = df_limpio[columnas_num].describe().T
analisis["mediana"] = df_limpio[columnas_num].median()
analisis["varianza"] = df_limpio[columnas_num].var()
print("\nAnalisis descriptivo:")
print(analisis.to_string())

# Tabla: churn proporcion
print("\nProporcion churn:")
print(df_limpio["Churn"].value_counts(normalize=True).mul(100).round(2))

# Tablas categóricas
for col in variables_categoricas:
    tasa = pd.crosstab(df_limpio[col], df_limpio["Churn"], normalize="index").mul(100).round(2)
    print(f"\nTasa churn por {col}:")
    print(tasa.to_string())

# Tabla: resumen numerico por churn
resumen = df_limpio.groupby("Churn")[variables_numericas].agg(["mean", "median"]).round(2)
print("\nResumen numerico por churn:")
print(resumen.to_string())

# Informe
contrato_churn = pd.crosstab(df_limpio["account_Contract"], df_limpio["Churn"], normalize="index").mul(100).round(2)
print("\nChurn por contrato:")
print(contrato_churn.to_string())

metodo_churn = pd.crosstab(df_limpio["account_PaymentMethod"], df_limpio["Churn"], normalize="index").mul(100).round(2)
print("\nChurn por metodo pago:")
print(metodo_churn.to_string())

resumen_informe = df_limpio.groupby("Churn")[["customer_tenure","account_Charges_Monthly","account_Charges_Total","Cuentas_Diarias","Total_Servicios"]].mean().round(2)
print("\nPromedios por churn:")
print(resumen_informe.to_string())
