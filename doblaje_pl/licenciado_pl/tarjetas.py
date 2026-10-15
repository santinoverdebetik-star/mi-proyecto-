# -*- coding: utf-8 -*-
"""Textos en pantalla (tarjetas) del video y su traducción al polaco.
Cada tarjeta: ventana aproximada (s), alineación ('c' centrada, 'l' izquierda) y líneas (es, pl).
`es` = texto original (para calibrar la tipografía y encontrar la línea con OCR); `pl` = traducción; pl=None -> no se toca (nombres propios, etc.)."""
CARDS = [
 dict(t=(44, 52), al='l', lines=[
    ("EL CÁRTEL DE SINALOA", "KARTEL Z SINALOA"),
    ("La organización en la que el Licenciado llegó a la cima", "Organizacja, w której Licenciado dotarł na szczyt"),
    ("Mapa base: Natural Earth / GSHHS", "Mapa: Natural Earth / GSHHS")]),
 dict(t=(100, 106), al='c', lines=[
    ("El hombre que sacó al Chapo de prisión...", "Człowiek, który wyciągnął Chapo z więzienia..."),
    ("y después lo traicionó", "a potem go zdradził")]),
 dict(t=(282, 286), al='l', lines=[
    ("Penal de Almoloya", "Więzienie Almoloya"),
    ("Guatemala", "Gwatemala"),
    ("9 de junio de 1993", "9 czerwca 1993"),
    ("1993: LA PRIMERA CAPTURA", "1993: PIERWSZE ZATRZYMANIE"),
    ("El Chapo es detenido en Guatemala y entregado a México", "El Chapo zatrzymany w Gwatemali i przekazany Meksykowi"),
    ("Mapa base: Natural Earth / GSHHS", "Mapa: Natural Earth / GSHHS")]),
 dict(t=(294, 304), al='l', lines=[
    ("Estado de México", "Stan Meksyk"),
    ("1995: PUENTE GRANDE", "1995: PUENTE GRANDE"),
    ("El Chapo es trasladado a un nuevo penal de máxima seguridad", "El Chapo przeniesiony do nowego więzienia o zaostrzonym rygorze"),
    ("Mapa base: Natural Earth / GSHHS", "Mapa: Natural Earth / GSHHS")]),
 dict(t=(644, 646), al='c', lines=[
    ("«Javi» y «Roberto»", "„Javi” i „Roberto”"),
    ("Los dos contactos dentro del gobierno, según su", "Dwa kontakty w rządzie, według jego"),
    ("testimonio", "zeznań"),
    ("Juicio contra Joaquín Guzmán Loera, Nueva York, enero de 2019", "Proces Joaquína Guzmána Loery, Nowy Jork, styczeń 2019")]),
 dict(t=(694, 704), al='l', lines=[
    ("Sudamérica", "Ameryka Południowa"),
    ("Panamá", "Panama"),
    ("Nueva York", "Nowy Jork"),
    ("MÁS ALLÁ DE MÉXICO", "POZA MEKSYKIEM"),
    ("Contactos que las autoridades de Estados Unidos le atribuyen en Perú y Panamá", "Kontakty, które władze USA mu przypisują w Peru i Panamie"),
    ("LA CADENA", "ŁAŃCUCH"),
    ("De Sudamérica a las ciudades de Estados Unidos", "Z Ameryki Południowej do miast Stanów Zjednoczonych"),
    ("Mapa base: Natural Earth / GSHHS", "Mapa: Natural Earth / GSHHS")]),
 dict(t=(740, 746), al='l', lines=[
    ("La tierra de los Dámaso, al sur de Culiacán", "Ziemia rodu Dámaso, na południe od Culiacán"),
    ("Mapa base: Natural Earth / GSHHS", "Mapa: Natural Earth / GSHHS")]),
 dict(t=(840, 844), al='c', lines=[
    ("280 millones de dólares", "280 milionów dolarów"),
    ("El decomiso que pedía la fiscalía de Virginia", "Konfiskata, której żądała prokuratura w Wirginii"),
    ("Acusación del Distrito Este de Virginia, revelada en marzo de 2013", "Akt oskarżenia Okręgu Wschodniego Wirginii, ujawniony w marcu 2013")]),
 dict(t=(942, 950), al='l', lines=[
    ("La Organización de Sinaloa se parte en dos", "Organizacja z Sinaloa rozpada się na dwie części"),
    ("Mapa base: Natural Earth / GSHHS", "Mapa: Natural Earth / GSHHS")]),
 dict(t=(992, 994), al='c', lines=[
    ("«Mi compadre»", "„Mój kompadre”"),
    ("Su respuesta cuando le preguntaron quién le dijo", "Jego odpowiedź na pytanie, kto mu powiedział,"),
    ("que el Guacho había muerto", "że Guacho nie żyje"),
    ("Testimonio de Dámaso López, Nueva York, enero de 2019", "Zeznanie Dámaso Lópeza, Nowy Jork, styczeń 2019")]),
 dict(t=(1212, 1218), al='c', lines=[
    ("2 millones de dólares", "2 miliony dolarów"),
    ("El soborno que, según el Licenciado, recibió un", "Łapówka, którą według Licenciado przyjął"),
    ("alto funcionario del sistema penitenciario", "wysoki urzędnik systemu więziennictwa"),
    ("Testimonio en Nueva York; la acusación nunca ha sido probada", "Zeznanie w Nowym Jorku; oskarżenia nigdy nie udowodniono")]),
 dict(t=(1226, 1232), al='l', lines=[
    ("MAYO DE 2016", "MAJ 2016"),
    ("El Chapo es trasladado al penal federal de Ciudad Juárez", "El Chapo przeniesiony do federalnego więzienia w Ciudad Juárez"),
    ("Mapa base: Natural Earth / GSHHS", "Mapa: Natural Earth / GSHHS")]),
 dict(t=(1272, 1276), al='c', lines=[
    ("19 de enero de 2001", "19 stycznia 2001"),
    ("Fuga de Puente Grande", "Ucieczka z Puente Grande"),
    ("19 de enero de 2017", "19 stycznia 2017"),
    ("Extradición a Estados Unidos", "Ekstradycja do Stanów Zjednoczonych")]),
 dict(t=(1292, 1296), al='l', lines=[
    ("Imágenes: Departamento del Tesoro de EE. UU. (dominio público)", "Zdjęcia: Departament Skarbu USA (domena publiczna)")]),
 dict(t=(1390, 1402), al='c', lines=[
    ("72 horas", "72 godziny"),
    ("al menos 23 asesinatos en el centro de Sinaloa", "co najmniej 23 zabójstwa w centrum Sinaloa"),
    ("Febrero de 2017, según el recuento del semanario Zeta", "Luty 2017, według zestawienia tygodnika Zeta"),
    ("7 DE FEBRERO DE 2017", "7 LUTEGO 2017"),
    ("La guerra llega a Villa Juárez, en Navolato", "Wojna dociera do Villa Juárez w Navolato"),
    ("Mapa base: Natural Earth / GSHHS", "Mapa: Natural Earth / GSHHS")]),
 dict(t=(1424, 1438), al='c', lines=[
    ("«Sabemos perfectamente que hay dos", "„Doskonale wiemy, że istnieją dwie"),
    ("grupos delincuenciales con intereses", "grupy przestępcze o sprzecznych"),
    ("antagónicos»", "interesach”"),
    ("Marco Antonio Higuera Gómez, procurador de Sinaloa, febrero de 2017", "Marco Antonio Higuera Gómez, prokurator Sinaloa, luty 2017")]),
 dict(t=(1488, 1490), al='c', lines=[
    ("«Los jefes no quieren que circule nada", "„Szefowie nie chcą, żeby krążyło cokolwiek"),
    ("de lo que anda diciendo el Licenciado»", "z tego, co opowiada Licenciado”"),
    ("Joven que compraba la edición de Riodoce, citado por el semanario Zeta", "Młody człowiek kupujący numer Riodoce, cytowany przez tygodnik Zeta")]),
 dict(t=(1508, 1518), al='l', lines=[
    ("ALIANZAS", "SOJUSZE"),
    ("Según la PGR, el Licenciado buscaba aliados fuera del Cártel de Sinaloa", "Według PGR Licenciado szukał sojuszników poza Kartelem z Sinaloa"),
    ("Mapa base: Natural Earth / GSHHS", "Mapa: Natural Earth / GSHHS")]),
 dict(t=(1674, 1676), al='l', lines=[
    ("Alexandria, Virginia", "Alexandria, Wirginia"),
    ("6 DE JULIO DE 2018", "6 LIPCA 2018"),
    ("El Licenciado es extraditado a Estados Unidos", "Licenciado wydany Stanom Zjednoczonym"),
    ("Mapa base: Natural Earth / GSHHS", "Mapa: Natural Earth / GSHHS")]),
 dict(t=(1702, 1712), al='c', lines=[
    ("«Una disculpa a todo el pueblo", "„Przepraszam cały naród"),
    ("de Estados Unidos»", "Stanów Zjednoczonych”")]),
 dict(t=(1790, 1796), al='c', lines=[
    ("12 de febrero de 2019", "12 lutego 2019"),
    ("Culpable de los diez cargos", "Winny wszystkich dziesięciu zarzutów"),
    ("Veredicto del jurado contra Joaquín Guzmán Loera, Nueva York", "Werdykt ławy przysięgłych w sprawie Joaquína Guzmána Loery, Nowy Jork")]),
 dict(t=(1802, 1808), al='c', lines=[
    ("¿Ayudó en la fuga de 2001?", "Czy pomógł w ucieczce w 2001 roku?"),
    ("¿Quién ordenó matar a Javier Valdez?", "Kto zlecił zabójstwo Javiera Valdeza?"),
    ("¿Dónde está hoy?", "Gdzie jest dziś?")]),
 dict(t=(1818, 1819), al='c', lines=[
    ("Evasión de presos", "Ucieczka więźniów"),
    ("Un juez mexicano lo procesó por la fuga de", "Meksykański sędzia sądził go za ucieczkę w"),
    ("2001", "2001 roku")]),
 dict(t=(1842, 1846), al='c', lines=[
    ("Un amparo ordena reponer el proceso contra", "Sąd w trybie amparo nakazuje powtórzyć proces przeciwko"),
    ("el Chito", "El Chito")]),
 dict(t=(1876, 1884), al='c', lines=[
    ("Orden de aprehensión contra el hijo del", "Nakaz aresztowania syna Licenciado jako"),
    ("Licenciado como presunto autor intelectual", "domniemanego mocodawcy"),
    ("Caso del asesinato de Javier Valdez, según la fiscalía mexicana", "Sprawa zabójstwa Javiera Valdeza, według meksykańskiej prokuratury")]),
 dict(t=(1926, 1930), al='c', lines=[
    ("«No puedo encontrar información", "„Nie mogę znaleźć informacji"),
    ("sobre esta persona»", "o tej osobie”"),
    ("Vocero del Buró Federal de Prisiones a Univisión, octubre de 2021", "Rzecznik Federalnego Biura Więziennictwa dla Univision, październik 2021")]),
 dict(t=(1976, 1978), al='c', lines=[
    ("5 años de prisión", "5 lat więzienia"),
    ("Sentencia contra el Mini Lic, 4 de febrero de", "Wyrok na Mini Lic, 4 lutego"),
    ("2026", "2026"),
    ("Tribunal federal de Alexandria, Virginia", "Sąd federalny w Alexandrii, Wirginia")]),
 dict(t=(2094, 2098), al='c', lines=[
    ("«Al pueblo de México le pido una", "„Proszę naród meksykański o wybaczenie"),
    ("disculpa por el daño que pude haberles", "za szkody, które mogłem im"),
    ("causado»", "wyrządzić”"),
    ("Dámaso López, respuestas por escrito al diario Milenio, 2020", "Dámaso López, pisemne odpowiedzi dla dziennika Milenio, 2020")]),
]
