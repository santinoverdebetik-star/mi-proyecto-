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
