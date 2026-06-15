# Casa Gracia Hotel Boutique — Contexto y Fuentes de Datos para Agentes

> **Propósito:** Este documento le da a cada agente el contexto completo del negocio, los problemas identificados, los datos disponibles y las fuentes para resolverlos. El objetivo final es construir un diagnóstico de data science aplicado a Casa Gracia Hotel Boutique en Cartagena, Colombia, para presentar al dueño del hotel.

---

## 1. El Negocio

**Nombre:** Casa Gracia Hotel Boutique  
**Tipo:** Hotel boutique / Bed & Breakfast  
**Dirección:** Cra. 17 #26-133, Barrio Manga, Cartagena de Indias, Bolívar, Colombia  
**Teléfono:** +573008843211  
**Estrellas:** 3  
**Habitaciones:** 8  
**Amenidades clave:** Piscina al aire libre, rooftop con vista a la bahía, WiFi, aire acondicionado, TV pantalla plana, minibar, parking privado gratuito  
**Airbnb Superhost:** Sí  
**Desayuno:** Disponible a $24.000 COP por persona por día  

---

## 2. Métricas Actuales Verificadas

### 2.1 Calificaciones en Booking.com

| Categoría | Puntuación |
|---|---|
| General | 9.0 / 10 |
| Personal | 9.5 / 10 ⭐ punto más fuerte |
| Limpieza | 9.5 / 10 |
| Instalaciones | 9.3 / 10 |
| Confort | 9.2 / 10 |
| Relación calidad-precio | 9.1 / 10 |
| Ubicación | 9.0 / 10 |
| WiFi | 8.7 / 10 ⚠️ punto más débil |

**Total reseñas Booking:** 203  
**Ranking Booking:** #26 de 140 posadas en Cartagena → Top 20% del mercado  

### 2.2 Precios Observados en Airbnb (snapshots públicos)

| Habitación | Fecha observada | Precio USD |
|---|---|---|
| Queen 101 | Enero 2026 | $55 |
| Queen 101 | Abril 2025 | $55 |
| Queen 203 | Marzo 2025 | $70 |
| Múltiple 103 | Agosto 2025 | $59 |
| King 202 | Septiembre 2025 | $75 |
| General | Julio 2025 | $58 (≈ $240.000 COP) |

**Conclusión:** Variación de apenas $20 USD durante todo el año. No hay evidencia de pricing dinámico por temporada. La diferencia obedece al tipo de habitación, no al mes.

### 2.3 Presencia Digital

| Canal | Estado | Métrica |
|---|---|---|
| Booking.com | ✅ Activo | 203 reseñas, 9.0/10 |
| Airbnb | ✅ Superhost | 4.82-4.94 calificación |
| Instagram | ⚠️ Débil | 885 seguidores, 71 posts |
| Facebook | ❌ Casi inexistente | 3 likes |
| TripAdvisor | ❌ Sin reseñas | Perfil activo, 0 opiniones |

---

## 3. Problemas Identificados con Evidencia

### Problema 1 — Pricing estático en mercado dinámico

**Evidencia:**
- Precios de Casa Gracia varían solo $20 USD durante todo el año
- El mercado de Manga varía hasta 65% entre temporada alta y baja (Momondo, dic 2025)
- Airbnb Smart Pricing documentado por anfitriones como subvaluador de propiedades
- Enero 2026 (mes con 78% de ocupación en Cartagena) = precio más bajo observado del año ($55)

**Fuente:** https://www.momondo.com.co/hoteles/cartagena-de-indias-manga-cartagena-de-indias.ksp

---

### Problema 2 — Algoritmo de Airbnb trabajando en contra

**Evidencia:**
- Airbnb Smart Pricing ajusta precios automáticamente pero subestima propiedades
- Miles de anfitriones reportan precios recomendados por debajo del mercado
- El patrón de precios planos de Casa Gracia es consistente con tener Smart Pricing activado sin supervisión

**Fuentes:**
- https://pricelabs.co/blog/airbnb-smart-pricing/
- https://hello.pricelabs.co/blog/7-proven-roi-benchmarks-for-small-hotels-using-automated-pricing/

---

### Problema 3 — Reseñas sin analizar sistemáticamente

**Problemas detectados en reseñas públicas:**
- Habitaciones sin ventanas → sensación de encierro
- Sin clóset → espacio reducido para ropa
- Limpieza solo si se solicita → no automática
- Piscina sobre comedor → falta de privacidad
- Moho en zona de piscina
- Desayuno con opiniones divididas (de "exquisito" a "muy regular")
- WiFi como punto más bajo (8.7)
- Personal mencionado por nombre en reseñas positivas → dato sin capitalizar

**Lo que no se está haciendo:** nadie está leyendo las 203 reseñas sistemáticamente para extraer patrones de satisfacción e insatisfacción por categoría.

**Fuentes de reseñas:**
- https://www.booking.com/reviews/co/hotel/casa-gracia.es.html
- https://hotelesbeijing.com.co/hotel/casa-gracia-hotel-cartagena/

---

### Problema 4 — Invisibilidad en TripAdvisor

**Evidencia:**
- Perfil activo en TripAdvisor
- Cero reseñas
- Turistas de EE.UU. y México (perfil mayoritario del hotel) usan TripAdvisor y Google para decidir
- Canal gratuito con alto tráfico completamente desaprovechado

**Fuente:** https://www.tripadvisor.es/Hotel_Review-g297476-d33258412-Reviews-Casa_Gracia_Hotel_Boutique-Cartagena_Cartagena_District_Bolivar_Department.html

---

### Problema 5 — Sin sistema de datos propio

**Evidencia:**
- No existe histórico de precios archivado
- No hay seguimiento de ocupación por canal
- No hay comparación sistemática con competencia
- No hay métricas de RevPAR ni ADR propias
- Toda la inteligencia del negocio está dispersa en plataformas externas sin centralizar

---

## 4. Contexto del Mercado

### 4.1 Ocupación Hotelera en Cartagena

| Periodo | Ocupación | Fuente |
|---|---|---|
| 2023 promedio | 70% | Cotelco |
| 2024 promedio | 66% | Cartagena Cómo Vamos |
| Julio 2024 | 68.63% | Cotelco / SIH |
| Enero 2026 | 78% proyectado | Alcaldía Cartagena |
| Oct 2025 (receso) | 72.7% | Cotelco |
| Airbnb Cartagena anual | 68% | AirDNA |

**Contexto clave:** Cartagena lidera ocupación hotelera a nivel nacional, pero la caída de 2023 a 2024 se atribuye directamente a la parahotelería informal.

**Fuentes:**
- https://www.eltiempo.com/colombia/otras-ciudades/hay-crisis-en-la-ocupacion-hotelera-de-cartagena-debido-a-la-parahoteleria-y-las-plataformas-digitales-senala-cotelco-3379395
- https://www.eluniversal.com.co/cartagena/2025/07/30/cartagena-primera-en-ocupacion-hotelera-vuelos-y-cruceros-durante-2024/
- https://www.infobae.com/colombia/2025/10/05/como-esta-la-ocupacion-de-los-hoteles-en-cartagena-medellin-y-santa-marta-para-la-semana-de-receso-de-octubre-de-2025/
- https://investwe.co/colombia/airbnb-la-plataforma-que-esta-invadiendo-de-turistas-a-barrios-de-cartagena/

### 4.2 Parahotelería como competencia directa

- 7.091 alojamientos con RNT vigente en Cartagena
- 91% son viviendas turísticas (Airbnb informales)
- Solo 470 son hoteles formales
- Cartagena concentra el 25.9% de ingresos de plataformas digitales de viviendas turísticas en Colombia
- Todos ajustan precio automáticamente → ventaja competitiva vs hoteles con precio fijo

**Fuente:** https://www.eltiempo.com/colombia/otras-ciudades/hay-crisis-en-la-ocupacion-hotelera-de-cartagena-debido-a-la-parahoteleria-y-las-plataformas-digitales-senala-cotelco-3379395

### 4.3 Precios del Mercado en Manga

| Métrica | Valor | Fuente |
|---|---|---|
| Precio promedio Manga | $41 USD / noche | Momondo dic 2025 |
| Variación alta vs baja | hasta 65% | Momondo |
| Mes más barato | Febrero (-48%) | Momondo |
| Día más barato | Martes | Momondo |
| Día más caro | Lunes | Momondo |

**Fuente:** https://www.momondo.com.co/hoteles/cartagena-de-indias-manga-cartagena-de-indias.ksp

### 4.4 Calendario de Eventos 2026 — Oportunidades de Pricing

| Mes | Evento | Potencial de subida |
|---|---|---|
| Enero | Hay Festival + Festival Internacional de Música | +35-40% |
| Marzo-Abril | Semana Santa | +35% |
| Mayo | Mayor concentración de eventos del año | +30% |
| Noviembre | Festival Náutico (Nicky Jam confirmado) | +50% |
| Diciembre | Temporada navideña (récord 764.000 visitantes en 2025) | +45% |

**Fuentes:**
- https://www.cartagena.gov.co (40 eventos 2026 oficiales)
- https://www.revistayate.com.co (Festival Náutico 2026)

---

## 5. Competencia Directa

### 5.1 Bahía Azul Boutique Hotel — Manga (mismo barrio)

| Métrica | Valor |
|---|---|
| Precio desde | $51 USD / noche |
| Calificación Airbnb | 4.94 / 5 |
| Ubicación | Manga, Cartagena |
| Diferenciador | Brisa marina, diseño boutique |

**Fuentes:**
- https://www.booking.com/hotel/co/bahia-azul-manga-cartagena.html
- https://www.airbnb.com/rooms/1395261514605535440
- https://www.booking.com/reviews/co/hotel/bahia-azul-manga-cartagena.es-mx.html

### 5.2 Lunalá Hotel Boutique — Centro Histórico

| Métrica | Valor |
|---|---|
| Precio | $113 - $163 USD / noche |
| Reseñas totales | 547 |
| Variación alta vs baja | ~44% |
| Pricing dinámico | Sí (por día de semana) |

### 5.3 Casa Jaguar — Getsemaní

| Métrica | Valor |
|---|---|
| Precio Airbnb | $87 - $99 USD |
| Precio TripAdvisor | hasta $250 USD |
| Habitaciones | 4 |
| Calificación Booking | 9.7 (parejas) |

**Conclusión comparativa:** Casa Gracia tiene mejor o igual calificación que sus competidores directos pero cobra entre 30% y 60% menos.

---

## 6. Fuentes de Datos para Extraer

### 6.1 Datos de Casa Gracia

```
Booking reseñas:
https://www.booking.com/reviews/co/hotel/casa-gracia.es.html

Booking página principal:
https://www.booking.com/hotel/co/casa-gracia.es.html

Airbnb Habitación Queen 101:
https://www.airbnb.mx/rooms/1197228721608888257

Airbnb Habitación Queen 203:
https://www.airbnb.mx/rooms/1247150160057099135

Airbnb Habitación King 202:
https://www.airbnb.mx/rooms/1265108254884566985

Airbnb Habitación múltiple 103:
https://www.airbnb.mx/rooms/1220198022423928832

Instagram:
https://www.instagram.com/casagracia.ctg

TripAdvisor:
https://www.tripadvisor.es/Hotel_Review-g297476-d33258412-Reviews-Casa_Gracia_Hotel_Boutique-Cartagena_Cartagena_District_Bolivar_Department.html
```

### 6.2 Datos de Competencia

```
Bahía Azul Booking:
https://www.booking.com/hotel/co/bahia-azul-manga-cartagena.html

Bahía Azul Airbnb:
https://www.airbnb.com/rooms/1395261514605535440

Bahía Azul reseñas:
https://www.booking.com/reviews/co/hotel/bahia-azul-manga-cartagena.es-mx.html
```

### 6.3 Datos de Mercado

```
Momondo Manga — variación estacional:
https://www.momondo.com.co/hoteles/cartagena-de-indias-manga-cartagena-de-indias.ksp

Kayak Cartagena:
https://www.kayak.com.co/Cartagena-Hoteles.d-1049939.ksp

Expedia variación por mes:
https://www.expedia.com.co/Cartagena-Hoteles.d179877.Travel-Guide-Hotels
```

### 6.4 Datos de Ocupación Oficial

```
Cotelco julio 2024:
https://www.eltiempo.com/colombia/otras-ciudades/hay-crisis-en-la-ocupacion-hotelera-de-cartagena-debido-a-la-parahoteleria-y-las-plataformas-digitales-senala-cotelco-3379395

Cartagena Cómo Vamos 2024:
https://www.eluniversal.com.co/cartagena/2025/07/30/cartagena-primera-en-ocupacion-hotelera-vuelos-y-cruceros-durante-2024/

Cotelco receso oct 2025:
https://www.infobae.com/colombia/2025/10/05/como-esta-la-ocupacion-de-los-hoteles-en-cartagena-medellin-y-santa-marta-para-la-semana-de-receso-de-octubre-de-2025/

AirDNA ocupación Airbnb Cartagena:
https://investwe.co/colombia/airbnb-la-plataforma-que-esta-invadiendo-de-turistas-a-barrios-de-cartagena/

AirDNA directo — Cartagena overview:
https://www.airdna.co/vacation-rental-data/app/co/bolivar/cartagena/overview
```

### 6.5 Herramientas de Pricing y Análisis

```
PriceLabs — pricing dinámico para hoteles boutique:
https://pricelabs.co

AirDNA — histórico de precios y ocupación:
https://www.airdna.co

Airbtics — ocupación Airbnb Cartagena:
https://airbtics.com/airbnb-occupancy-rate-in-cartagena-colombia

PriceLabs blog — benchmarks ROI:
https://hello.pricelabs.co/blog/7-proven-roi-benchmarks-for-small-hotels-using-automated-pricing/
```

### 6.6 Casos de Éxito y ROI

```
Raíz Hotel Boutique México — 43% aumento ingresos:
https://www.littlehotelier.com/blog/increase-your-revenue/revenue-management-small-hotels/

Hotel Tech Report — pricing dinámico +30% ingresos:
https://hoteltechreport.com/resources/revenue-management/reports/revenue-management-systems/hotel-pricing-in-2025

ROI herramientas automatizadas hoteles pequeños:
https://hello.pricelabs.co/blog/7-proven-roi-benchmarks-for-small-hotels-using-automated-pricing/

Duetto — pricing dinámico hoteles independientes:
https://www.duettocloud.com/library/how-boutique-independent-hotels-drive-revenue-with-dynamic-pricing
```

---

## 7. Tareas por Agente

### Agente 1 — Scraping y extracción de datos

**Objetivo:** Extraer precios, calificaciones y reseñas de todas las plataformas listadas.

**Tareas específicas:**
1. Extraer precios de las 4 habitaciones de Casa Gracia en Airbnb en al menos 12 fechas diferentes cubriendo todos los meses del año
2. Extraer las 203 reseñas de Booking de Casa Gracia con fecha, calificación y texto
3. Extraer precios de Bahía Azul en Airbnb en las mismas fechas
4. Extraer precios promedio de Manga desde Momondo para cada mes disponible
5. Extraer calificaciones por categoría de Bahía Azul en Booking

**Output esperado:** CSVs limpios con columnas: fecha, propiedad, habitacion, precio_usd, fuente

---

### Agente 2 — Análisis de sentimientos en reseñas

**Objetivo:** Leer las 203 reseñas de Casa Gracia y extraer patrones de satisfacción e insatisfacción por categoría.

**Categorías a analizar:**
- Personal (nombres mencionados, actitudes, idiomas)
- Desayuno (calidad, variedad, precio)
- Habitaciones (tamaño, ventanas, limpieza, mobiliario)
- Piscina (tamaño, limpieza, privacidad, ubicación)
- WiFi (velocidad, cobertura, confiabilidad)
- Ubicación (distancia al centro, transporte, seguridad)
- Precio-valor (si se menciona como caro, justo o barato)

**Herramientas sugeridas:** Python con transformers (BERT en español), spaCy, VADER

**Output esperado:** DataFrame con columna de reseña, categoría, sentimiento (positivo/negativo/neutro), intensidad y palabras clave

---

### Agente 3 — Análisis de pricing y comparación de mercado

**Objetivo:** Comparar la estructura de precios de Casa Gracia con el mercado de Manga y con los eventos de Cartagena 2026.

**Tareas específicas:**
1. Construir serie de tiempo de precios de Casa Gracia mes a mes
2. Construir serie de tiempo de precios promedio de Manga mes a mes
3. Superponer calendario de eventos de Cartagena 2026 sobre ambas series
4. Calcular diferencia entre precio de Casa Gracia y precio promedio del mercado por mes
5. Identificar semanas específicas donde el gap es mayor (oportunidades de subida de precio)
6. Calcular ingreso adicional potencial si se aplica pricing dinámico

**Output esperado:** Gráfica de líneas con tres series: precio Casa Gracia, precio mercado Manga, eventos marcados. Tabla de oportunidades de pricing con fecha, precio actual, precio sugerido, diferencia en USD.

---

### Agente 4 — Dashboard de diagnóstico

**Objetivo:** Construir visualización para presentar al dueño del hotel el martes.

**Secciones del dashboard:**
1. Calificaciones por categoría de Casa Gracia vs Bahía Azul (barras horizontales)
2. Precio Casa Gracia vs mercado Manga por mes (líneas con eventos marcados)
3. Análisis de sentimientos por categoría de reseñas (barras con positivo/negativo)
4. Comparación de reseñas totales: Casa Gracia 203 vs Lunalá 547 vs Bahía Azul
5. Presencia digital: canales activos vs inactivos con potencial estimado

**Importante:** Etiquetar claramente qué datos son reales y cuáles son simulados. No presentar datos inventados como reales.

**Output esperado:** Dashboard interactivo en React o HTML, o en su defecto slides con gráficas exportadas en PNG.

---

## 8. Métricas Clave a Calcular

Estas son las métricas que el dueño del hotel debe aprender a monitorear:

| Métrica | Definición | Cómo calcularla |
|---|---|---|
| ADR (Average Daily Rate) | Ingreso promedio por habitación ocupada | Ingresos totales / noches vendidas |
| RevPAR (Revenue per Available Room) | Ingreso por habitación disponible | ADR × tasa de ocupación |
| Tasa de ocupación | % de habitaciones vendidas | Noches vendidas / noches disponibles |
| Score de reputación | Promedio ponderado de calificaciones | Promedio de Booking + Airbnb + Google |
| Ingreso por canal | Cuánto genera cada plataforma | Reservas × precio - comisión de canal |
| Indice de sentimiento | % de reseñas positivas por categoría | Reseñas positivas / total reseñas por categoría |

---

## 9. Stack Tecnológico Sugerido

```python
# Scraping
requests, BeautifulSoup, Selenium, Playwright

# Análisis de datos
pandas, numpy

# Análisis de sentimientos
transformers (BERT), spaCy, VADER, langdetect

# Visualización
plotly, matplotlib, seaborn

# Dashboard
Streamlit (rápido de deployar) o React (más presentable)

# Almacenamiento
SQLite para proyecto piloto, PostgreSQL si escala

# APIs externas útiles
AirDNA API (de pago, pero tiene trial)
PriceLabs API
Google Maps API (para datos de ubicación y reseñas de Google)
```

---

## 10. Entregable Final para el Dueño

El diagnóstico que se le presentará al dueño el martes debe responder estas cuatro preguntas con datos:

**Pregunta 1:** ¿Cuánto dinero está dejando sobre la mesa por no ajustar precios en temporada alta?

**Pregunta 2:** ¿Qué están diciendo exactamente sus huéspedes que él todavía no ha leído de forma sistemática?

**Pregunta 3:** ¿Cómo se compara Casa Gracia con su competencia directa en precio, calificación y volumen de reseñas?

**Pregunta 4:** ¿Qué canales están generando más valor y cuáles están siendo ignorados?

Cada respuesta debe ir acompañada de un número concreto, una gráfica y una recomendación accionable de máximo dos líneas.

---

*Documento generado para reunión con dueño de Casa Gracia Hotel Boutique — Martes 17 de junio de 2026*
*Última actualización: 14 de junio de 2026*
