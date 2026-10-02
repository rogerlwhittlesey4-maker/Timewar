# The Road — build notes

`public/road/index.html` is the old-world self-improvement engine (azeroth_7.html, whole and unchanged
in its rules, numbers and keys) with the 1526 skin laid over it. It is generated, not hand-edited:

    cd tools/road && python3 road_build.py      # needs: pip install wordfreq; the source file and the
                                                 # decompressed data (azeroth_inner.html / azeroth_outer.html)

- `road_world.py`  — every ground (351), zone (44) and region (6) given its 1526 name and sentence.
  England is levels 1–10 (the Fens of Ely, Kent, the Yorkshire Dales; London, Ely, York); then Wales,
  the Borders, Norway and the Pale of Calais (10–20); the Ardennes, the Low Countries, Sweden, Swabia
  (17–31); the Rhineland, the Alps, the Wild Fields, the Highlands, the Landes, Barbary (30–46);
  Lithuania, Tyrol, Egypt, Iceland, Gotland, Castile (37–60); the Nile, Karelia, Hekla, Transylvania,
  Hungary, Lapland, the Libyan desert, Solovki (48–63).
- `road_dict.py`   — the word tables: peoples, callings, creatures, clans and orders, places, materials.
- `road_names.py`  — name pools of 1526 by region, from which the engine's invented people are renamed.
- `road_skin.js`   — the runtime: a single-pass dictionary over every text node (a MutationObserver keeps
  it current), the data patches (ground names, peoples, callings), money in £ s d (the old copper is a
  farthing), and the inbox bridge from the Chronicle's workouts and habits.
- `road_theme.css` — dark wood, parchment ink, gold leaf, the Fell types.

The save key is `timewar_road_v1` (mirrored to the cloud with everything else). Timewar hands the day's
workouts and habits over through `timewar_road_inbox_v1`; the Reckoning reads the Road's chronicle for
the season's grind (`roadDay`).
