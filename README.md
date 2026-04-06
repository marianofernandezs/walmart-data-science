# Optimización de Inventario

## 1. Contextualización del Proyecto
Este proyecto aborda la gestión de inventarios en el sector del retail masivo (basado en el ecosistema de Walmart), enfocándose en la predicción exacta de ventas diarias para miles de productos (SKUs) en diversos estados y tiendas. El objetivo es mitigar el "efecto látigo" (Bullwhip Effect) y optimizar los costos operativos mediante modelos de aprendizaje automático avanzados.

## 2. Definición del Problema y KPI
- ** Problemática: Necesidad de generar pronósticos precisos para un horizonte de 28 días, enfrentando una demanda altamente intermitente (67.99% de ceros) y manteniendo la coherencia jerárquica entre categorías y tiendas
- ** KPI Principal: WRMSSE (Weighted Root Mean Squared Scaled Error), métrica que prioriza el impacto económico de los productos de alta rotación
- ** Criterio de Éxito: Lograr un pronóstico auditable y explicable (explicabilidad técnica vía SHAP) que supere a los modelos estadísticos tradicionales

## 3. Arquitectura del Pipeline de Datos
El proyecto implementa una arquitectura reproducible y optimizada para grandes volúmenes de datos:
1. Ingesta: Carga de fuentes crudas desde archivos CSV (Sales, Calendar, Prices).
2. Staging (Optimización): Transformación de tipos de datos a int16 y category, reduciendo el consumo de memoria de 3.2 GB a ~678 MB (Reducción del 78%).
3. Curated (Transformación): Cambio de formato Wide-to-Long mediante pd.melt() para estructurar el dataset como una serie de tiempo unificada.
4. Persistencia: Exportación a formato Parquet para preservar la optimización de memoria y servir como checkpoint para el modelado.

## 4. Hallazgos del Análisis Exploratorio (EDA)
- ** Intermitencia Extrema: Se confirmó que aproximadamente 7 de cada 10 registros tienen ventas de cero, lo que invalida métodos estadísticos convencionali.
- ** Patrones de Venta: Los Sábados y Domingos representan los picos de demanda semanal.
- ** Riesgos (Outliers): La categoría FOODS presenta la mayor cantidad de valores atípicos, reflejando picos por eventos especiales o compras masivas, lo que justifica el uso de métricas de error escaladas.
