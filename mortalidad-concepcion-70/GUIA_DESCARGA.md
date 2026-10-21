# Guía de descarga de datos: mortalidad 70+ (Concepción, regiones y país)

Esta guía lista los archivos que necesita el proyecto, dónde está cada uno y
cómo entregarlos para que la cadena de scripts sea reproducible.

> **Nota:** las páginas de DEIS e INE no se pudieron consultar desde el
> entorno de trabajo porque la red está bloqueada. Las rutas de navegación y
> los nombres de archivo son los habituales de esos sitios, pero pueden haber
> cambiado. Si algo no coincide, guíese por la **descripción** del archivo, no
> por el nombre exacto.

---

## Opción A (recomendada): habilitar la red y dejar que el script descargue

Así la descarga queda automatizada y registrada (URL, fecha y SHA-256), y se
puede repetir cada semana cuando DEIS actualice el archivo preliminar.

1. En Claude Code (web o app), abra el menú del **entorno** en la barra de
   título de la sesión y elija **Edit → Network access**.
2. Seleccione **Custom**, mantenga la lista de gestores de paquetes y agregue:
   - `deis.minsal.cl`
   - `repositoriodeis.minsal.cl`
   - `ine.gob.cl`
   - `www.ine.gob.cl`
3. Guarde y **abra una sesión nueva** en ese entorno. Una sesión que ya está
   corriendo puede no tomar el cambio.
4. Pida: *"continúa el proyecto mortalidad-concepcion-70 desde la rama
   `mortalidad-concepcion-70`, paso 1"*.

Documentación: <https://code.claude.com/docs/en/cloud-environments#network-access>

---

## Opción B: descarga manual

### Archivos requeridos

| # | Archivo | Fuente | Formato habitual | Tamaño aprox. |
|---|---|---|---|---|
| 1 | Defunciones por causa **1990–2021, cifras oficiales** | DEIS – MINSAL | `.zip` con `.csv` | 100–200 MB comprimido |
| 2 | Defunciones por causa **2022–presente, cifras preliminares** (actualización semanal) | DEIS – MINSAL | `.zip` o `.csv` | 20–60 MB |
| 3 | **Diccionario de datos** de defunciones | DEIS – MINSAL | `.pdf` / `.xlsx` | pequeño |
| 4 | Estimaciones y proyecciones de población 2002–2035, **por comuna**, base 2017 | INE | `.xlsx` / `.csv` | 5–20 MB |
| 5 | Estimaciones y proyecciones de población 2002–2035, **por región** (y total país), base 2017 | INE | `.xlsx` / `.csv` | 1–10 MB |
| 6 | **Anuario de Estadísticas Vitales**, cuadros de defunciones por comuna, **2 años** (sugeridos: 2018 y 2019) | INE | `.xlsx` | pequeño |

Los archivos 1, 2, 4 y 5 son **imprescindibles**. El 3 se necesita si el
archivo preliminar viene sin fila de encabezados. El 6 es para la validación
(cruce de totales anuales).

---

### 1–3. DEIS: defunciones

1. Vaya a <https://deis.minsal.cl/#datosabiertos>.
2. En la sección **Datos Abiertos**, busque el bloque **Defunciones** (a veces
   aparece como *"Defunciones por causa"*).
3. Descargue:
   - **Archivo 1:** el que dice *1990–2021* y *cifras oficiales*. El nombre
     típico es parecido a `DEFUNCIONES_FUENTE_DEIS_1990_2021_CIFRAS_OFICIALES.zip`.
   - **Archivo 2:** el que dice *2022–20XX*, *cifras preliminares* o
     *actualización semanal*. El nombre típico es parecido a
     `DEFUNCIONES_FUENTE_DEIS_2022_20XX_<fecha>.zip`.
   - **Archivo 3:** el *diccionario de datos* o *descripción de variables*
     del bloque de defunciones, si está disponible.
4. **Copie la URL de cada archivo:** clic derecho sobre el enlace → *Copiar
   dirección del enlace*. Normalmente apunta a `repositoriodeis.minsal.cl/...`.
5. Si DEIS ya publicó como oficial algún año 2022 o posterior (por ejemplo
   *"1990–2022 cifras oficiales"*), descargue esa versión y avíseme: cambia el
   corte entre datos oficiales y preliminares.

Fíjese en la fecha de actualización del archivo preliminar, si la página la
muestra. Se usa para definir el corte por rezago de inscripción.

### 4–5. INE: proyecciones de población, base 2017

1. Vaya a <https://www.ine.gob.cl>.
2. Navegue a **Estadísticas → Sociales → Demografía y vitalidad →
   Proyecciones de población**.
3. Abra la sección **Base 2017** (estimaciones y proyecciones 1992/2002–2035
   *basadas en el Censo 2017*). **No** use bases anteriores (2002) ni
   proyecciones ya reemplazadas.
4. Descargue:
   - **Archivo 4:** el de **comunas**, desagregado por **sexo y edad**. El
     nombre típico es parecido a `estimaciones-y-proyecciones-2002-2035-comunas.xlsx`.
   - **Archivo 5:** el de **regiones** (o *país y regiones*), por sexo y edad
     simple, si existe.
5. Copie la URL de cada uno.

Abra el archivo de comunas solo para **mirar**, sin guardarlo. Anote si la
edad viene **simple hasta 100+** o si se **cierra en "80 y más"**. Esto
define qué tramos de edad tienen tasa.

### 6. INE: Anuario de Estadísticas Vitales (validación)

1. En <https://www.ine.gob.cl>, vaya a **Estadísticas → Sociales →
   Demografía y vitalidad → Nacimientos, matrimonios y defunciones**
   (o *Estadísticas vitales*), y luego **Anuarios / Publicaciones**.
2. Descargue los **cuadros estadísticos** (Excel) del anuario de **2018** y
   **2019**. Son años oficiales y anteriores al COVID.
3. Lo que se usa es el cuadro de **defunciones por comuna de residencia**.

---

## Reglas para no dañar los archivos

- **No descomprima** los `.zip`: súbalos tal cual. El script los lee directo.
- **No abra y guarde** los `.csv` en Excel. Excel cambia la codificación,
  borra los ceros a la izquierda de los códigos de comuna (08101 → 8101) y
  convierte fechas.
- **No renombre** los archivos. El nombre original sirve como evidencia de
  la versión.
- Si un archivo pesa **mucho menos** que lo indicado en la tabla, la
  descarga probablemente se cortó: descárguelo de nuevo.

### (Opcional) Huella SHA-256 para verificar la integridad

Le permite confirmar que el archivo que llega a la sesión es el mismo que
descargó.

- **Windows (PowerShell):** `Get-FileHash .\ARCHIVO.zip -Algorithm SHA256`
- **macOS / Linux:** `shasum -a 256 ARCHIVO.zip`

---

## Cómo entregarlos

1. **Adjunte los archivos en la conversación** con Claude Code. Yo los copio a
   `mortalidad-concepcion-70/data/raw/`, ejecuto `scripts/01_download.py`
   para registrarlos en `data/raw/SOURCES.md` y sigo con el paso 2.
2. Si algún archivo es **demasiado grande para adjuntar** (típicamente el de
   1990–2021), use la **Opción A**.
3. Pegue además esta tabla completada:

```
| # | Nombre del archivo | URL de descarga | Fecha de descarga | Fecha de actualización indicada en la página | SHA-256 (opcional) |
|---|---|---|---|---|---|
| 1 |  |  |  |  |  |
| 2 |  |  |  |  |  |
| 3 |  |  |  |  |  |
| 4 |  |  |  |  |  |
| 5 |  |  |  |  |  |
| 6 |  |  |  |  |  |
```

Y una nota sobre la edad en el archivo comunal del INE: ¿edad simple hasta
100+ o cierre en "80 y más"?

---

## Checklist

- [ ] 1. Defunciones 1990–2021, oficiales (DEIS)
- [ ] 2. Defunciones 2022–presente, preliminares (DEIS)
- [ ] 3. Diccionario de datos de defunciones (DEIS)
- [ ] 4. Proyecciones INE base 2017 por comuna
- [ ] 5. Proyecciones INE base 2017 por región / país
- [ ] 6. Anuario de Estadísticas Vitales 2018 y 2019 (INE)
- [ ] Tabla de URL y fechas completada
- [ ] Nota sobre la edad máxima en el archivo comunal del INE
