# Metodología: serie mensual de defunciones 70+ por sexo y edad — Concepción, regiones y país

Estado: **borrador previo a inspeccionar los datos**. Lo marcado como
**[VERIFICAR]** se confirma o corrige en el paso 2 (`02_clean.py` imprime
encabezados, tipos y filas de muestra de cada archivo) y luego se actualiza
este documento con el mapeo definitivo.

## 0. Decisiones de alcance (confirmadas por el usuario, 2026-10-21)

| Tema | Decisión |
|---|---|
| Geografía | Comuna de Concepción (CUT 8101) **más las 16 regiones y el total país**, con los límites actuales |
| Período | **2002–presente** en toda la serie (conteos y tasas), con una sola base INE (2017) y sin el quiebre territorial de 1995–96 |
| Tramos con tasa | 70+, 70–79 y 80+. Los conteos van en 70–79, 80–89 y 90+. Si INE no separa 80–89 y 90+, esos dos tramos van sin tasa |
| Tasa principal | Anualizada y ajustada por días del mes. La ×12 se guarda en una columna aparte |

## 1. Fuentes y unidad de análisis

| Fuente | Cobertura | Uso |
|---|---|---|
| DEIS, defunciones por causa, cifras oficiales | 1990–2021 (se usa 2002–2021) | numerador, años cerrados |
| DEIS, defunciones por causa, preliminar (actualización semanal) | 2022–presente | numerador, `preliminary_flag = 1` |
| INE, estimaciones y proyecciones 2002–2035 por comuna, base 2017 | 2002–2035 | denominador de la comuna; sumado a región y país |
| INE, estimaciones y proyecciones 2002–2035 por región, base 2017 | 2002–2035 | control de la suma comunal; tramos finos si trae edad simple hasta 100+ [VERIFICAR] |

- **Unidad:** defunción no fetal de una persona de 70 años o más, residente
  en Chile, contada en el mes de la fecha de defunción (no en el de
  inscripción). Se asigna a tres niveles geográficos:
  - `pais`: todas las defunciones de residentes, incluso las de comuna de
    residencia ignorada.
  - `region`: la región actual de la comuna de residencia. Las defunciones de
    comuna ignorada no se asignan a ninguna región y se reporta cuántas son.
  - `comuna`: solo Concepción, 8101.
- **Residencia, no ocurrencia:** se filtra por comuna de *residencia*.
  Concepción concentra hospitales de referencia regional (p. ej. el Hospital
  Guillermo Grant Benavente), así que filtrar por lugar de ocurrencia inflaría
  la serie con residentes de otras comunas.
- **Defunciones fetales:** DEIS las publica en una base aparte, así que la base
  de defunciones no debería traerlas. [VERIFICAR] que no existan registros con
  marca de mortinato; para 70+ esto es irrelevante en la práctica.

## 2. Esquema esperado y armonización

Nombres esperados según las publicaciones recientes de DEIS. **[VERIFICAR]**
contra cada archivo, sin suponer que el oficial y el preliminar coinciden.
La armonización se hace con un diccionario explícito
`{columna_origen: columna_canónica}` por archivo dentro de `02_clean.py`, y el
script falla si falta alguna columna canónica.

| Campo canónico | Oficial 1990–2021 (esperado) | Preliminar 2022+ (esperado) | Notas |
|---|---|---|---|
| `fecha_def` | `FECHA_DEF` | `FECHA_DEF` | Parsear a fecha; registrar las no parseables |
| `anio` | `ANO_DEF` / `AÑO` | ídem | Solo para control; el año-mes sale de `fecha_def` |
| `sexo` | `GLOSA_SEXO` / `SEXO` | ídem | Recodificar a Hombre / Mujer / Indeterminado |
| `edad_tipo` | `EDAD_TIPO` | ídem | 1 = años; 2 = meses; 3 = días; 4 = horas. [VERIFICAR] código de "ignorado" |
| `edad_cant` | `EDAD_CANT` | ídem | Ignorado puede venir vacío o como 999. [VERIFICAR] |
| `comuna_res_cod` | `CODIGO_COMUNA_RESIDENCIA` | ídem | Leer como texto y normalizar a 4–5 dígitos (8101 ↔ 08101) |
| `comuna_res_nom` | `GLOSA_COMUNA_RESIDENCIA` | ídem | Control cruzado con el código |
| `region_res` | `GLOSA_REG_RES` / `CODIGO_REGION` | ídem | No se usa directamente: la región se deriva de la comuna armonizada (ver §2.1) |
| `diag1` | `DIAG1` | ídem | Causa básica, CIE-10 |
| `capitulo_diag1` | `CAPITULO_DIAG1` / `GLOSA_CAPITULO_DIAG1` | ídem | Si falta, se deriva de `diag1` |

Riesgos de formato conocidos en estas bases (todos [VERIFICAR]):

- La codificación puede ser latin-1 o UTF-8 con BOM, y puede no ser la misma
  en los dos archivos. Se detecta con una muestra de bytes y se valida que
  "CONCEPCIÓN" y "AÑO" se lean bien.
- El separador suele ser `;`.
- Algunas versiones del archivo preliminar se han publicado **sin fila de
  encabezado**. Si es el caso, se asignan los nombres desde el diccionario de
  datos de DEIS y se deja documentado.
- Hay que leer todo como texto (`dtype=str`) y convertir después; si no, se
  pierden los ceros a la izquierda de los códigos y se corrompen los códigos
  CIE.

### 2.1 Armonización de la región a los límites actuales

Entre 2002 y hoy hubo tres cambios en la división regional. Las proyecciones
INE base 2017 ya vienen con los límites actuales en toda la serie, así que el
numerador tiene que quedar en los mismos límites:

| Región actual | Creada | Desde | Comunas afectadas |
|---|---|---|---|
| XIV Los Ríos | 2007 | X Los Lagos | provincias de Valdivia y Ranco |
| XV Arica y Parinacota | 2007 | I Tarapacá | provincias de Arica y Parinacota |
| XVI Ñuble | 2018 | VIII Biobío | provincias de Diguillín, Itata y Punilla |

- La región se deriva de la **comuna de residencia**, con una tabla de
  correspondencia código antiguo → código CUT vigente (`data/processed/cut_crosswalk.csv`),
  y no del campo de región que trae DEIS, porque ese campo refleja la
  división vigente al momento del registro.
- [VERIFICAR] si DEIS ya entrega los códigos comunales actualizados en toda
  la serie. Si es así, la tabla de correspondencia sirve solo como control.
- Validación: todos los códigos de comuna de residencia tienen que calzar con
  la lista de comunas del archivo INE. Los que no calcen se listan, y el
  script falla si son más del 0,1 %.

**Solapamiento oficial/preliminar:** se toman los años ≤ 2021 del oficial y
los años ≥ 2022 del preliminar. Si el preliminar trae registros de 2021 o
antes, se descartan y se reporta cuántos eran. Cuando DEIS oficialice 2022 o
años posteriores, el corte se mueve con un parámetro único (`ULTIMO_ANIO_OFICIAL`).

## 3. Filtros, en este orden y con conteo en cada paso

1. Registros totales por archivo.
2. Fecha de defunción válida, y año dentro del rango del archivo.
3. Año de defunción ≥ 2002.
4. Comuna de residencia armonizada al CUT vigente (§2.1). Las defunciones con
   residencia ignorada o en el extranjero se separan y se informan; entran
   solo al total país si la residencia es en Chile pero la comuna es ignorada.
   [VERIFICAR] que el código 8101 corresponde a "CONCEPCIÓN" en todos los años.
5. Edad en años: `edad_tipo == 1` y `edad_cant >= 70`.
6. Se excluyen los fetales, si los hubiera.

Los descartes por edad ignorada o sexo indeterminado se cuentan y se
reportan. No se imputan: se espera que sean menos de 0,5 %. Los registros de
sexo indeterminado entran al total y no a la desagregación por sexo, y se
informa cuántos son.

**Duplicados:** la base abierta no trae ID de defunción. Solo se cuentan las
filas idénticas, se reportan y no se eliminan, salvo que sean un número
apreciable.

## 4. Agregación

- Período: año-mes de `fecha_def`, desde enero de 2002.
- Geografía: `geo_level` ∈ {pais, region, comuna} × `geo_code` × `geo_name`.
  Son 18 unidades: el país, 16 regiones y Concepción.
- Dimensiones: `sexo` ∈ {Total, Hombre, Mujer} × `age_band` ∈
  {70+, 70–79, 80–89, 90+}.
- **Grilla completa:** todos los meses × sexos × tramos, rellenando con 0. Las
  celdas pequeñas (p. ej. hombres de 90+, con pocas muertes por mes) no deben
  desaparecer como filas faltantes.
- **Consistencia interna:** Hombre + Mujer (+ Indeterminado) = Total, y la
  suma de los tres tramos = 70+. Además, Σ regiones + ignoradas = país. Son
  aserciones dentro del script.
- **Corte por rezago de inscripción** (preliminar): se excluyen el mes en
  curso y los **3 meses completos anteriores** a la fecha de publicación del
  archivo. Además se revisa el último mes retenido: si queda bajo el 80 % del
  promedio 2015–2019 de ese mes calendario, se recorta uno más. El corte final
  queda escrito en el informe.

## 5. Denominador y tasas

- **Población región y país:** se suma la población comunal y se contrasta
  con el archivo regional del INE (la diferencia debería ser 0 o de redondeo).
- **Población INE:** las estimaciones están referidas al **30 de junio** de
  cada año, es decir, a mitad de año, así que no hace falta interpolar para las
  tasas anuales. Para las tasas mensuales se interpola linealmente entre dos
  30 de junio consecutivos, a mitad de cada mes.
- **Edades disponibles:** [VERIFICAR] si el archivo comunal trae edad simple
  hasta 100+ o si se cierra en un grupo abierto "80 y más". Si se cierra en
  80+, no hay denominador para 80–89 ni para 90+ por separado: las tasas se
  calculan para 70+, 70–79 y 80+, y los tramos 80–89 y 90+ quedan solo con
  conteos. Para que los tres niveles geográficos sean comparables se aplica la
  misma regla en todos, aunque el archivo regional traiga más detalle.
- **Tasa anualizada por 1.000:**
  `tasa = muertes / población × (365,25 / días_del_mes) × 1.000`.
  Esto corrige el largo del mes; con ×12, febrero aparece entre 7 % y 10 %
  más bajo solo por tener menos días, lo que sesga el perfil estacional. La
  tasa ajustada por días es la principal (`rate`), y además se guarda
  `deaths × 12 / pop × 1000` como `rate_x12`, para quedar alineado con el
  brief.
- **Advertencia del denominador post-2020:** la base 2017 no incorpora el
  exceso de mortalidad por COVID ni la migración reciente, por lo que la
  población 70+ de 2020 en adelante puede estar sobreestimada y las tasas
  subestimadas. Esto se documenta como limitación.

## 6. Quiebres conocidos en la serie

Al empezar en 2002, los dos primeros quiebres de esta lista quedan fuera del
período. Se documentan como justificación del corte.

- **Territorio de la comuna:** San Pedro de la Paz y Chiguayante se crearon a
  mediados de los años 90 (Ley 19.436, 1995) a partir de territorio de la
  comuna de Concepción. Hasta ~1995–1996, "residente en Concepción" incluye
  esos territorios. Es esperable un salto a la baja en los conteos, y no es un
  cambio de riesgo. Hualpén (2004) salió de Talcahuano, así que no afecta.
  [VERIFICAR] en los datos si el quiebre se ve y si DEIS recodificó
  retroactivamente.
- **Denominador antes de 2002:** la base 2017 del INE empieza en 2002. Para
  1990–2001 habría que empalmar las proyecciones de bases anteriores, que usan
  otra metodología.
- **Causas, CIE-9 → CIE-10:** Chile adoptó la CIE-10 para mortalidad en
  1997, así que todo 2002+ viene en CIE-10 y no hay quiebre de clasificación.
- **Regiones nuevas (2007, 2018):** se resuelven con la armonización de §2.1.

## 7. Validación

- Totales anuales de Concepción, de las regiones y del país (todas las
  edades) contra el Anuario de Estadísticas Vitales INE para al menos 2 años.
  La diferencia esperada es menor al 1 % en años oficiales.
- El porcentaje de 70+ sobre el total de muertes debería estar entre 60 % y
  75 % en Concepción y en el país. En regiones con estructura más joven (p. ej.
  Antofagasta, Tarapacá) puede quedar bajo ese rango; se reporta por región y
  no se toma como error.
- El total mensual de la serie debe cuadrar con el conteo de registros
  filtrados (sin pérdida en la agregación).

## 8. Salida tidy

Dos archivos con el mismo esquema:

- `output/AAAA-MM-DD_serie_mensual_70mas_concepcion.csv`: solo la comuna, con
  el nombre que pide el brief.
- `output/AAAA-MM-DD_serie_mensual_70mas_regiones_pais.csv`: país + 16
  regiones + Concepción.

Columnas (una fila por geo × year × month × sex × age_band):

`geo_level, geo_code, geo_name, year, month, sex, age_band, deaths, population, rate, rate_x12, preliminary_flag`

`population`, `rate` y `rate_x12` quedan vacíos (no en cero) en los tramos
80–89 y 90+ si INE no los desagrega.
