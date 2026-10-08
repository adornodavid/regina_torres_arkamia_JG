# Aprendizaje · Reel ALBORADAS (8-oct-2026) — receta v2 de Regina

> **Estado:** video **abierto**. La **v2** («acentos abajo») es la mejor versión hasta ahora. Faltan los ajustes finales de David.
> Drive: `06 Finales/alboradas-v1/REEL ALBORADAS v2 - acentos abajo.mp4` (+ ligero 720p). Repo de trabajo local: `~/Proyectos/tr-regina-alboradas/` (copia de scripts en `videos-ia/alboradas/`).

## 1. Por qué cambiamos de receta

David calificó **Castelo con un 7** y el reel de **Javier (Montessa) con un 9.5**: movimiento, cara, naturalidad, voz, subtítulos, lipsync y gestos. Estudiamos su repo (`adornodavid/regina_torres_arkamia_JG`) y adoptamos su receta. Las diferencias de fondo:

| | Castelo (nosotros, 5-oct) | Javier / Alboradas (8-oct) |
|---|---|---|
| Crudo | WhatsApp 478×850 | **Croma ORIGINAL 4K** |
| Motor de Regina | Still Nano Banana → Kling 3.0 Motion Control | **Genjutsu `hf_mult_motion_control`** (persona + fondo en una pasada) |
| Labios | Lipsync 2.0 en recorte (~2,000 cr Magnific/toma) | **Ninguna IA de labios**: boca real de Barbara, solo se ajusta el tiempo (`bocaabierta.swift` + `sync_toma24.py`) |
| Voz | Original + clon para huecos | **Original de Barbara**, siempre |
| Identidad | Varias referencias de cara | **Solo la hoja gris de 3 paneles** |
| Fondos | Renders tal cual | **Foto real** (showroom) o **render fotorrealizado** con Nano Banana |
| Regina a cuadro | 3 tomas, encuadre repetido | **5 tomas**, locaciones distintas, plano americano |
| B-roll | Renders + Kling 2.5 (325 cr Magnific/5 s) | **Dron real** + gráficos rastreados + Kling 3.0 (6–8 cr Higgsfield/5 s) |
| Costo por video | ≈11,500 cr Magnific | ≈240 Higgsfield + ≈1,800 Magnific |

**Error de diagnóstico corregido:** en Castelo «descartamos Genjutsu» porque probamos `hf_mult_replace_object` (agranda el cuadro). El que funciona es **`hf_mult_motion_control`**.

## 2. Reglas de David (nuevas, 8-oct)

1. **Todo a 720p.** No se gastan créditos en 1080p. Las tomas se escalan con lanczos (nunca upscale de IA, mancha la piel).
2. **Identidad = la hoja de Javier** (cara angosta y alargada, pecas, cejas rectas gruesas). Viene de la ficha original del 24-sep (`ficha-original-24sep/` en Drive). Por proyecto solo cambia el outfit. **Alboradas = blusa champagne satinada sin mangas + pantalón camel + cinturón café.**
3. **La esencia es el realismo físico**: luz de la foto con su sombra, pliegues de la ropa, viento en las plantas, piel mate. «No pierdas esta esencia».
4. **Una toma aprobada al 100 % antes de abrir la siguiente.**
5. **El movimiento sale del croma.** Si Regina se ve tiesa es porque Barbara gesticula poco. No se le pide a la IA «más gestos». Se elige la toma repetida con más gesto (viéndola, no por métrica) y se usa **plano americano** para que las manos se lean.
6. **B-roll de construcción sobre el DRON REAL, nunca sobre un render 3D.** La toma 6a v1 (render máster aéreo) se rechazó: «caricatura», camiones amarillos de juguete y casas iguales tipo cajas.
7. **Letreros:** si un render trae un nombre que confunde (el pórtico decía «LUCERNA»), se cambia a **ALBORADAS** sin regenerar (`letrero_patch.py`).
8. **CTA:** en la toma 8, «terraregia.com» se **autocompleta** letra por letra justo cuando Barbara abre y señala con las manos (2.21–3.25 s).
9. **Subtítulos:** la palabra de acento grande va **DEBAJO del subtítulo, entre las piernas**, nunca detrás ni encima de la cabeza. Si la palabra de acento es la primera de la frase («Agenda»), va dentro del subtítulo para no invertir el orden de lectura.

## 3. Receta por toma de Regina (aprobada 5 de 5)

```
crudo 4K ── cortar por negros (ffmpeg -nostdin, 1080×1920 30 fps)
   └─ plano americano: crop=1240:2204:460:700 sobre el 4K (manos dentro de cuadro)
clean.py (MEDIO=1) ── fix_wardrobe.py (MEDIO=1) ── quita mic de solapa y puños
Higgsfield (conector): media_upload → curl PUT (Content-Type + If-None-Match: *) → media_confirm
Genjutsu hf_mult_motion_control 720p (≈42 cr)  medias: video_references=croma, image_references=hoja + fondo
   └─ si responde preset_recommendation → repetir con declined_preset_id
bocaabierta (Vision) en croma y salida → sync_toma24.py (corr ≥ 0.75; logramos 0.85–0.93)
handheld.py (cámara en mano sutil) → previa 720p a Drive → aprobación
```

Prompt = bloques de Javier: **PERSONA** (identidad + outfit exacto + «SLEEVELESS… no sleeves» + cabello suelto + «no microphone» + «same position and size in frame» + encuadre) · **LUGAR** (la foto «exactly… no reframing», dónde pisa, luz con dirección del sol, sombra de contacto, piel MATE, «no golden glow, no rim-light halo», vida: brisa) · **LOOK** ARRI Alexa 35 + Signature Prime 50 mm T2 · **CIERRE** («static locked-off camera… no text»).

| Toma | Línea | Fondo | corr. boca |
|---|---|---|---|
| 1 | Hay terrenos que compras… | Pórtico (render fotorrealizado) + letrero ALBORADAS | 0.85 |
| 4 | Espacio suficiente… jardín | Parque central zona zen (render fotorrealizado) | 0.933 |
| 5 | Además, tienes alberca… | Casa Club Solaria (render fotorrealizado) | 0.868 |
| 6b | O comprar tierra hoy… patrimonio | Showroom TR foto 06 (monograma + maqueta) | 0.894 |
| 8 | Agenda tu visita… terraregia.com | Showroom TR foto 02 (sala) | 0.923 |

**Hallazgo técnico:** el `sync_toma.py` original fundía cuadros vecinos para pasar de 24 a 30 fps y las manos se veían blandas («tiesas»). `sync_toma24.py` sale a los 24 fps de Genjutsu con el cuadro más cercano.

## 4. B-roll

| Toma | Qué es | Cómo | Costo |
|---|---|---|---|
| 2 | Obra viva: excavadoras, bulldozer, camiones y tráfico | Cuadro real del dron → **Kling 3.0 PRO** 5 s (Higgsfield) | 7.5 cr |
| 3 | Lote 10 × 20 dibujado sobre la terracería real | `broll/lote_t3.py`: homografía SIFT al cuadro de referencia, contorno que se dibuja, «200 m²», «10 m de frente», «20 m de fondo» sincronizados con la voz | 0 |
| 6a | Casas construyéndose | Cuadro real del dron → Nano Banana «finished high-end San Pedro homes, each different, real aerial photo, no CGI/toy look, no construction vehicles» → **Kling 3.0 PRO start→end** «real-estate construction timelapse… no vehicles, no cranes» | 150 Magnific + 7.5 |
| 7 | 319 terrenos | Render «Máster aéreo» (lotificación real) con paneo, ola de lotes encendidos desde el acceso y contador (`broll/lotes_t7.py`, máscara por contorno convexo para no perder bloques) | 0 |

Kling 3.0 vía Higgsfield cuesta **6.25 (std) / 7.5 (pro) cr por 5 s**, contra 325 cr Magnific de Kling 2.5 en Castelo.

## 5. Montaje (estilo Kelssie, `edicion/`)

- `render.py` = `render_head.py` + `seg_alboradas.py` + `render_tail.py`. Es el `render.py` de Javier con cambios:
  - **`LazyFrames`**: el original carga todos los cuadros en memoria (~9 GB a 1080p) y revienta una Mac de 8 GB. Ahora lee bajo demanda (~360 MB).
  - Helvetica Neue (Light/Bold/Medium) en vez de SF Pro.
  - Degradado de acento **crema → durazno → terracota** (paleta Alboradas). Tinta oscura opcional por toma (`ink='dark'`) para fondos claros.
  - Estilo `'y'` = **autocompletar** letra por letra (terraregia.com).
  - Títulos de acento **por delante y abajo** (`title_y` ≈ 0.745·H), ya no recortados por la silueta detrás de la cabeza.
- `facebox.swift` (cara por cuadro, Vision) y `personmatte.swift` (silueta) para cada toma de Regina.
- `audio.py`: voz original por toma, whoosh/whip alternados en cada corte, pop por amenidad, tecleo en terraregia.com, afro-house de Castelo a 0.11 que sube en el cierre, `loudnorm` → **−14.2 LUFS**.
- `logo_tr.py`: cierre con el logo de Terra Regia animado sobre el verde de marca `#19815C` (de Javier).
- SFX generados con ElevenLabs sound-generation (`sfx/`).

## 6. Lo que se rechazó y por qué

- **Toma 6a v1** sobre el render máster aéreo: aspecto de maqueta, camiones de juguete, casas idénticas.
- **Acentos en la cabeza** (v1): tapaban la cara; David los quiere abajo.
- **Outfits A/C/D**: David eligió la B (champagne + camel) aunque la D era la paleta exacta del brochure.
- **LUCERNA** en el pórtico: confunde; se cambió a ALBORADAS.

## 7. Pendiente (video abierto)

- Feedback final de David sobre la v2.
- Música propia de Alboradas (hoy usa la de Castelo).
- Versión solo con narración (sin música) si Terra Regia la pide.
- Integrar el clasificador de tinta por palabra de Castelo (`subs_v2.py`) al render Kelssie.
