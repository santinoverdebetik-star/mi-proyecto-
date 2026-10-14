# Imágenes para el video — prompts para Google Labs (ImageFX / Whisk), SIN CARAS

Solo paisajes, lugares, objetos y ambientes. Nada de personas, rostros ni actores reales, nada de
logos ni texto legible (la IA lo escribe mal y además evita problemas de marca).

## Cómo usarlos

1. En ImageFX elige proporción **horizontal 16:9**.
2. Pega el **prompt del bloque** y añade al final el **sufijo de estilo** (siempre el mismo, para que
   todas las imágenes parezcan del mismo video):

> **SUFIJO DE ESTILO:** `cinematic photograph, shot on 35mm film, warm desaturated tones, dark moody
> lighting, early 2000s New Jersey atmosphere, subtle film grain, soft vignette, shallow depth of
> field, no people, no faces, no text, no logos, 16:9`

3. Genera 2–4 variantes de cada prompt y quédate con la mejor.
4. Nómbralas con su código (por ejemplo `R10-2.png`) para que luego encajen con el guion.
5. Si una imagen sale con cara, texto o logo, descártala o vuelve a generar con "no people, empty scene".

**Cobertura y regla de ritmo.** La regla es un corte cada 2–4 s. Para 27 minutos eso son ~500 cortes.
No hace falta generar 500 imágenes: con las ~150 de abajo, cada imagen se usa 3–4 veces con
**encuadres distintos** (zoom a un detalle, paneo, versión en blanco y negro o más oscura, desenfoque
al cambiar). Nunca más de 5 segundos seguidos con el mismo encuadre.

---

## BIBLIOTECA GENERAL (G01–G40) — para repetir en cualquier bloque

| Cód. | Prompt (en inglés) |
|---|---|
| G01 | Empty suburban New Jersey street at dusk, parked sedans, overhead power lines, warm streetlights turning on |
| G02 | Rain streaking down a car window at night, blurred neon bokeh outside, interior view |
| G03 | Dark two-lane rural road at night, a single car's red taillights fading into the distance |
| G04 | Old Italian-American social club exterior at night, striped awning, a single warm glowing window, wet pavement |
| G05 | Empty restaurant booth with a red-checkered tablecloth, a candle and a wine bottle, dim light |
| G06 | Empty parking lot behind a strip mall at night, sodium-vapor lights, light fog |
| G07 | Aerial view of an industrial New Jersey waterfront at dawn, cranes and smokestacks in haze |
| G08 | Chain-link fence topped with barbed wire against a gray dusk sky |
| G09 | Closed butcher shop storefront at night, sausages hanging seen through the window, empty |
| G10 | Long empty hospital corridor with flickering fluorescent lights |
| G11 | Suburban backyard with a charcoal grill and patio furniture at golden hour, nobody in frame |
| G12 | Close-up of a rotary dial telephone on a wooden desk, warm lamp light |
| G13 | A cigar burning in a glass ashtray, smoke curling, dark background |
| G14 | Cluttered desk with stacks of cash, a ledger and a desk lamp, noir mood |
| G15 | Empty courtroom with wooden benches, harsh daylight from tall windows |
| G16 | Blank cork board with pushpins and red string, no photos, warm desk lamp (investigation-board look) |
| G17 | Stack of manila folders and an old typewriter on a metal desk, 1980s government office |
| G18 | Brooklyn brownstone street in early morning mist, empty |
| G19 | Highway overpass at night with light trails from passing cars |
| G20 | Black SUV parked at the edge of a forest road at dawn, fog |
| G21 | Empty church interior with candles and stained glass, dim |
| G22 | Old cemetery with weathered stone angels at dusk, mist |
| G23 | Wooden pier over calm water at dawn, fog, melancholy |
| G24 | Lake cabin exterior in autumn, wooden porch, empty chairs |
| G25 | Suburban kitchen at night, single light over the table, a cold cup of coffee |
| G26 | Marble steps of a government building with long shadows |
| G27 | Worn leather briefcase on a wooden table, slightly open, warm light |
| G28 | Wet cobblestone alley in an old Sicilian town at dawn, laundry hanging between buildings |
| G29 | Sicilian countryside hill with a lone farmhouse at sunset |
| G30 | Neon glow reflected on a rain-soaked street, abstract bokeh, no readable signs |
| G31 | Dock warehouse interior with stacked crates, shafts of light through dusty air |
| G32 | A set of keys on a wooden table beside a glass of whiskey, warm light |
| G33 | A shovel leaning against a tree in a dark forest at dusk |
| G34 | Airport window view of a runway at dusk in gray rain |
| G35 | Vintage 1980s sedan parked outside a steakhouse at night, glowing windows |
| G36 | Jewelry shop window with watches and gold chains at night, empty street |
| G37 | Snow-covered suburban street at night, lit windows |
| G38 | Quiet barbershop interior with chairs and mirrors, warm light, empty |
| G39 | Railroad tracks leading into fog at dawn |
| G40 | Manhattan skyline seen from the New Jersey riverbank at dusk |

---

## POR BLOQUE DEL GUION (`GUION_V2.md`)

Cada bloque trae 5–6 prompts propios; combínalos con 3–4 imágenes de la biblioteca general.

### GANCHO (Lo Piccolo y Tony)
| Cód. | Prompt |
|---|---|
| H01 | Sicilian farmhouse at dawn seen from a hillside, a dirt road, distant faint blue police lights, no people |
| H02 | Leather briefcase open on a table with handwritten sheets of paper inside, text illegible and blurred |
| H03 | Neon-lit strip club exterior at night in New Jersey, glowing abstract sign with no readable text, wet road |
| H04 | Rotary phone and a black suit jacket draped over a chair in a dim office |
| H05 | Aged prayer book and a rosary on dark wood, warm candlelight |
| H06 | Foggy suburban cul-de-sac with a lone black sedan at night |
Sugeridas de la biblioteca: G28, G29, G12, G13.

### Regla 1 — "El dinero sube" (Paulie, Vito y el coma)
| Cód. | Prompt |
|---|---|
| R1-1 | Envelope stuffed with cash on a hospital bedside table, dim light, no people |
| R1-2 | Hospital waiting room at night, empty chairs, vending machine glow |
| R1-3 | Duffel bag full of cash on a motel bed, harsh lamp light |
| R1-4 | Shabby apartment building door slightly ajar at night, hallway light spilling out |
| R1-5 | Hospital lobby elevator doors closing, empty lobby |
Sugeridas: G10, G14, G32.

### Regla 2 — "La mafia no toca las drogas"
| Cód. | Prompt |
|---|---|
| R2-1 | Stack of sealed plastic-wrapped brick-shaped packages on a metal table in an empty warehouse, noir lighting |
| R2-2 | Manhattan steakhouse exterior at night in winter, glowing windows, wet sidewalk |
| R2-3 | Handcuffs resting on a wooden courtroom table |
| R2-4 | Garbage trucks parked in a depot at dawn |
| R2-5 | Open ledger with columns of handwritten numbers, desk lamp |
Sugeridas: G31, G35, G40.

### Regla 3 — "Respeta a la esposa de otro" (Ginny y Ralph)
| Cód. | Prompt |
|---|---|
| R3-1 | Dinner table set for two with untouched plates and candles |
| R3-2 | Gold wedding ring on a polished table, close-up |
| R3-3 | Empty restaurant booth at closing time, chairs on tables |
| R3-4 | Telephone receiver left off the hook beside a lamp |
| R3-5 | Glass candy dish on a coffee table in a living room at night |
Sugeridas: G05, G25, G12.

### Regla 4 — "Un iniciado no puede ser homosexual" (D'Amato y Vito)
| Cód. | Prompt |
|---|---|
| R4-1 | Parked car outside a Brooklyn rowhouse at night, streetlight |
| R4-2 | Small New England roadside motel at night, vacancy light glowing (no readable text) |
| R4-3 | Single suitcase on a motel bed, dim lamp |
| R4-4 | Card table in an empty social club, ashtray and abandoned chairs |
| R4-5 | Highway sign-less exit ramp at night in rain |
Sugeridas: G18, G06, G19.

### Regla 5 — "Nadie se retira" (Eugene y Bonanno)
| Cód. | Prompt |
|---|---|
| R5-1 | Arizona desert landscape at sunset with an adobe ranch house |
| R5-2 | Stack of cash beside a one-way bus ticket (text illegible) on a table |
| R5-3 | Suburban house front door with a for-sale sign (no readable text), dusk |
| R5-4 | Closed garage door in a New Jersey suburb at night |
| R5-5 | Riverbank at dusk with bare trees |
Sugeridas: G34, G23, G32.

### Regla 6 — "Un Don no usa shorts"
| Cód. | Prompt |
|---|---|
| R6-1 | Folded khaki shorts on a lawn chair at dusk, backyard barbecue smoking in the background |
| R6-2 | Row of dark tailored suits hanging in a closet, warm light |
| R6-3 | Pair of polished black leather shoes on a wooden floor |
| R6-4 | Glass of iced tea on a patio table, sunset |
| R6-5 | Suburban swimming pool at dusk with a lone inflatable |
Sugeridas: G11, G01.

### Regla 7 — "Un jefe no llora en público" (Johnny Sack)
| Cód. | Prompt |
|---|---|
| R7-1 | Empty wedding reception hall with set tables and flowers, soft light |
| R7-2 | White wedding cake with a toppled champagne flute on a table |
| R7-3 | Black car driving away in the rain with headlights on, wide shot |
| R7-4 | Empty dance floor with scattered confetti at dusk |
| R7-5 | Federal building exterior with flags, overcast |
Sugeridas: G26, G02, G21.

### Regla 8 — "Eso no se hace con una mujer" (Junior en Boca)
| Cód. | Prompt |
|---|---|
| R8-1 | Florida retirement-community street with palm trees under harsh sun |
| R8-2 | Pastel-colored clubhouse exterior with a flagpole |
| R8-3 | Golf cart parked by a pond at sunset |
| R8-4 | Sprinkler watering a perfectly green lawn |
| R8-5 | Empty poolside lounge chairs with towels |
Sugeridas: G11, G37.

### Regla 9 — "La ceremonia tiene que hacerse bien"
| Cód. | Prompt |
|---|---|
| R9-1 | A holy card burning in a ceramic bowl beside a lit candle, close-up, dark background |
| R9-2 | A dark table with a candle, a knife and a white cloth, ritual atmosphere |
| R9-3 | Empty basement room with a single chair under a bare bulb |
| R9-4 | Old stone stairway descending into a cellar |
| R9-5 | A row of lit votive candles in a dark church side chapel |
Sugeridas: G21, G22, G04.

### PARTE 3 — introducción (Comisión, Valachi, Pistone)
| Cód. | Prompt |
|---|---|
| P3-1 | 1930s-style New York street at night, wet cobblestones, empty |
| P3-2 | Senate hearing room with empty seats and microphones, 1960s look |
| P3-3 | FBI-style surveillance van parked on a quiet street at night |
| P3-4 | Reel-to-reel tape recorder on a desk with headphones, warm lamp |
| P3-5 | Long conference table with empty leather chairs, dim chandelier |
Sugeridas: G17, G15, G26.

### Regla 10 — "No se mata a un jefe sin permiso de la Comisión"
| Cód. | Prompt |
|---|---|
| R10-1 | Long boardroom table with empty chairs and a single lamp |
| R10-2 | Manhattan steakhouse exterior at winter dusk with a lone car at the curb |
| R10-3 | Empty Manhattan sidewalk at night in light rain |
| R10-4 | Rusted iron gate in an alley at night |
| R10-5 | Wall clock showing late night in an empty office |
| R10-6 | Black sedan parked under a bridge at night |
Sugeridas: G35, G40, G19.

### Regla 11 — "No se le pone la mano encima a un iniciado" (Bobby)
| Cód. | Prompt |
|---|---|
| R11-1 | Lake cabin porch at dusk with a board game on a table seen through the window, no people |
| R11-2 | Overturned wooden chair on a cabin floor, warm light |
| R11-3 | Lake at dawn with mist |
| R11-4 | Pine forest road in autumn, empty |
| R11-5 | Kitchen table with a bag of ice and a dishcloth, morning light |
Sugeridas: G24, G33.

### Regla 12 — "No se mata a un iniciado sin autorización" (Fat Dom)
| Cód. | Prompt |
|---|---|
| R12-1 | Butcher shop back room with meat hooks and a wooden cutting block, harsh light, empty |
| R12-2 | Pork store exterior at dusk, shuttered windows |
| R12-3 | Stainless steel prep table with kitchen knives, clean, cold light |
| R12-4 | Loading dock behind a store at night |
| R12-5 | Motel room door at night with a flickering light |
Sugeridas: G09, G06, G31.

### Regla 13 — "Avisa a tus superiores" (Tony B)
| Cód. | Prompt |
|---|---|
| R13-1 | Parked car outside a late-night urban establishment, neon glow reflected on the hood |
| R13-2 | Old phone booth on an empty street at night |
| R13-3 | Basement poker table with scattered chips and cards, empty |
| R13-4 | Pile of unopened mail on a doormat |
| R13-5 | Wall map of New Jersey and New York with pins and red string (no readable text) |
Sugeridas: G16, G12, G30.

### Regla 14 — "El jefe se mantiene lejos de la calle" (Tony y Christopher)
| Cód. | Prompt |
|---|---|
| R14-1 | Dark rural road at night, a wrecked car in a ditch, steam rising, headlights glowing |
| R14-2 | Empty infant car seat on a back seat, dim light, no people |
| R14-3 | Emergency flares burning on a dark road |
| R14-4 | Foggy forest at night |
| R14-5 | Car hood lit by headlights in the dark |
Sugeridas: G03, G20, G33.

### Regla 15 — "Los asuntos de la mafia no se cuentan a extraños" (J.T. Dolan)
| Cód. | Prompt |
|---|---|
| R15-1 | Modern apartment living room at night, a laptop with blurred pages, whiskey glass, city lights |
| R15-2 | Film clapperboard on a table, blank slate, warm light |
| R15-3 | Script pages scattered on a wooden floor |
| R15-4 | Apartment front door at night, hallway light |
| R15-5 | City lights through a window at night, curtains moving |
Sugeridas: G25, G32, G02.

### Regla 16 — "Nunca admitas que esto existe" (Johnny Sack ante el tribunal)
| Cód. | Prompt |
|---|---|
| R16-1 | Empty courtroom witness stand with microphone, harsh daylight |
| R16-2 | Judge's gavel on a bench, close-up |
| R16-3 | Federal courthouse steps in the morning |
| R16-4 | Empty prison corridor with a metal gate at the end |
| R16-5 | Wooden benches of a courtroom seen from the back |
Sugeridas: G15, G26.

### Regla 17 — "Nunca colabores con la ley" (informantes, Valachi y Gravano)
| Cód. | Prompt |
|---|---|
| R17-1 | FBI-style surveillance room with headphones, tape reels and a desk, no people |
| R17-2 | Diner booth with two empty coffee cups at night |
| R17-3 | Unmarked sedan parked on a street at dusk |
| R17-4 | Senate hearing room, 1960s look, empty |
| R17-5 | Prison exterior at dawn with watchtower |
| R17-6 | A manila envelope on a table with a red wax-like seal, text illegible |
Sugeridas: G17, G15, G08.

### Regla 18 — "La familia mafiosa va antes que tu familia real" (Coco y Meadow)
| Cód. | Prompt |
|---|---|
| R18-1 | Restaurant interior at night with an overturned chair and neon reflected in a window, no people |
| R18-2 | Quiet suburban house at night with one light on in an upstairs window |
| R18-3 | Parked car outside a restaurant with the driver door open at night |
| R18-4 | Empty family kitchen with a framed photo turned face down on the counter |
| R18-5 | Staircase in a family home at night, warm light |
Sugeridas: G05, G25, G01.

### Regla 19 — Resto del decálogo siciliano
| Cód. | Prompt |
|---|---|
| R19-1 | Neon-lit nightclub exterior at night, abstract glow, no readable text |
| R19-2 | Hotel room bed with two glasses on a nightstand, dim light |
| R19-3 | Binoculars on a car dashboard at night |
| R19-4 | Wedding ring on a bedside table at dawn |
| R19-5 | Empty bedroom in a large home, dawn light, unmade bed |
Sugeridas: G30, G28, G27.

### CIERRE
| Cód. | Prompt |
|---|---|
| C01 | Old brass balance scale with coins on one side, dark wood, warm light |
| C02 | Weathered handwritten list on a leather briefcase, text illegible |
| C03 | Sunrise over a New Jersey highway, empty road |
| C04 | Closing wooden door in a dim hallway, light narrowing |
| C05 | Road leading into dense fog |
| C06 | Empty chair at the head of a long table |
| C07 | Candle burning low beside a closed book |
| C08 | Empty social club at night with a single neon glow |
Sugeridas: G04, G27, G40.

---

## Resumen
- Biblioteca general: 40 · Gancho: 6 · Reglas 1–19: ~100 · Parte 3: 5 · Cierre: 8 → **~160 imágenes**.
- Con 3–4 usos por imagen (encuadres distintos, blanco y negro, oscurecido, desenfoque) se cubren ~500 cortes.
- **Fotos reales que sí conviene incluir** (no son de la serie): fotos históricas de dominio público (por
  ejemplo en Wikimedia Commons) del juicio, del Senado en 1963 o de la calle de Nueva York de la época.
  Revisa la licencia de cada una.
- **Clips y fotos de la serie:** los pones tú, de 3–5 s como máximo y con narración encima.
