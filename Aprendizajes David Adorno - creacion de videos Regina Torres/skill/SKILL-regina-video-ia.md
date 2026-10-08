---
name: regina-video-ia
description: Produce un video vertical (reel 9:16, 40-50 s) de un desarrollo de Terra Regia presentado por el avatar Regina Torres sobre la actuación real de una talento en croma (Barbara Morales). Receta v2 (8-oct-2026) = la de Javier (reel Montessa, David le dio 9.5 vs 7 de Castelo): croma ORIGINAL 4K limpio (clean.py + fix_wardrobe.py) → Genjutsu `hf_mult_motion_control` 720p con la hoja gris de 3 paneles + foto (o render fotorrealizado) de la locación → sincronía por la boca real (bocaabierta.swift + sync_toma24.py, voz ORIGINAL de Barbara, sin lipsync IA) → cámara en mano → montaje Kelssie. Todo a 720p. Triggers - "video de Regina", "video IA de Terra Regia", "video de Alboradas/Alinka/Veralia/Montessa/Rincón/Castelo", "avatar sobre actuación real", "character swap de Barbara", "reel estilo Kelsie", "siguiente video de Regina".
---

# regina-video-ia (v2 · receta de Javier)

Referencias: repo de Javier `adornodavid/regina_torres_arkamia_JG` (README + `tomas/tomaN/LEEME.txt`, la fuente de verdad de la receta) · repo de trabajo del proyecto en curso `~/Proyectos/tr-regina-alboradas/` (scripts de Javier en `scripts/`, adaptados a `ffmpeg` del sistema) · herramientas viejas de montaje en `~/Proyectos/tr-regina-castelo/tools/` (subs_v2, music_bed, reframe, silencecut; correr con su `.venv`, que trae cv2/numpy). Medios en Drive `Clientes/Externos/Terra Regia/Terra Regia - Regina Torres Videos IA/`. Memoria: `TR-REGINA-VIDEOS-IA`.

## Principio
Barbara actúa; Regina presta la cara. El cuerpo, las manos y la boca son los de Barbara 1:1: **lo que ella no actúa, Regina no lo hace.** Si David ve gestos tiesos, la causa es el croma (dirigir más gesto en la grabación), no el motor. Nunca pedirle al modelo «más gestos»: inventa y rompe la naturalidad.

## 🔒 Identidad (David, 8-oct-2026)
La cara oficial es la de la **hoja gris de 3 paneles de Javier** (cara angosta y alargada, pómulos altos, pecas, cejas gruesas rectas, cabello largo lacio con raya al centro, argollas de oro). Viene de la ficha original del 24-sep: `01 Ficha Regina Torres/ficha-original-24sep/` (5 vistas, macro de ojos, 12 expresiones). Reemplaza al LOCK «óvalo redondo» del 5-oct.
- **Por proyecto se cambia solo el outfit:** se genera una hoja nueva con Nano Banana Pro (Magnific `mode=imagen-nano-banana-2`, 16:9, 75 cr) pasando la hoja de Javier + `04-rostro-primer-plano.png` + `02-ojos-macro.png` y «ONLY CHANGE THE WARDROBE». David aprueba la hoja antes de animar.
- **En Genjutsu entra SOLO la hoja** (más referencias = la cara cambia entre tomas).
- Outfits: Montessa = top crema off-shoulder + pantalón negro (Javier) · Alboradas = blusa champagne satín SIN mangas + pantalón camel + cinturón café (`~/Proyectos/tr-regina-alboradas/personaje/regina_hoja_outfitB_APROBADA.png`). Barbara trae manga corta y aun así Genjutsu respetó «sleeveless» con el prompt explícito.

## 0. Antes de gastar un crédito
- **Todo a 720p** (regla de David 8-oct). Genjutsu 720p ≈ 42 cr Higgsfield por toma (~6 s); 480p para pruebas. Nunca 1080p salvo pedido explícito.
- `mcp__claude_ai_Higgsfield__balance` y `mcp__magnific__account_balance`. Cotizar con `generate_video … get_cost:true`. Video completo ≈ 5 tomas × 42 = ~210 Higgsfield + ~1,500 Magnific de fondos.
- **Crudo = el ORIGINAL 4K** del croma (no WhatsApp: con 478×850 ningún motor da cara ni labios). Si llega comprimido, pedir el original.
- **Storyboard aprobado antes de la primera toma** y **una toma al 100 % antes de abrir la siguiente.**

## 1. Insumos
| Qué | Cómo |
|---|---|
| Crudo 4K (tomas separadas por negro) | `ffmpeg -vf blackdetect=d=0.2:pix_th=0.1` para los cortes; transcribir con ElevenLabs scribe (`timestamps_granularity=word`, llave `~/.config/arkamia/elevenlabs.env`) para saber qué línea es cada toma y detectar repeticiones. Cortar con **`ffmpeg -nostdin`** (dentro de un `while read` sin `-nostdin` ffmpeg se come el heredoc) a 1080×1920 30 fps → `tomas/Tn.mp4`. |
| Toma repetida | Elegir VIENDO una tira de cuadros (gestos abiertos, sin intrusos a cuadro); la métrica de diferencia entre cuadros engaña. |
| Fondos | Foto real de la locación si existe (showroom TR: `02 Referencias/showroom-oficinas-TR/`). Si solo hay renders: **fotorrealizar** con Nano Banana Pro 9:16 `count=2` («Turn this architectural render into a real vertical photograph… keep its architecture… camera at chest/waist height… lower half empty paving where a person could stand… no people… 5 pm natural light, sun front-left behind camera… Sony A7 IV, no CGI look»). Elegir la que deje el piso libre al centro. |
| Dron | DJI reales del proyecto; revisar rotación con ffprobe (de Alboradas: 0045 vertical, 0046 16:9 → `reframe.py pan`). |

## 2. Tomas de Regina — por toma
1. **Encuadre en el croma:** Genjutsu respeta el encuadre del video fuente. Cuerpo entero = la toma tal cual. **Plano americano** (preferido para que se lean las manos) = recortar desde el 4K: `crop=1124:2000:518:760` (ajustar a la toma; manos dentro de cuadro en sus extremos) → 1080×1920.
2. **Limpieza** (`scripts/`, con `~/Proyectos/tr-regina-castelo/.venv/bin/python`): `clean.py in out` (verde parejo, despill, sin cintas; `MEDIO=1` en americano) → `fix_wardrobe.py in out` (borra el micrófono de solapa, oscurece los puños claros y alarga el pantalón; `MEDIO=1`). Revisar un cuadro antes/después.
3. **Subir a Higgsfield** (el CLI `higgsfield` pierde la sesión; usar el conector): `media_upload` → `curl -X PUT -H "Content-Type: …" -H "If-None-Match: *" --data-binary @archivo '<upload_url>'` → `media_confirm`. Ids valen 24 h.
4. **Genjutsu:** `generate_video {model:"hf_mult_motion_control", resolution:"720p", medias:[{role:"video_references", value:<croma limpio>}, {role:"image_references", value:<hoja>}, {role:"image_references", value:<fondo>}], prompt}`. Si responde con `preset_recommendation`, repetir con `declined_preset_id`. Prompt = bloques de Javier (`scripts/run_batch.py`): PERSONA (identidad + outfit exacto + cabello SUELTO + «no microphone» + «performs exactly the same body motion… at the same position and size in frame» + encuadre) · LUGAR (la foto «exactly… no reframing, no redesign», dónde pisa, luz de la foto con dirección del sol, sombra de contacto, piel MATE con poros, «no golden glow, no rim-light halo») · LOOK ARRI Alexa 35 + Signature Prime 50 mm T2 · CIERRE («static locked-off camera… Absolutely no text»). Tarda ~6-8 min; `jobs_wait` cada 15 s.
5. **Sincronía por la boca real:** `swiftc -O scripts/bocaabierta.swift -o scripts/bocaabierta` (una vez) → medir croma limpio y salida → `python scripts/sync_toma24.py gen.mp4 src.txt gen.txt tomas/Tn.mp4 sync.mp4` (busca K y offset; **corr ≥ 0.75**; toma 1 de Alboradas dio 0.85). `sync_toma24` sale a los 24 fps de Genjutsu con el cuadro más cercano: **no mezcla cuadros** (el `sync_toma.py` original a 30 fps los fundía y las manos se veían blandas/tiesas). Audio = voz original de la toma.
6. **Acabado:** `handheld.py sync.mp4 out.mp4 7` (deriva de cámara en mano con overscan). Si la piel brilla: `piel_golden.py` (necesita mattes por cuadro; `NOWARM=1` si la toma ya es cálida). Escalar SIEMPRE con lanczos, nunca con upscale de IA (mancha la piel).
7. **QA y entrega de la toma:** tira de 6 cuadros + recorte de cara; comparar contra la hoja. Copiar a Drive `06 Finales/<proyecto>-v1/` y `open -a "QuickTime Player"`. Esperar aprobación.

Plan B (solo si Genjutsu falla en una toma): Kling 3.0 Motion Control + Lipsync 2.0 en recorte (receta de Castelo en el PLAYBOOK; ~2,000 cr Magnific por toma). Descartados: OmniHuman, Genjutsu `replace_object` (agranda el cuadro), Seedance `video_modify`, Aleph 2, LatentSync, Veed Fabric, upscale de IA sobre piel.

## 3. B-roll (regla de David: sobre el DRON REAL, nunca sobre un render 3D)
- **Obra viva:** cuadro real del dron → Kling 3.0 PRO 5 s vía Higgsfield (7.5 cr): «several excavators, bulldozers, dump trucks… steady flow of cars on the road… real DJI drone footage». Std (6.25 cr) sale con muy poca actividad.
- **Lote:** `alboradas/broll/lote_t3.py` — homografía SIFT al cuadro de referencia, contorno que se dibuja y textos planos sincronizados a la voz.
- **Casas construyéndose:** cuadro real del dron → Nano Banana «finished high-end San Pedro homes, each different… real aerial photograph… no CGI/toy look, no construction vehicles» (escoger la que respete escala y monte) → Kling 3.0 PRO start→end «real-estate construction timelapse… no vehicles, no cranes». ❌ Sobre el render máster aéreo salió «caricatura» (camiones de juguete, casas iguales).
- **Plano de lotes / conteo:** render de lotificación + `alboradas/broll/lotes_t7.py` (ola de lotes y contador; máscara por contorno convexo para no perder bloques).
- Renders de amenidades solo **fotorrealizados** como fondo de Regina; el dron real 16:9 se pasa a 9:16 con `tr-regina-castelo/tools/reframe.py pan|fixed`.
- Letrero confuso en un render (p.ej. «LUCERNA»): `alboradas/scripts/letrero_patch.py` (Nano Banana sobre un recorte del cuadro + pegado con protección de lo que se mueve).

## 4. Audio
- Voz = la original del croma, limpia (ElevenLabs voice isolation si hay reverberación) + EQ y compresión. Sin clon salvo línea faltante (avisar).
- SFX en cada corte (whoosh/whip; pop en píldoras), música baja (~0.13), `loudnorm=I=-14:TP=-1.5:LRA=11` (Javier `reel_final/audio.py`). Siempre poder entregar versión solo con narración.

## 5. Montaje estilo Kelssie (`videos-ia/alboradas/edicion/`)
`render.py` = `render_head.py` + `seg_<proyecto>.py` + `render_tail.py` (render de Javier con **LazyFrames**: el original carga ~9 GB y revienta 8 GB de RAM). Insumos por toma: `sN.mp4` 1080×1920 30 fps, y en las de Regina `faceN.txt` (`facebox.swift`) y `matteN/` (`personmatte.swift`).
- Subtítulo palabra por palabra al pecho: Light chico + Bold grande, acento en degradado de la paleta del proyecto (Alboradas: crema→durazno→terracota), `ink='dark'` en fondos claros.
- 🔤 **Palabra de acento grande DEBAJO del subtítulo, en las piernas** (`title_y`≈0.745), por delante de Regina — **nunca en la cabeza** (David 8-oct). Si el acento es la primera palabra de la frase («Agenda»), va dentro del subtítulo.
- Etiquetas de vidrio (amenidades) a los lados, a la altura de hombros, que no tapen manos ni cara.
- CTA: estilo `'y'` = **autocompletar** «terraregia.com» sincronizado con el gesto de apertura/señalamiento de Barbara.
- Punch-in en palabras clave, whip con speed ramp en cada corte, cierre `logo_tr.py` (logo TR sobre `#19815C`).
- `audio.py`: voz original por toma + whoosh/whip en cortes + pop por etiqueta + tecleo + música baja (0.11) que sube en el cierre + `loudnorm` −14 LUFS. SFX con ElevenLabs sound-generation.

## 6. QA y entrega
- Hoja de contacto, `volumedetect`, revisar cada frase de subtítulos.
- Entregar a 720p (master) + hoja en Drive `06 Finales/<proyecto>-vN/`; abrir en QuickTime.
- Commit en el repo del proyecto (medios ignorados). Actualizar memoria `TR-REGINA-VIDEOS-IA`.

## Errores que ya costaron un demo
Croma de WhatsApp · lipsync IA sobre la boca real · varias referencias de cara en Genjutsu · probar `replace_object` y concluir que «Genjutsu no sirve» · `sync_toma` mezclando cuadros (manos blandas) · ffmpeg sin `-nostdin` en un `while read` · tarjetas sobre la cara · subtítulos claros sobre ropa clara · zsh no divide `$VAR` en `for` (usar `${=VAR}`) · el CLI `higgsfield` con sesión vencida (usar el conector).
