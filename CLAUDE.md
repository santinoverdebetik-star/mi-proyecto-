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
- **Variar en cada video** (que sea parecido pero no siempre lo mismo): otros planos de fondo (`--a-inicio`, `--b-inicio`), otra frase (`--frase 1|2|3`) y otro color del nombre (`--color`). Mirar una hoja de contacto del video para elegir planos nuevos; no repetir los de videos anteriores (Chapo Isidro: planos a 132 s y 136 s, frase 1, naranja; Nini: planos a 230,5 s y 388 s, frase 2, rojo; Licenciado: planos a 1966,6 s y 628 s, frase 3, celeste; Yogurt: planos a 240 s y 840 s, frase 4, verde; Chapo 701: planos a 200 s y 1190 s, frase 5, amarillo; Mansiones abandonadas: planos a 421,2 s y 1742 s, frase 6, rosa).
- Herramienta: `doblaje_pl/intro_suscripcion/crear_intro.py` (con `--unir` pega la intro delante del video final ya recortado, sin recodificarlo). Hacerlo después de `recortar-pausas` y antes de subir; comprobar que los fotogramas del video quedan idénticos (cuenta = 300 + los del video).
