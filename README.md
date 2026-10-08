# Regina · Terra Regia (ARKAMIA)

Reel vertical de Terra Regia (Montesa / Dominio Cumbres) con **Regina**, personaje IA, sobre locaciones reales. Aquí solo está lo que **funcionó y se aprobó**: no hay pruebas fallidas ni descartes.

Respaldo de la carpeta de trabajo local `~/Desktop/Claude Proyectos/ARKAMIA/terra-regia-regina-genjutsu/`.

## Estructura

| Carpeta | Contenido |
|---|---|
| `personaje/` | Perfil oficial de Regina: la hoja gris de 3 paneles FINAL (con cara y sin cara en el cuerpo) y sus prompts. En `outfit_coffee_date/` está el outfit alterno (camisa de lino verde salvia + pantalón crema), con sus dos hojas |
| `fondos/` | Fotos reales de las locaciones: showroom (03 lounge, 07 ventanal, 08 mesa de mapas, 09 agente, 11 sala), la elipse y el pórtico Montessa con sol frontal dorado |
| `scripts/` | El pipeline completo: limpieza del chroma, generación, piel, cámara en mano, sincronía de labios |
| `tomas/tomaN/` | Cada toma aprobada: salida cruda de Genjutsu, material intermedio, el script que la arma y un `LEEME.txt` con la receta exacta |
| `previas/` | Las previas aprobadas (los SI) y el reel final |
| `reel_final/` | Los scripts del reel final aprobado |
| `referencias-estilo/` | Cuadros clave del estilo @kelssie3 + el estilo "regio" del amigo |

## Tomas

| Toma | Locación | Receta |
|---|---|---|
| 1 | Showroom, lounge + frase de la pared | Genjutsu 480p → upscale 1080p (1 crédito) → sincronía → `frase.py` → punch-in |
| 2 | Pórtico Montessa, plano medio, golden hour | Genjutsu 720p con la hoja sola (`SOLO_HOJA=1`, `MEDIO=1`) → `piel_golden.py` → `handheld.py` |
| 3 | Drone del lote | `reel3d.py`: 127 m², casas de lujo construyéndose y el pin 3D sobre Monterrey |
| 4 | Showroom, mesa de mapas | Genjutsu 720p con la hoja sola → `sync_toma.py`; en el reel final, sin el hombre de traje (`reel_final/quitar_hombre.py`) |
| 5 | Elipse, plano americano, **sin gimbal** | Genjutsu 720p sobre `elipse_L3.jpg` → `sync_toma.py` escalando con lanczos desde la salida cruda (nunca con upscale de IA) |
| 6 | Drone del parque con casas de lujo construyéndose | DJI horizontal → Nano Banana Pro (terminadas + obra negra) → `derecho.py 12.5` → `toma6L.py` (ventana 9:16, tramo central) |
| 7 | Showroom, agente con la pareja (financiamiento) | Nano Banana Pro (showroom 09 + logo) → `logo_camisa.py` → Kling 3.0 Pro → `logo_track.py` |
| 8 | Casa club, luz natural, cámara a ras de piso | Nano Banana Pro (Regina dentro de la foto) → fondo vacío → Genjutsu cuerpo completo → `piso_limpio.py` |
| 9 | Showroom 07, ventanal | La misma receta que la toma 8, sobre el showroom 07 |

Cada carpeta `tomas/tomaN/` trae su `LEEME.txt` con la receta exacta y lo que se descartó.

## Reel final (aprobado 2026-10-07)

`previas/REEL_FINAL_terra-regia_regina_kelssie.mp4`: 43 s a 1080×1920, con las tomas 1–9 más el cierre con el logo animado sobre el verde de marca `#19815C`. Los scripts están en `reel_final/` y la receta en `reel_final/LEEME.txt`:
- `render.py` arma el reel con la edición estilo Kelssie y `logo_final.py` hace el cierre.
- `quitar_hombre.py` saca al hombre de traje de la toma 4.
- `audio.py` mezcla la voz aislada con ElevenLabs (sin reverberación), ecualizada y comprimida: `VOZ=voz_limpia.wav python3 audio.py`.

**Pendiente:** confirmar el dominio "terraregia.com". Las tomas de Regina son de 720p (la toma 1, de 480p) escaladas con lanczos; Liz decidió no regenerarlas a 1080p porque costaría 308 créditos.

`previas/tomas-fondos-anteriores/` guarda las tomas aprobadas el 2026-10-01 con los fondos de la primera ronda.

## Reglas firmes

- **Identidad:** solo la hoja gris FINAL con cara (`SOLO_HOJA=1`), sin el retrato viejo. Cara angosta y alargada, piel clara oliva con pecas: no ensanchar ni broncear.
- **Cabello siempre suelto**, lacio y con raya al centro, cayendo al frente. El prompt lo exige: "worn DOWN… NOT tied".
- **Vestuario íntegro:** top crema off-shoulder, pantalón negro de pierna ancha hasta el zapato (sin puños), stilettos negros. Genjutsu copia la ropa del chroma, así que SIEMPRE hay que pasar antes `fix_wardrobe.py`; el prompt solo no basta.
- **ARRI siempre en el prompt** (Alexa 35, Signature Prime 50 mm T2), sin acabado de grano por código.
- **Sincronía de labios:** Genjutsu no comprime el tiempo, corta el final. Hay que medir la boca con `bocaabierta.swift` (Vision) en la fuente y en la salida, y retimear con `sync_toma.py`, que busca solo el K y el offset.
- **Audio:** la voz es la del chroma original. Los SFX de Ocular Sounds van en una pista aparte (no se incluyen aquí, ver abajo), y siempre se puede entregar una versión solo con narración.
- **Textos en el drone:** planos en pantalla, no en perspectiva sobre el terreno.
- **Escalado:** en tomas con piel en primer plano se escala con lanczos desde la salida cruda de Genjutsu. El upscale de IA (bytedance, aigc) mancha la piel.
- **Cotizar antes de generar.** Genjutsu cuesta 56 créditos por toma a 720p y 12–24 a 480p. Para conservar una toma aprobada se escala esa misma; no se regenera.

## Pipeline de una toma nueva

```bash
cd scripts
python3 clean.py  in.mp4 cleanN.mp4             # verde parejo
python3 fix_wardrobe.py cleanN.mp4 cleanNw.mp4  # sin micrófono ni puños (MEDIO=1 para plano medio)
higgsfield upload create cleanNw.mp4            # agregar "cleanNw <id>" a uploads.txt
SHEET=5d827bb9-21ab-4ca7-a2f9-3f1b4c726d5d SOLO_HOJA=1 BG=<fondo> python3 run_batch.py 720p N
swiftc bocaabierta.swift -o bocaabierta
./bocaabierta cleanNw.mp4 > src.txt; ./bocaabierta gen_720p_tomaN.mp4 > gen.txt
python3 sync_toma.py gen_720p_tomaN.mp4 src.txt gen.txt tomaN_original_con_voz.mp4 previa_tomaN_720p.mp4
```

Fondos en `run_batch.py`: 1 = lounge, 2 = mesa de mapas, 3 = sala con maqueta, 4–6 = pórtico Montessa. Los upload IDs de Higgsfield pueden caducar; si fallan, vuelve a subir el archivo.

## Fuera del repositorio

- **Los SFX de Ocular Sounds** (whoosh, whip, stone, maps): tienen licencia de librería y viven solo en el equipo local, en `aprobados/toma3/sfx_ocular/`.
- **El chroma 4K original** de la modelo: está en el Seagate (`Respaldo Marcas/ARKAMIA/TERRA REGIA/Videos Regina/`).

## Edición estilo Kelssie (aprobada 2026-10-06)

`edicion_kelssie/render.py` + `audio.py` unen las tomas en el reel con el estilo de @kelssie3:
- Títulos detrás de la cabeza y par Light+Bold palabra por palabra.
- Palabra clave en degradado pastel y píldoras de vidrio.
- Punch-ins, y whip con speed ramp en cada corte.

La prueba con las tomas 1–5 está en `previas/reel_terra-regia_estilo-kelssie_v1.mp4`. Para clips nuevos, se agregan a `SEG` en `render.py`.
