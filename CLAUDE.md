# Doblajes del canal "Reino Criminal"

Herramienta: `doblaje_pl/doblar.py` (extraer → transcribir → afinar → sintetizar → mezclar → recortar-pausas → qa).

## Receta fija (instrucción permanente del usuario) — paso final de CADA doblaje

Eliminar las pausas largas del video ya montado:

1. Detectar los silencios sobre la **voz limpia** (`voz_pl.wav` / voice_natural), nunca sobre el mix con música (la música los taparía).
2. Recortar las pausas **≥ 0,7 s dejando 0,4 s de respiro**; no tocar los gaps cortos (para que no suene atropellado).
3. Aplicar el corte al **video final ya montado**, cortando video y audio juntos para que queden sincronizados.

Comando: `python doblar.py --dir work recortar-pausas video_final.mp4 salida.mp4 --idioma <pl|de> --crf 26`
Luego: `python doblar.py --dir work qa original.mp4 salida.mp4 --idioma <pl|de> --compacto --glosario glosario.json --modelo medium`

Entregas: subir a `salida/` (Git LFS, cuota gratuita 1 GB) y pasar el enlace + el informe de QA.

## Texto en pantalla (también en cada doblaje)

Antes de mezclar: buscar texto en pantalla (OCR de fotogramas cada 2 s; `doblaje_pl/mansion_ivan/` tiene los scripts de ejemplo: `intro_texto.py` borra el texto original y escribe el traducido con el mismo efecto de aparición; `sub_texto.py` traduce el botón animado Subscribe/Subscribed). Se traducen los textos del canal; los nombres propios y el texto de las imágenes de archivo (mapas, pantallas) se dejan como están. Luego el video con textos traducidos es el que entra a `mezclar`.

## Intro de suscripción de 10 s (instrucción permanente del usuario — en TODOS los videos que se pasen)

Los primeros 10 s de cada video doblado son una intro de aviso de suscripción, y después el video queda igual:
- Narración polaca (voz Piper) que pide suscribirse al canal y activar la campanita. El nombre del canal se dice y se escribe **en polaco: «Królestwo Przestępcze»** (Reino Criminal), nunca en español.
- Dos planos tomados del propio video (sin texto en pantalla), título «SUBSKRYBUJ» + nombre del canal, botón animado Subskrybuj → Subskrybujesz con campana, y la música original.
- **Variar en cada video** (que sea parecido pero no siempre lo mismo): otros planos de fondo (`--a-inicio`, `--b-inicio`), otra frase (`--frase 1|2|3`) y otro color del nombre (`--color`). Mirar una hoja de contacto del video para elegir planos nuevos; no repetir los de videos anteriores (Chapo Isidro: planos a 132 s y 136 s, frase 1, naranja; Nini: planos a 230,5 s y 388 s, frase 2, rojo; Licenciado: planos a 1966,6 s y 628 s, frase 3, celeste; Yogurt: planos a 240 s y 840 s, frase 4, verde; Chapo 701: planos a 200 s y 1190 s, frase 5, amarillo; Mansiones abandonadas: planos a 421,2 s y 1742 s, frase 6, rosa; Niños sicarios: planos a 668 s y 966,5 s, frase 7, violeta).
- Herramienta: `doblaje_pl/intro_suscripcion/crear_intro.py` (con `--unir` pega la intro delante del video final ya recortado, sin recodificarlo). Hacerlo después de `recortar-pausas` y antes de subir; comprobar que los fotogramas del video quedan idénticos (cuenta = 300 + los del video).


## Canal de guerra (nuevo canal del usuario) — `canal_guerra/`

Videos de historia militar en español, **sin cara**, con el estilo de `canal_guerra/ESTILO.md` (imágenes IA cinematográficas + mapas animados + rótulos serif de papel/etiqueta roja + grano y viñeta). Se montan con **Remotion**.

Normas permanentes del usuario:
- **Duración: de 25 a 30 minutos** por video (unas 4.200–4.900 palabras a ~163 palabras/min con la voz elegida).
- **El guion debe ser siempre atrapante y con sentido**: arranca en medio de la acción (gancho), plantea una pregunta que el video responde, cada bloque sube la tensión y cierra con una enseñanza, hay giros y avisos de lo que viene ("recuerda esto, volverá"), el cierre retoma el gancho. Datos solo verificados; lo dudoso se marca en `NOTAS_VERIFICACION.md` o se redacta como "se cuenta / se le atribuye".
- Voz: **Voizum**, voz «salvatore soprano» (id `c9ee4c92-a6dc-4e2d-8a53-2a04e990658f`, español). API `https://voizum.com/api/v1` (Bearer `sk_voizum_…`; POST /tts → GET /tts/{job} → GET /tts/{job}/audio?download=1; 60 créditos/1.000 caracteres; MP3 se borra a los 4 días). Los números y años se escriben con letras en el texto hablado.
- Imágenes: **G-Labs Studio** (Webhook API en `127.0.0.1:8765` del PC del usuario, plan MAX, cabecera `X-API-Key`); desde la nube no se alcanza: el usuario corre `canal_guerra/herramientas/generar_imagenes.py` en su PC y pasa la carpeta por Drive.
- **Las claves NO se guardan en el repo** (ni en commits ni en archivos versionados): variables de entorno o archivos fuera del repo.
