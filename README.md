# Telecom X LATAM 2

## Archivos

| Recurso | Contenido |
|---|---|
| `TelecomX_LATAM.ipynb` | Parte 1 · limpieza y analisis exploratorio |
| `TelecomX_PARTE2_Modelado.ipynb` | Parte 2 · modelado predictivo de churn |
| `data/telecomx_parte1_limpio.csv` | dataset tratado usado en ambas partes |
| `images/` | graficas exportadas para el analisis |

## Resumen del dataset

> Se partio de 7267 registros. Tras eliminar 224 filas sin valor de churn y completar 11 valores faltantes en cargos totales, el dataset quedo con 7043 filas limpias y 21 columnas, sin duplicados.

| Estado | Filas | Columnas |
|---|---:|---:|
| Dataset original | 7267 | 21 |
| Dataset tratado | 7043 | 21 |

| Calidad del dato | Valor |
|---|---:|
| Registros con `Churn` ausente eliminados | 224 |
| Valores faltantes en `account_Charges_Total` completados con `0` | 11 |
| Duplicados totales | 0 |

## Distribucion de churn

> El 26.54% de los clientes cancelaron el servicio. El desbalance es moderado: hay suficientes casos de churn para entrenar modelos sin tecnicas de remuestreo, pero el recall puede verse afectado si no se ajusta el umbral de decision.

| Clase | Cantidad | Porcentaje |
|---|---:|---:|
| No churn | 5174 | 73.46 |
| Churn | 1869 | 26.54 |

![Distribucion de churn](images/01_distribucion_churn.png)

## Variables numericas

> La permanencia media es de 32 meses con alta dispersion (std 24.56), lo que indica que hay tanto clientes muy nuevos como muy antiguos. Los cargos mensuales promedio son de $64.76, con una facturacion total media de $2,279 que refleja el tiempo acumulado del cliente.

| Variable | count | mean | std | min | 25% | 50% | 75% | max |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| customer_tenure | 7043 | 32.37 | 24.56 | 0.00 | 9.00 | 29.00 | 55.00 | 72.00 |
| account_Charges_Monthly | 7043 | 64.76 | 30.09 | 18.25 | 35.50 | 70.35 | 89.85 | 118.75 |
| account_Charges_Total | 7043 | 2279.73 | 2266.79 | 0.00 | 398.55 | 1394.55 | 3786.60 | 8684.80 |
| Cuentas_Diarias | 7043 | 2.16 | 1.00 | 0.61 | 1.18 | 2.34 | 2.99 | 3.96 |

![Distribucion numerica](images/03_distribucion_numericas.png)

## Churn por variables categoricas

> El tipo de contrato es el factor categorico con mayor impacto: los clientes mes a mes cancelan a una tasa del 42.71%, frente al 2.83% de contratos bianuales. El pago por cheque electronico y el servicio de fibra optica tambien concentran tasas de churn elevadas.

| Contrato | No (%) | Churn (%) |
|---|---:|---:|
| Month-to-month | 57.29 | 42.71 |
| One year | 88.73 | 11.27 |
| Two year | 97.17 | 2.83 |

| Metodo de pago | No (%) | Churn (%) |
|---|---:|---:|
| Bank transfer (automatic) | 83.29 | 16.71 |
| Credit card (automatic) | 84.76 | 15.24 |
| Electronic check | 54.71 | 45.29 |
| Mailed check | 80.89 | 19.11 |

| Servicio de internet | No (%) | Churn (%) |
|---|---:|---:|
| DSL | 81.04 | 18.96 |
| Fiber optic | 58.11 | 41.89 |
| No | 92.60 | 7.40 |

![Churn por variables categoricas](images/02_churn_categoricas.png)

## Correlacion

> La permanencia del cliente (tenure) muestra la correlacion mas fuerte con churn (-0.35): a menor tiempo en la empresa, mayor riesgo de cancelacion. El cargo total acumulado sigue el mismo patron (-0.20) al ser derivado del tiempo. El cargo mensual tiene una correlacion positiva debil (0.19), sugiriendo que planes mas caros generan algo mas de churn.

| Variable | Correlacion con churn |
|---|---:|
| customer_tenure | -0.35 |
| account_Charges_Monthly | 0.19 |
| account_Charges_Total | -0.20 |
| Total_Servicios | -0.02 |

![Correlacion](images/04_correlacion.png)

## Parte 2 · Modelado predictivo

> Se eliminaron columnas sin valor predictivo (`customerID`) y se aplico `OneHotEncoder` a las variables categoricas. Se entrenaron dos modelos con distintos enfoques: Regresion Logistica con escalado y Random Forest sin escalado. El split fue 70/30 con estratificacion para mantener la proporcion de churn.

| Preparacion | Estado |
|---|---|
| Columna eliminada | `customerID` |
| Encoding | `OneHotEncoder` |
| Escalado para modelo lineal | `StandardScaler` |
| Balanceo adicional | no aplicado |
| Split train/test | 70 / 30 |

| Modelo | Usa escalado | Accuracy train | Accuracy test | Precision test | Recall test | F1 test | ROC-AUC test | Gap accuracy |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| LogisticRegression | Si | 0.8097 | 0.7974 | 0.6383 | 0.5472 | 0.5893 | 0.8404 | 0.0123 |
| RandomForest | No | 0.9327 | 0.7866 | 0.6239 | 0.4938 | 0.5512 | 0.8311 | 0.1461 |

| Lectura de ajuste | Resultado |
|---|---|
| LogisticRegression | ajuste razonable |
| RandomForest | posible overfitting |

## Mejor modelo

> La Regresion Logistica gano con ROC-AUC de 0.8404 y un gap train/test de solo 0.0123, lo que indica buen ajuste sin sobreentrenamiento. Random Forest mostro overfitting claro (gap 0.1461): aprende bien el conjunto de entrenamiento pero no generaliza igual de bien a datos nuevos.

| Modelo ganador | Accuracy | Precision | Recall | F1 | ROC-AUC |
|---|---:|---:|---:|---:|---:|
| LogisticRegression | 0.7974 | 0.6383 | 0.5472 | 0.5893 | 0.8404 |

| Matriz de confusion · LogisticRegression | Predicho No | Predicho Churn |
|---|---:|---:|
| Real No | 1378 | 174 |
| Real Churn | 254 | 307 |

| Matriz de confusion · RandomForest | Predicho No | Predicho Churn |
|---|---:|---:|
| Real No | 1385 | 167 |
| Real Churn | 284 | 277 |

## Variables mas influyentes

> Ambos modelos coinciden en que `customer_tenure` y `account_Charges_Total` son los predictores mas importantes. La Regresion Logistica ademas asigna alto peso al tipo de contrato bianual (efecto protector) y al contrato mes a mes (efecto de riesgo). Random Forest distribuye mas uniformemente la importancia entre variables numericas y categoricas.

| LogisticRegression | Importancia |
|---|---:|
| num__customer_tenure | 1.472860 |
| num__account_Charges_Total | 0.723144 |
| cat__account_Contract_Two year | 0.719663 |
| cat__account_Contract_Month-to-month | 0.583022 |
| cat__internet_InternetService_DSL | 0.363712 |
| cat__account_PaperlessBilling_No | 0.354400 |
| cat__phone_PhoneService_Yes | 0.341093 |
| cat__internet_TechSupport_Yes | 0.302755 |
| cat__phone_MultipleLines_No | 0.284102 |
| cat__customer_Dependents_Yes | 0.249339 |

| RandomForest | Importancia |
|---|---:|
| num__customer_tenure | 0.147588 |
| num__account_Charges_Total | 0.139297 |
| num__account_Charges_Monthly | 0.110610 |
| cat__account_Contract_Month-to-month | 0.077583 |
| cat__internet_TechSupport_No | 0.039331 |
| cat__account_PaymentMethod_Electronic check | 0.036358 |
| cat__internet_OnlineSecurity_No | 0.034630 |
| cat__internet_InternetService_Fiber optic | 0.032912 |
| cat__account_Contract_Two year | 0.023141 |
| cat__internet_OnlineBackup_No | 0.018557 |

## Hallazgos clave

> Los patrones de churn estan dominados por variables de comportamiento contractual y tiempo de permanencia. Los clientes de alto riesgo son identificables desde el inicio de la relacion comercial, lo que abre una ventana de intervencion temprana para equipos de retencion.

| Hallazgo | Valor |
|---|---|
| Mayor riesgo de churn | contratos `Month-to-month` |
| Mayor riesgo por pago | `Electronic check` |
| Mayor riesgo por servicio | `Fiber optic` |
| Variable numerica mas asociada | menor `customer_tenure` |

## Conclusiones estrategicas

> El modelo predictivo confirma que el churn es anticipable con variables disponibles desde el alta del cliente. La Regresion Logistica es suficiente para este problema y su interpretabilidad facilita la toma de decisiones. Las mejoras futuras deben enfocarse en aumentar el recall para detectar mas casos reales de churn antes de que ocurran.

| # | Conclusion |
|---:|---|
| 1 | La cancelacion se concentra en clientes con menor permanencia y menor cargo total acumulado, lo que apunta a fuga temprana |
| 2 | La Regresion Logistica se beneficia de la estandarizacion porque optimiza coeficientes sobre variables en distintas escalas |
| 3 | Random Forest permite contrastar un enfoque no lineal sin dependencia de escala y aporta una segunda lectura de importancia de variables |
| 4 | Si el recall del churn resulta insuficiente, el siguiente ajuste es mover el umbral de decision o usar pesos de clase antes de remuestreo |
| 5 | Las acciones de retencion deben priorizar clientes nuevos, contratos flexibles y perfiles con senales de bajo compromiso de permanencia |

| Perfil de mayor riesgo | Descripcion |
|---|---|
| Permanencia | Clientes con `customer_tenure` bajo (primeros meses) |
| Contrato | Contrato `Month-to-month` |
| Pago | Metodo `Electronic check` |
| Servicio | `Fiber optic` sin soporte tecnico ni seguridad en linea |
| Compromiso | Sin servicios adicionales contratados |
| Modelo con mejor desempeno | `LogisticRegression` |

## Graficas disponibles

| Parte | Grafica |
|---|---|
| Parte 1 | `images/01_distribucion_churn.png` |
| Parte 1 | `images/02_churn_categoricas.png` |
| Parte 1 | `images/03_distribucion_numericas.png` |
| Parte 1 | `images/04_correlacion.png` |