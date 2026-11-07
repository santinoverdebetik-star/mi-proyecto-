# Canal de historias raras del lado oculto de la IA — guía de estilo

Referencia analizada: **"AI Viruses Are Almost Here"** (canal *Token Drift*, 15:58, ~275 mil vistas, publicado 2026-10-16).
https://www.youtube.com/watch?v=QyoEVnzZYpU

> **Qué pude y qué no pude analizar (por honestidad):** no pude *ver* el video completo (YouTube bloquea la descarga desde este
> entorno y la herramienta de análisis visual requiere un plan de pago). Lo que está analizado viene de: (1) la **transcripción completa**
> con tiempos (`referencia_transcripcion.txt`), (2) la **miniatura** y **3 fotogramas** del video que YouTube publica
> (`referencia/`), (3) los metadatos. De lo visual, entonces, tengo certeza sobre el look de esas 4 imágenes; el ritmo exacto de
> cortes, la música y los efectos de sonido son **inferencias** y están marcados como tal. Si me pasás el video descargado (o 2–3 clips de
> 20 s), afino los números.

## 1. Look visual (lo que se ve en los fotogramas)

Tres "familias" de plano, todas sobre **negro casi puro** (#040405), sin personas ni caras:

| Familia | Qué es | Cómo replicarla |
|---|---|---|
| **A. Objeto 3D hiperrealista** | Un objeto cotidiano en macro (RJ-45 de cristal con LEDs rojos saliendo de una pantalla rota; manómetro analógico con aguja y arco rojo). Iluminación dramática de bajo contraste, **un solo acento de color que brilla** (naranja/rojo). | Imágenes generadas con IA (ver prompt abajo), animadas con empuje lento + paralaje. |
| **B. Diagrama de línea neón** | Iconos *wireframe* en **cian** sobre negro (casa, nevera, aspiradora, móvil, laptop, TV) con **arcos eléctricos** que los unen. | `Diagrama.tsx` (hecho): líneas que se dibujan, "infección" que cambia a naranja y chisporrotea. |
| **C. UI minimalista** | Mockup oscuro (candado 3D, campo de contraseña con **línea roja tachada**). | Escena `imagen` con un render del mockup, o SVG. |

**Paleta:** negro `#040405` · naranja `#ff5a1f` (amenaza/IA) · rojo `#e0201b` (alerta) · cian `#35d9ff` (tecnología normal) · crema `#f1e8d6` (texto).
Regla: **cian = lo normal, naranja/rojo = lo que se "infecta"**. El color cuenta la historia.

**Tipografía:** condensada gruesa en mayúsculas, **crema desgastada** (textura de tinta gastada) — "NEW GUEST" en la miniatura, la primera línea en tamaño menor y la palabra clave más grande.
Local: *Anton* (equivalente libre).

**Miniatura:** objeto 3D enorme a la derecha, 2 palabras a la izquierda, mucho negro. Una sola idea.

## 2. Edición (inferido — confirmar con el video)

- **Sin caras, sin presentador.** Solo voz en off.
- **Sin subtítulos grabados** en los fotogramas disponibles (supuesto; lo dejé desactivado por defecto).
- Planos de 3–7 s con **empuje lento (dolly-in)** y leve deriva; cada frase nueva = nuevo plano. Gráficos de datos (contadores, escala 0.5–1.0–1.5) para cifras.
- **Acabado común** (ya implementado en `Capas.tsx`): viñeta fuerte, grano de película a ~15 fps, polvo flotante, parpadeo de luces.
- **Sonido (inferido):** ambiente oscuro/drone de bajo volumen, *risers* antes de revelaciones, *hit* grave en los golpes de dato, silencios cortos antes de la frase clave. Voz grave, calmada, pausada.

## 3. Estructura narrativa (esto sí está verificado en la transcripción)

Es **misterio/tensión, no noticia**. La plantilla que se repite y que vamos a copiar:

1. **Gancho en segunda persona y en escena (0:00–0:35):** *"Imagina que es de noche. Tu TV está apagada. La lucecita de la caja parpadea…"* → "lo que ocurre en tu casa sin que lo sepas". Cierra con "científicos creen que estamos peligrosamente cerca".
2. **Hecho real inquietante** (Kimwolf: 2 millones de dispositivos) con cifras concretas y fuente (Synthient, enero 2026).
3. **Precedente histórico** (Mirai, 2016) para dar escala, y su **límite** ("Mirai era tonto").
4. **"Ahora imagina…"**: el giro hipotético (un gusano con cabeza de IA).
5. **Experimento real** (Anthropic: 15 cajas, 26B parámetros) con números → "ridículamente lento, pero funciona".
6. **El obstáculo y la cuenta que lo vuelve aterrador** (2 días por copia → 1 000 en 3 semanas → 1 M en mes y medio).
7. **Giro con metáfora** (*Memento*: notas generación tras generación; moho mucilaginoso).
8. **Contramedidas** y por qué fallan (no hay botón, el 1 % que queda rebrota).
9. **Cierre circular:** vuelve a la lucecita del inicio. Última frase deja la duda: *"¿…era la última copia? ¿o ya volvió a parpadear una lucecita?"*

Técnicas de guion: segunda persona, frases cortas, cifras concretas, una pregunta que la frase siguiente responde, "pero hay un detalle", cada sección termina con una puerta abierta. Todo con hechos que se pueden citar (el video nombra fuentes).

## 4. Prompt base para las imágenes 3D (a generar con IA de imágenes)

Las escenas procedurales de Remotion son un sustituto; el look del video **es render fotorrealista**, y eso lo da un generador de imágenes. Plantilla:

> `Hyper-realistic 3D render, cinematic macro shot of [OBJETO COTIDIANO] , pitch-black background, single [naranja/rojo] glowing accent light, dramatic low-key lighting, shallow depth of field, subtle film grain, volumetric haze, no people, no text, 16:9`

Se guardan en `video/public/img/escena_NN.png` y se usan con `{ tipo: "imagen", archivo: "img/escena_NN.png", dur: 5 }`. Remotion les da empuje lento, brillo de acento, grano, viñeta y polvo.

## 4b. Regla de luz según lo que dice la narración (pedido del usuario)

El video de muestra gustó, pero el usuario pidió **menos oscuridad según el tema**. Cada escena 3D tiene un parámetro `luz`:

| `luz` | Cuándo usarla | Ejemplos |
|---|---|---|
| `noche` (por defecto) | amenaza, intrusión, algo oculto que avanza, suspenso, cierre inquietante | la caja parpadeando de noche, la infección, la puerta que se abre |
| `media` | explicación, contexto, historia ("en 2016…"), cómo funciona algo | diagramas, el precedente histórico, el mecanismo |
| `clara` | datos, ciencia, laboratorio, respiro después de la tensión | el experimento, cifras, "los investigadores midieron…" |

Se escribe en `src/guion.ts`: `{ tipo: "3d", dur: 5, objeto: "contagio", luz: "media" }`. Los titulares y los diagramas siguen sobre negro (son los que dan el contraste). Las imágenes de ImageFX deben pedirse con el mismo criterio (ver "prompt base": cambiar *pitch-black background* por *dim blue-grey studio* en las escenas `media`/`clara`).

## 5. Proyecto Remotion (`video/`)

```
cd historias_ia/video && npm install
npx remotion studio src/index.ts               # vista previa interactiva
npx remotion render src/index.ts Historia out/historia.mp4
```
En esta nube hace falta `CHROMIUM_PATH=/opt/pw-browsers/chromium_headless_shell-1194/chrome-linux/headless_shell`. En tu PC no hace falta.

- `src/guion.ts`: **una escena por idea del guion** (tipos `3d`, `diagrama`, `titular`, `imagen`). `DEMO` es el ejemplo.
- `Historia.tsx` acepta `voz` y `musica` (ficheros en `public/`) y aplica `Acabado` (viñeta+grano+polvo) a todo.
- Estado actual: ejemplo de 19 s con las 4 familias de escena. Las escenas 3D procedurales (caja/TV, núcleo de IA, red que se infecta, puerta, pantalla rota) son rudimentarias, sobre todo `caja_tv` que queda muy oscura.


## REGLAS FIJAS DEL USUARIO (aplicar SIEMPRE, en todos los videos del canal IA DESCONTROLADA)
1. **Ningún clip 3D se repite** dentro de un video. Cada clip debe ilustrar lo que dice la narración en ese momento. `herramientas/prueba_4min.py` lo hace cumplir (`MAX_USOS = 1`) y avisa con "AVISO: se repite el clip…" si la biblioteca no alcanza. Biblioteca actual: 45 objetos 3D procedurales (en `video/src/escenas/Objetos3D*.tsx`). Un video largo (~25 min) necesita ~250 clips únicos: para eso hay que generar imágenes en ImageFX (una por escena) o ampliar la biblioteca.
2. **Clips 3D cortos:** máximo ~5 s cada uno (promedio ~4,5 s).
3. **Mucha más luz:** los clips no deben verse oscuros. Niveles `noche` / `media` / `clara` ya son más claros; usar `media` o `clara` salvo en momentos de amenaza.
4. **Música de aventura/misterio audible de fondo en todo el video** (no un drone grave): `herramientas/musica_aventura.py`. Se baja un poco cuando habla la voz (ducking) y **desde el minuto 2:46 baja un poco más** (parámetro `bajar_desde`).
5. **Transición:** glitch digital. Voz: Martín (Voizum).


## REGLAS FIJAS (V5 — pedido del usuario)
- **Fondo de los clips 3D = estudio oscuro como la referencia** (degradado radial neutro + piso brillante). NADA de fotos de fondo detrás de los objetos 3D.
- **Nada flota**: cada objeto se apoya en el piso (alturas medidas con `src/Medir.tsx`, tabla `MIN_Y` en `Escena3D.tsx`); los que flotan por naturaleza (nube, ojo, globo, núcleo…) se posan sobre un pedestal con aro cian.
- **Ritmo rápido**: se alternan clip 3D (~3 s) y FOTO REAL (~2,2 s) del mismo tema (`escenas/Foto.tsx`); las fotos tampoco se repiten (pool: `public/fotos` de objetos + `public/fondos_raw` de lugares; créditos en CSV).
- Las fotos deben ser MUY realistas (fotografías reales, nunca ilustraciones). Para el video completo de 25 min hacen falta ~250 clips únicos: generar más con ImageFX o ampliar el pool.
- **PROHIBIDOS para siempre (pedido del usuario V6):** los clips 3D `ojo` y `nucleo` (se sustituyen por `camara` y `placa`). Música de fondo MUY baja (nivel 0.10).
- Calidad 3D: entorno de reflejos + antialias activados (render ~0,45 fps por software; ~35 min por cada 20 s de 3D).
- **Insertos entre clips 3D (V8):** poco texto. Gráficos Remotion afines al objeto recién visto (radar, cuadrícula de contagio, barras de tráfico, globo de puntos, lluvia de código, red de contagio, terminal) + foto real solo 1 de cada 4 + cifra grande cuando el guion dice un número. NO usar frases largas en pantalla. Clips 3D ~4,6 s.
- **Audio (V8):** música a 0.05 y efectos de transición (glitch/riser/hit) muy bajos.
- **Render incremental:** `herramientas/render_incremental.py` renderiza por escena y cachea (`video/out/cache`): si solo cambia el audio o unas escenas no se re-renderiza lo demás.

## V10 — estilo copiado del video de referencia 2 (analizado cuadro por cuadro: "ChatGPT Was Caught Hiding Messages From You", Token Drift)
- **Estructura:** salas 3D completas con travelling lento (laboratorio de CRT, jaula de servidores, sala con mapamundi, sala de casa) que se alternan con **pantallas 2D rojas** (ventana crema de navegador, cadena de aparatos en pixel art, tarjetas comparativas, mapas). Terminal verde sobre negro para frases sueltas.
- **Transición 3D → 2D:** la cámara se acerca a un monitor de la sala (`lab3`) y su pantalla roja llena el cuadro (escena `roja` ventana).
- **Iluminación:** sala en penumbra cálida con charcos de luz (lámparas, paneles del techo); no estudio negro.
- Salas en `video/src/escenas/Salas.tsx`; tarjetas/transiciones/pantalla roja en `Pantallas.tsx`; efectos de sonido en `herramientas/sfx.py`.

## REGLAS FIJAS (pedido del usuario, V11) — valen para ESTE video y para TODOS los siguientes
1. **Todo lo que dice el narrador debe estar representado en pantalla en ese mismo momento** (objeto, sala, gráfico o foto de lo que se nombra). El planificador elige el visual por las palabras de las líneas que suenan en cada tramo (palabras clave → objeto/sala/inserto), no solo por la etiqueta del bloque.
2. **El texto nunca ocupa toda la escena.** Si hay texto sobre fondo, el fondo es una **imagen realista** con gradación tipo After Effects (contraste, viñeta, destello de color, grano) y el texto ocupa como mucho ~40 % del cuadro, en un lado. Prohibido el texto gigante sobre negro liso.
3. **Los clips 3D deben durar más** (salas ~8 s, objetos ~6 s; no cortes cortos) y haber **más 3D que insertos**. Los insertos (pantalla roja, tarjetas, radar, globo, terminal, fotos) se **distribuyen a lo largo de TODO el video**, no se concentran al principio.
4. Prohibidos los insertos de mosaico/cuadrícula naranja a pantalla completa (parecen transición).
5. **Duración del video final: 25 a 30 minutos** (voz Martín con velocidad ~0,92 y pausa 650 ms para llegar a >25 min).
6. Apertura con la pantalla de tarjetas pixel-art en español, transiciones profesionales (píxeles/barras/zoom), efectos de sonido suaves, música muy baja.
7. **El 3D se sigue haciendo como en el video de referencia** (salas completas con travelling lento, penumbra cálida, pantallas rojas pixel-art intercaladas, transición entrando en un monitor). Cada vez que se mejore algo, repasar TODAS las reglas fijas de arriba antes de entregar.
8. Insertos distribuidos a lo largo de todo el video (uno cada ~3 clips 3D); la imagen cambia cuando cambia la frase del narrador (cortes en los límites de línea).

## V13 — REFERENCIA 3 (la que mas importa: Token Drift, "The first AI clone is already here", 16 min; analizada cuadro por cuadro y su audio)
- **Look 3D**: escenas casi fotorreales, MUY oscuras (low-key), luz calida de lampara/practicas, acentos TEAL/CIAN en LEDs (router, cajas), **profundidad de campo corta y primeros planos macro** (reloj digital rojo, router con LED, hileras de cajitas negras con cables azules/amarillos sobre una mesa de madera, llave en cerradura, papeles, tazas). Camaras lentas y bajas.
- **Infografias 2D** sobre negro: casa en **linea cian** con sus aparatos, puerta abierta con bicho, **mapa de puntos** con contador ("2,000,000+ INFECTED DEVICES"), **numeros enormes blancos** sobre lluvia de datos, **cuadricula de cajitas** con contador, terminales de texto monoespaciado.
- **Tipografia**: sans condensada tipo DIN (Barlow Condensed), blanco, mayusculas con tracking; un signo (?) en cian como acento. Texto pequeño y centrado, nunca invade la escena.
- **Transiciones**: casi siempre CORTE directo o **fundido por negro**; algun parpadeo digital. Nada de efectos llamativos (el estilo pixel rojo de la referencia 2 se usa solo para las tarjetas comparativas).
- **Musica**: ambiente oscuro continuo, graves/sub-bajo y textura, SIN melodia ni bateria; ~26 dB por debajo de la voz.
- Si el narrador habla de una **IA** → mostrar un **robot** (y cosas afines al tema); cada objeto/escena debe corresponder a lo que se dice.
