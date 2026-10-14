@echo off
rem Recorta los clips de la serie para los huecos del video (necesita yt-dlp y ffmpeg instalados).
rem 1) Revisa cada ventana (inicio-fin, 3 a 5 s) abriendo el enlace; las marcadas AJUSTAR son un valor por defecto.
rem 2) Ejecuta este archivo dentro de la carpeta del proyecto: crea clips\slot_NN.mp4
mkdir clips 2>nul

rem hueco 01: sin clip encontrado (Busca en YouTube: 'Sopranos Bada Bing exterior' o la intro de un episodio)
rem hueco 02: sin clip encontrado (Busca: 'Sopranos Mayham Paulie Vito dinero Carmela hospital')
rem hueco 03 - AJUSTAR (abre el enlace y elige 4-5 s)
yt-dlp -f "bv*[height<=720]+ba/b[height<=720]" --download-sections "*0:00-0:05" --force-keyframes-at-cuts --merge-output-format mp4 -o "clips\slot_03.%%(ext)s" "https://youtu.be/OfUEbx1ddXM"
rem hueco 04 - AJUSTAR
yt-dlp -f "bv*[height<=720]+ba/b[height<=720]" --download-sections "*0:00-0:05" --force-keyframes-at-cuts --merge-output-format mp4 -o "clips\slot_04.%%(ext)s" "https://youtu.be/drh8MNLDt1k"
rem hueco 05 - COMPROBADO: la frase 'Don doesn't wear shorts' esta en 0:15
yt-dlp -f "bv*[height<=720]+ba/b[height<=720]" --download-sections "*0:13-0:18" --force-keyframes-at-cuts --merge-output-format mp4 -o "clips\slot_05.%%(ext)s" "https://youtu.be/kIC6yRjBGwM"
rem hueco 06 - COMPROBADO: los agentes llegan entre 0:50 y 0:58
yt-dlp -f "bv*[height<=720]+ba/b[height<=720]" --download-sections "*0:52-0:57" --force-keyframes-at-cuts --merge-output-format mp4 -o "clips\slot_06.%%(ext)s" "https://youtu.be/LTrQlsxLM7Y"
rem hueco 07: sin clip encontrado (Busca: 'Sopranos Junior Boca Raton Bobby Baccala' o 'Boca' temporada 1)
rem hueco 08 - AJUSTAR (el pinchazo y la imagen ardiendo estan hacia la mitad)
yt-dlp -f "bv*[height<=720]+ba/b[height<=720]" --download-sections "*0:00-0:05" --force-keyframes-at-cuts --merge-output-format mp4 -o "clips\slot_08.%%(ext)s" "https://youtu.be/K1iREHCi1bg"
rem hueco 09 - AJUSTAR
yt-dlp -f "bv*[height<=720]+ba/b[height<=720]" --download-sections "*0:00-0:05" --force-keyframes-at-cuts --merge-output-format mp4 -o "clips\slot_09.%%(ext)s" "https://youtu.be/Rz1DmQgJFEo"
rem hueco 10 - AJUSTAR (el golpe de Bobby llega tras la partida)
yt-dlp -f "bv*[height<=720]+ba/b[height<=720]" --download-sections "*0:00-0:05" --force-keyframes-at-cuts --merge-output-format mp4 -o "clips\slot_10.%%(ext)s" "https://youtu.be/W6ktF-y-hPU"
rem hueco 11 - AJUSTAR
yt-dlp -f "bv*[height<=720]+ba/b[height<=720]" --download-sections "*0:00-0:05" --force-keyframes-at-cuts --merge-output-format mp4 -o "clips\slot_11.%%(ext)s" "https://youtu.be/O893sYU7694"
rem hueco 12 - AJUSTAR
yt-dlp -f "bv*[height<=720]+ba/b[height<=720]" --download-sections "*0:00-0:05" --force-keyframes-at-cuts --merge-output-format mp4 -o "clips\slot_12.%%(ext)s" "https://youtu.be/PXv1H_Oan98"
rem hueco 13 - AJUSTAR (el asesinato esta en la segunda mitad)
yt-dlp -f "bv*[height<=720]+ba/b[height<=720]" --download-sections "*0:00-0:05" --force-keyframes-at-cuts --merge-output-format mp4 -o "clips\slot_13.%%(ext)s" "https://youtu.be/wl04fL6A368"
rem hueco 14 - COMPROBADO: 'Chris, you're in the mafia' dicho entre 3:04 y 3:12
yt-dlp -f "bv*[height<=720]+ba/b[height<=720]" --download-sections "*3:06-3:11" --force-keyframes-at-cuts --merge-output-format mp4 -o "clips\slot_14.%%(ext)s" "https://youtu.be/ZvnVQwLDGWI"
rem hueco 15 - AJUSTAR
yt-dlp -f "bv*[height<=720]+ba/b[height<=720]" --download-sections "*0:00-0:05" --force-keyframes-at-cuts --merge-output-format mp4 -o "clips\slot_15.%%(ext)s" "https://youtu.be/Z-nOIrlg5pQ"
rem hueco 16 - AJUSTAR
yt-dlp -f "bv*[height<=720]+ba/b[height<=720]" --download-sections "*0:00-0:05" --force-keyframes-at-cuts --merge-output-format mp4 -o "clips\slot_16.%%(ext)s" "https://youtu.be/OSId8hyxqH4"
rem hueco 17 - AJUSTAR
yt-dlp -f "bv*[height<=720]+ba/b[height<=720]" --download-sections "*0:00-0:05" --force-keyframes-at-cuts --merge-output-format mp4 -o "clips\slot_17.%%(ext)s" "https://youtu.be/XPT-zh1sk74"
rem hueco 18 - AJUSTAR
yt-dlp -f "bv*[height<=720]+ba/b[height<=720]" --download-sections "*0:00-0:04" --force-keyframes-at-cuts --merge-output-format mp4 -o "clips\slot_18.%%(ext)s" "https://youtu.be/VK68ziSJABk"
