# Aprendizajes David Adorno · creación de videos de Regina Torres

**Para Javier.** Esta carpeta junta lo que aprendimos al producir el reel de **Alboradas Residencial** (8-oct-2026) partiendo de tu receta de Montessa, y lo que agregamos o mejoramos encima de ella. Todo lo que funcionó en Alboradas salió de tu trabajo. Aquí está lo que tomamos de ti tal cual, lo que cambiamos y por qué, y las reglas que David fijó en el camino.

Contexto: David calificó nuestro primer reel (Castelo, receta propia con Kling Motion Control + Lipsync 2.0) con un **7** y tu reel de Montessa con un **9.5** por movimiento, cara, naturalidad, voz, subtítulos, lipsync y gestos. Por eso adoptamos tu receta completa. La mejor versión de Alboradas hasta ahora es la **v2** (46 s). La v3 (con tu `acabado_video.py` de Amaral) se rechazó por perder nitidez.

| Carpeta | Qué hay |
|---|---|
| `scripts/` | `sync_toma24.py` (sincronía sin mezclar cuadros) y `letrero_patch.py` (cambiar un letrero en una toma de cámara fija) |
| `broll/` | `lote_t3.py` (lote 10 × 20 rastreado sobre el dron real) y `lotes_t7.py` (ola de lotes + contador sobre el máster aéreo) |
| `edicion/` | Tu `render.py` Kelssie con nuestras modificaciones (`render_head.py` + `seg_alboradas.py` + `render_tail.py`), `audio.py`, `logo_tr.py` (tu logo_final con el logo blanco de TR) y `facebox.swift` |
| `skill/` | La skill de Claude Code `regina-video-ia` v2 (la receta completa como instrucciones para el agente) |
| `referencias/` | Documento largo del proyecto, hoja del outfit de Alboradas, hoja de cuadros del reel y ejemplo de acentos abajo |

---

## 1. Lo que tomamos de tu receta tal cual (y funcionó)

1. **Croma original 4K**, nunca reenviado por WhatsApp. Nuestro Castelo partía de un 478×850 y ningún motor da cara ni labios con eso.
2. `clean.py` + `fix_wardrobe.py` antes de generar (quitan el micrófono de solapa y los puños claros).
3. **Genjutsu `hf_mult_motion_control`**: persona y fondo en una pasada. Nosotros habíamos descartado Genjutsu porque probamos `hf_mult_replace_object`, que agranda el cuadro. Era el modo equivocado.
4. **Solo la hoja gris de 3 paneles** como identidad. David adoptó tu cara (angosta, pecas, cejas rectas) como la oficial de Regina.
5. **Sin IA de labios**: boca real de Barbara + `bocaabierta.swift` + retimeo con K y offset. Logramos correlación de **0.85 a 0.93** en las 5 tomas.
6. **Voz original de Barbara** en todo el video.
7. Tus prompts por bloques: PERSONA, LUGAR (luz de la foto, sombra de contacto, piel mate, «no glow, no halo»), LOOK ARRI Alexa 35 + Signature Prime 50 mm T2 y CIERRE (cámara fija, sin texto).
8. `handheld.py`, escalado con lanczos (nunca upscale de IA) y el montaje Kelssie: whips con speed ramp, punch-ins, píldoras de vidrio, SFX en cada corte, música baja y `loudnorm` −14.
9. El cierre con el logo animado sobre el verde de marca `#19815C`.

## 2. Reglas que fijó David en Alboradas

1. **Todo a 720p.** Ningún crédito en 1080p; se escala con lanczos.
2. **La esencia es el realismo físico**: la luz de la foto con su sombra, los pliegues de la ropa, el viento en las plantas y la piel mate. «No pierdas esta esencia».
3. **Una toma aprobada al 100 % antes de abrir la siguiente.**
4. **El movimiento sale del croma.** Si Regina se ve tiesa es porque Barbara gesticuló poco. Nunca pedirle al modelo «más gestos». Se elige la toma repetida con más gesto **viéndola** (la métrica de diferencia entre cuadros engañó) y se prefiere el **plano americano** para que las manos se lean.
5. **El B-roll de construcción va sobre el dron real, nunca sobre un render 3D.** Un timelapse hecho sobre el render del máster aéreo se rechazó: «caricatura», camiones amarillos de juguete y casas iguales tipo cajas.
6. **Letreros que confunden se corrigen** sin regenerar: el render del pórtico decía «LUCERNA» (nombre de una privada) y se cambió a «ALBORADAS».
7. **CTA: «terraregia.com» se autocompleta** letra por letra justo cuando Barbara abre y señala con las manos.
8. **La palabra de acento grande va DEBAJO del subtítulo, entre las piernas**, nunca detrás ni encima de la cabeza («no me gusta que uses tanto la altura de su cabeza»). Ejemplo: «y otros pensando / en tu» y abajo, grande, **futuro**. Si el acento es la primera palabra de la frase («Agenda»), va dentro del subtítulo para no invertir el orden de lectura. **Esta es la regla en la que más nos separamos de tu edición de Montessa y de Amaral.**

## 3. Lo que agregamos o mejoramos

| Mejora | Problema que resuelve | Archivo |
|---|---|---|
| **Sincronía a 24 fps sin mezclar cuadros** | `sync_toma.py` saca 30 fps fundiendo cuadros vecinos de Genjutsu (24 fps); las manos se ven blandas y David las sintió «tiesas». `sync_toma24.py` usa el cuadro más cercano. | `scripts/sync_toma24.py` |
| **Plano americano desde el 4K** | De cuerpo entero la cara mide ~60 px a 720p y los gestos se pierden. Recortando el croma 4K (`crop=1240:2204:460:700`) antes de Genjutsu, la correlación de boca subió a 0.89–0.93. | (paso de preparación) |
| **Renders → foto real** | Cuando no hay foto de la locación, Nano Banana Pro «Turn this architectural render into a real vertical photograph… lower half empty paving where a person could stand… Sony A7 IV, no CGI look» (2 variantes, elegir la que deja el piso libre al centro). | (prompt en el documento largo) |
| **Cambio de letrero sin regenerar** | Nano Banana edita solo las letras sobre un recorte del cuadro y el parche se pega en todos los cuadros respetando lo que pasa por encima (diferencia contra el cuadro 0). | `scripts/letrero_patch.py` |
| **Lote rastreado** | Lote 10 × 20 pegado al terreno real por homografía SIFT, contorno que se dibuja y textos planos sincronizados con la voz. | `broll/lote_t3.py` |
| **Ola de lotes + contador** | Lotes que se encienden en ola desde el acceso y contador hasta 319 sobre el render de lotificación (máscara por contorno convexo para no perder bloques con otro verde). | `broll/lotes_t7.py` |
| **Kling 3.0 por Higgsfield** | 6.25 cr (std) / 7.5 cr (pro) por 5 s. Obra viva sobre el dron real y casas construyéndose con start→end (dron real → Nano Banana con casas de San Pedro distintas entre sí, «no vehicles, no cranes»). | (prompts en el documento largo) |
| **`render.py` que cabe en 8 GB de RAM** | El original carga todos los cuadros (~9 GB a 1080p). `LazyFrames` los lee bajo demanda (~360 MB). | `edicion/render_tail.py` |
| **Autocompletar** | Estilo `'y'`: escribe el texto letra por letra durante 0.9 s. | `edicion/render_tail.py` |
| **Acentos abajo y por delante** | `title_y` ≈ 0.745·H, cap ~165 px, sin recortar con la silueta. | `edicion/render_tail.py` |
| **Tinta oscura por toma** | `ink='dark'` para fondos claros (pared del showroom). | `edicion/render_head.py` |
| **Paleta por proyecto** | Degradado del acento crema → durazno → terracota (Alboradas). Helvetica Neue si no está SF Pro. | `edicion/render_head.py` |
| **Audio** | Voz original por toma + whoosh/whip alternados + pop por píldora + tecleo en el autocompletar + música a 0.11 que sube al terminar la última frase (regla de David desde Castelo). SFX generados con ElevenLabs sound-generation. | `edicion/audio.py` |
| **Cara por cuadro** | `facebox.swift` (Vision) genera los `faceN.txt` que espera el render. | `edicion/facebox.swift` |

## 4. Lo que aprendimos de tu Amaral (y adoptamos para lo que sigue)

- **«Realismo a tope»**: still con Regina ya dentro de la foto (cámara a 50 cm, planta desenfocada al frente, sol a contraluz) → Nano Banana borra a Regina y su sombra → esa placa vacía entra a Genjutsu. En Alboradas usamos la placa directa; para el próximo video adoptamos tu método.
- **`acabado_video.py`**: lo probamos en la v3 de Alboradas y David la **rechazó**: «la nitidez y calidad se ve mejor la v2». Sobre tomas que ya vienen limpias, el grano por cuadro, la halación, la aberración cromática, la curva fílmica y la recompresión las ablandan. En nuestros videos no se usa.
- **`construir.py` por bloques**: alternativa más controlable que Kling start→end para las casas.
- **Prompt de viento**: «architecture, sky and camera stay perfectly still».

## 5. Costos de Alboradas

≈ **240 créditos Higgsfield** (5 Genjutsu a 720p + 4 Kling 3.0) + ≈ **1,800 Magnific** (hojas de outfit, fondos fotorrealizados, letrero y casas). Castelo, con la receta anterior, costó ≈ 11,500 Magnific.

## 6. Flujo de trabajo con David

- Storyboard aprobado antes de la primera toma; cada toma se entrega sola (previa 720p en Drive + QuickTime) y no se abre la siguiente hasta que la apruebe.
- Ningún 1080p ni crédito de más sin su visto bueno; cotizar antes (`get_cost`).
- Todo queda documentado en el repo `regina_torres_terraregia` (`videos-ia/`) y en Drive (`06 Finales/<proyecto>-v1/`).

— David Adorno · Arkamia (documentado con Claude Code, 8-oct-2026)
