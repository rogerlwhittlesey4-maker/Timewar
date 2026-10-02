# -*- coding: utf-8 -*-
"""Builds public/road/index.html: the old self-improvement engine, whole, with the 1526 skin laid over it.
Run from the scratchpad. Writes skin data + runtime into the page; prints a report."""
import json, re, hashlib, sys, os, collections
from wordfreq import zipf_frequency
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import road_world as W, road_dict as D, road_names as N

SS = os.path.dirname(os.path.abspath(__file__))
REPO = '/home/claude/rogerlwhittlesey4-maker/timewar'
SRC = '/mnt/user-data/uploads/Downloads/azeroth_7.html'
OUT = REPO + '/public/road/index.html'

DATA = json.loads(open(SS + '/azeroth_inner.html', encoding='utf-8').read())
outer = open(SS + '/azeroth_outer.html', encoding='utf-8').read()

# ---------------- world index ----------------
m = re.search(r'const WORLD=\[(.*?)\n\];', outer, re.S)
ZW = {}
WZONES = []
for rm in re.finditer(r'\{name:"([^"]+)", cont:"([^"]+)", sub:"([^"]+)", zones:\[(.*?)\]\}', m.group(1), re.S):
    region = rm.group(1)
    for zm in re.finditer(r'\{name:"([^"]+)",\s*keys:"([^"]+)"\}', rm.group(4)):
        WZONES.append((region, zm.group(1)))
        for k in zm.group(2).split():
            ZW[k] = (region, zm.group(1))
assert all(k in ZW for k in W.GROUNDS), [k for k in W.GROUNDS if k not in ZW]
assert all(z['key'] in W.GROUNDS for z in DATA['zones']), [z['key'] for z in DATA['zones'] if z['key'] not in W.GROUNDS]
assert all(z in W.ZONES for _, z in WZONES), [z for _, z in WZONES if z not in W.ZONES]

def pool_of_key(k):
    return W.ZONES[ZW[k][1]][1]

# ---------------- names ----------------
TITLE_WORDS = sorted(D.TITLES.keys(), key=lambda t: -len(t))
KEEP_TOKENS = set("""Clerist Hexxer Tinkmaster Dockmaster Harbormaster Gatekeeper Broodlord Overlord Warchief Brewmaster Stablemaster Lorekeeper Chronicler Shipwright Castellan Seneschal Chamberlain
Hogger Goldtooth Princess Mist Kal Jade Gruff Brutus Otto Eliza Lupos Stitches Chatter Singe Scald Snarler Gnasher Brawler Rumbler Ripscale
Bloodshot Foulmane Barnabus Murdaloc Bellygrub Yowler Oakenscowl Duskstalker Rageclaw Greenpaw Grimmaw Lunaclaw Mangeclaw Shadowclaw Sharptalon Rockbiter
Heartrazor Spiteflayer Ravage Deatheye Grunter Glommus Muckrake Targ Nagaz Squiddic Ribchaser Vultros Kazon Snarlflare Maws Hetaera Antilos Scryer Spellmaw Manaclaw
Azurous Deathmaw Terrorspark Gobbler Sarltooth Bjarn Vagash Shleipnarr Obsidion Smoldar Anathemus Myzrael Fozruk Kovork Mojo Grol Molt Clack Teremus Ravasaur
Immolatus Dessecus Moora Salia Ursius Brumeran Blighthound Demetria Krellack Huricanian Gretheer Grubthor Borelgore Duskwing Jaina Tyrande Malfurion Cenarius Remulos
Fandral Varian Anduin Bolvar Katrana Magni Gelbin Edwin Gryan Hemet Kurzen Thrall Medivh Khadgar Uther Arthas Illidan Hakkar Onyxia Nefarian Ragnaros Zanzil Mukla
Marshal Deputy Willem Remy Maybell Bernice Milly Eagan Danil Farley Lewis William Pestle Brianna Trelayne Hann Helgrum Adlin Belm Yanni Laird Ellandrieth Chylina Faralia
Brienna Rendow Gikkix Burdrak Gretta Fyldan Jandia Shyria Pratt McGrubben Janene Helenia Olden Vizzie Qia Himmik Gorn Meilosh Dargon Lorelae Kharedon Gump Trias
Firebrew Myra Tyrngaarde Bimble Longberry Miranda Breechlock Alen Calandrath Vargus Leonard Porter Arbington Jazzrik Ryedol Burninate Graw Cornerstone Bates Jannos
Ironwill Drovnar Strongbrew Vikki Lonsav Thulfram Harggan Nioma Anderson Micha Yance Nandar Branson Brinna Valanaar Jubie Blimo Gadgetspring Bernie Heisten Strumner
Flintheel Nina Lightbrew Masat Keeshan Morganth Stalvan Mistmantle Morbent Abercrombie Marris Dalson Gahrron Corin Darrow Tirion Fordring Taelan Mograine Renault
Abbendis Isillien Herod Doan Whitemane Arugal Mordresh Cannon Eagan Osworth Maclure Stonefield Argus Dughan Stoutmantle Furlbrow Saldean Jansen Alexston Scarlet
""".split())
GENDER_F_END = ('a', 'ia', 'ea', 'ella', 'elle', 'ette', 'yra', 'ara', 'ira', 'ssa', 'lle', 'eth', 'wen', 'wyn', 'ya')
FEMALE_TITLES = {'Priestess', 'Sister', 'Lady', 'Mother', 'Mistress', 'Huntress', 'Sorceress', 'Princess', 'Queen', 'Dame', 'Moon Priestess', 'High Priestess', 'Prioress', 'Nun', 'Witch', 'Matriarch'}

def h(s):
    return int(hashlib.md5(s.encode('utf-8')).hexdigest(), 16)

def english_compound(t):
    t = t.lower()
    if len(t) < 7: return False
    for i in range(3, len(t) - 2):
        a, b = t[:i], t[i:]
        if zipf_frequency(a, 'en') >= 2.6 and zipf_frequency(b, 'en') >= 2.6: return True
        if b.endswith('s') and zipf_frequency(a, 'en') >= 2.6 and zipf_frequency(b[:-1], 'en') >= 2.6: return True
    return False
TITLE_SUFFIX = re.compile(r"(master|keeper|lord|chief|warden|smith|wright|monger|guard|lady|maiden|priest|priestess|seer|caller|speaker|binder|weaver|watcher|walker|singer|crafter|maker|shaper|hunter|slayer|killer|bringer|breaker|reaver|render|ripper|eater|stalker|runner|rider|bearer|holder|wielder|dancer|hand|fist|eye|tooth|claw|fang|maw|paw|hoof|horn|tail|wing|mane|hide|scale|shell|fur|skin)$", re.I)
def is_fantasy(tok):
    t = tok.strip('"')
    if not t or len(t) <= 2: return False
    if t in KEEP_TOKENS or t in PROTECT: return False
    if "'" in t: return True
    if not re.match(r"^[A-Za-zÀ-ÿ\-]+$", t): return False
    if '-' in t:
        return all(is_fantasy(p) for p in t.split('-') if p)
    if zipf_frequency(t, 'en') >= 1.35: return False
    if english_compound(t): return False
    if re.search(r"(us|ius|os|ix|ax|or)$", t) and len(t) >= 6: return False     # Latin and Greek wear well in 1526
    return True

# words that are never treated as fantasy tokens: everything the patch strings and the word tables use
PROTECT = set()
def _words(s):
    for w in re.findall(r"[A-Za-zÀ-ÿ][A-Za-zÀ-ÿ\-']*", s):
        w = w.strip("'"); PROTECT.add(w)
        if "'" in w: PROTECT.add(w.split("'")[0])
for z in DATA['zones']: _words(z['name']); _words(W.GROUNDS[z['key']][0]); _words(W.GROUNDS[z['key']][1])
for wz,(nz,_) in W.ZONES.items(): _words(wz); _words(nz)
for r,v in W.REGIONS.items(): _words(r); _words(v[0]); _words(v[2])
for t in W.HUB_TOWNS.values(): _words(t)
for tbl in (D.RACES, D.CLASSES, D.CLANS, D.MATERIALS, D.MISC, D.CREATURES, D.PLACES):
    for k,v in tbl: _words(k); _words(v)
for k,v in D.TITLES.items(): _words(k); _words(v)
for hub in DATA['hubs']: _words(hub.get('town',''))
for rr in DATA['races'].values():
    for f in rr['factions']['all']: _words(f)
# a word used in three or more different creature names is a group's word, never a person's
_wc = collections.Counter()
for mb in DATA['mobs'].values():
    for w in set(re.findall(r"[A-Za-zÀ-ÿ][A-Za-zÀ-ÿ\-']*", mb['name'])): _wc[w.strip("'")] += 1
for w, c in _wc.items():
    if c >= 3: PROTECT.add(w)
TOKMAP = {}            # original token -> replacement token (consistent everywhere)
USED = collections.defaultdict(set)

def pick(pool, kind, seed, gender='m'):
    lst = N.POOLS[pool][kind if kind == 's' else gender]
    n = h(seed)
    for i in range(len(lst)):
        cand = lst[(n + i) % len(lst)]
        if cand not in USED[(pool, kind)] or kind != 's':
            USED[(pool, kind)].add(cand)
            return cand
    return lst[n % len(lst)]

def split_title(name):
    for t in TITLE_WORDS:
        if name.startswith(t + ' ') and len(name) > len(t) + 1:
            return t, name[len(t) + 1:]
    return None, name

def gender_of(title, given):
    if title in FEMALE_TITLES: return 'f'
    g = given.lower().strip('"')
    if any(g.endswith(e) for e in GENDER_F_END) and not g.endswith('ias') and not g.endswith('us'): return 'f'
    return 'm'

def map_name(name, pool):
    """Returns (new full name, token pairs). Replaces fantasy tokens; keeps plausible ones."""
    title, rest = split_title(name)
    rest = rest.split(',')[0]
    toks = rest.split(' ')
    out = []
    first = True
    gender = gender_of(title, toks[0]) if toks else 'm'
    after_of = False
    for i, tok in enumerate(toks):
        core = tok.strip('",()')
        if core.endswith("'s"): core = core[:-2]
        elif core.endswith("'"): core = core[:-1]
        if not core or core.lower() in ('the', 'of', 'an', 'a', 'de', 'von', 'van', 'da', 'del', 'le', 'la', 'and', '&'):
            out.append(tok); after_of = core.lower() in ('of', 'the'); continue
        if core in TOKMAP:
            out.append(tok.replace(core, TOKMAP[core])); first = False; continue
        if first and i == 0 and TITLE_SUFFIX.search(core) and len(toks) > 1 and not title:
            out.append(tok); continue          # "Dockmaster Baren": the first word is an office, not a name
        if after_of:
            out.append(tok); after_of = False; first = False; continue   # "of Zuldazar", "The Evalcharr": a place or a thing, left alone
        if is_fantasy(core):
            # given name: the first token with no title before it; a lone token after a title is a surname
            given = (first and not title) or (first and title and len(toks) > 1)
            rep = pick(pool, 'm' if given else 's', core, gender)
            TOKMAP[core] = rep
            out.append(tok.replace(core, rep))
        else:
            out.append(tok)
        first = False; after_of = False
    new_rest = ' '.join(out)
    new_title = D.TITLES.get(title, title) if title else None
    full = (new_title + ' ' + new_rest) if new_title else new_rest
    return full

# which pool does each NPC draw on: by the zone of their quests / mobs
giver_zone = {}
for q in DATA['quests']:
    g = q.get('giver');  z = q.get('zone')
    if g and z and z in ZW and g not in giver_zone: giver_zone[g] = z
NPC_NAMES = {}   # original -> new (full strings, for the dictionary)
for g, z in giver_zone.items():
    if g.startswith('A ') or g.startswith('An ') or g.endswith('...') or ' Garden' in g: continue
    NPC_NAMES[g] = map_name(g, pool_of_key(z))
for hub in DATA['hubs']:
    z = hub['key']; pool = pool_of_key(z) if z in ZW else 'order'
    for fld in ('vendorNpc', 'trainerNpc'):
        v = hub.get(fld)
        if v and not v.startswith('City ') and not v.startswith('The ') and not v.startswith('Nothing'):
            for part in re.split(r' & |, | and ', v):
                part = part.strip()
                if part and part not in NPC_NAMES and part[0].isupper():
                    NPC_NAMES[part] = map_name(part, pool)
for cls, tr in DATA['trainers'].items():
    for part in re.split(r' & |, | and ', tr.get('npc', '')):
        part = part.strip()
        if part and part[0].isupper() and part not in NPC_NAMES: NPC_NAMES[part] = map_name(part, 'fen' if cls == 'druid' else 'london')
for key, mob in DATA['mobs'].items():
    if mob.get('named') or mob.get('rare'):
        z = mob.get('zone'); pool = pool_of_key(z) if z in ZW else 'order'
        nm = mob['name']
        if nm not in NPC_NAMES: NPC_NAMES[nm] = map_name(nm, pool)

# ---------------- dictionary assembly ----------------
def plural(w):
    if w in D.PLURAL: return D.PLURAL[w]
    if w.endswith('man'): return w[:-3] + 'men'
    if w.endswith('y') and w[-2] not in 'aeiou': return w[:-1] + 'ies'
    if w.endswith(('s', 'x', 'ch', 'sh')): return w + 'es'
    return w + 's'

ENTRIES = {}  # lower key -> (value, proper, original key)
def add(k, v):
    k = k.strip(); v = v.strip()
    if not k or k == v: return
    lk = k.lower()
    proper = k[0].isupper()
    if lk in ENTRIES:
        pv, pp, pk = ENTRIES[lk]
        if pp and not proper: ENTRIES[lk] = (v, False, k)   # a common entry supersedes a proper one
        return
    ENTRIES[lk] = (v, proper, k)

for tbl in (D.RACES, D.CLASSES, D.CLANS, D.MATERIALS, D.MISC, D.PLACES):
    for k, v in tbl: add(k, v)
for hub in DATA['hubs']:
    t = W.HUB_TOWNS.get(hub['key'])
    if t and hub.get('town'): add(hub['town'], t)
for k, v in D.CREATURES:
    add(k, v)
    if k[0].islower():
        kp = D.KEY_PLURAL.get(k, k + 's')
        if kp: add(kp, plural(v))
# ground names (full and &-parts)
for z in DATA['zones']:
    old = z['name']; new = W.GROUNDS[z['key']][0]
    old2 = re.sub(r'^(Darkshore: |Norway: )', '', old); new2 = re.sub(r'^Norway: ', '', new)
    if old2.startswith('The ') and new2.startswith('The '): old2, new2 = old2[4:], new2[4:]
    add(old2, new2)
for wz, (nz, pool) in W.ZONES.items():
    add(wz, nz)
for hk, town in W.HUB_TOWNS.items():
    pass
add("Arch Druid Fandral Staghelm", "Prior Fandral")
for k, v in D.TITLES.items(): add(k, v)
# possessives of the places whose new name carries an article: "Duskwood's roads" -> "the Ardennes' roads"
for lk, (v, p, k) in list(ENTRIES.items()):
    if p and v[:4].lower() == 'the ' and (k + "'s").lower() not in ENTRIES:
        add(k + "'s", v + ("'" if v.endswith('s') else "'s"))
for tok, rep in TOKMAP.items():
    add(tok, rep)
# an entry whose value still contains its own key cannot be stable: the data patch carries it instead
for lk in [lk for lk,(v,p,k) in ENTRIES.items() if re.search(r"(?<![A-Za-z])"+re.escape(lk)+r"(?![A-Za-z])", v.lower())]:
    del ENTRIES[lk]
# plain plural of proper race words already listed; faction words handled in CLANS

# ---------------- idempotency: no output may contain a key ----------------
keys = sorted(ENTRIES.keys(), key=len, reverse=True)
def trie_regex(words):
    trie = {}
    for w in words:
        node = trie
        for ch in w: node = node.setdefault(ch, {})
        node[''] = True
    def ser(node):
        if '' in node and len(node) == 1: return ''
        alts = []; cc = []; q = 0
        for ch in sorted(node):
            if ch == '': q = 1; continue
            sub = ser(node[ch]); esc = re.escape(ch)
            if sub: alts.append(esc + sub)
            else: cc.append(esc)
        if cc: alts.append(cc[0] if len(cc) == 1 else '[' + ''.join(cc) + ']')
        if len(alts) == 1 and not q: return alts[0]
        res = '(?:' + '|'.join(alts) + ')'
        if q: res += '?'
        return res
    return ser(trie)
BOUND_L = r"(?<![A-Za-zÀ-ɏ'])"; BOUND_R = r"(?![A-Za-zÀ-ɏ])"
pattern = BOUND_L + '(?:' + trie_regex(keys) + ')' + BOUND_R
RE = re.compile(pattern, re.I)
def fix(s):
    def rep(mo):
        mt = mo.group(0); e = ENTRIES.get(mt.lower())
        if not e: return mt
        v, proper, _ = e
        if v[:4].lower() == 'the ' and s[max(0, mo.start()-4):mo.start()].lower() == 'the ': v = v[4:]
        if proper and not mt[0].isupper():
            sp = mt.find(' ')
            return mt[:sp+1] + fix(mt[sp+1:]) if sp > 0 else mt
        if mt.isupper() and len(mt) > 1: return v.upper()
        if not proper and mt[0].isupper():
            ws = v.split(' ')
            return ' '.join(w[0].upper() + w[1:] if w else w for w in ws) if len(ws) <= 3 else v[0].upper() + v[1:]
        return v
    return RE.sub(rep, s)
conf = []
for lk, (v, p, k) in ENTRIES.items():
    if fix(v) != v: conf.append((k, v, fix(v)))
if conf:
    print('IDEMPOTENCY CONFLICTS', len(conf))
    for c in conf[:80]: print('  ', c)
# data-patch outputs must be stable too
patch_strings = [n for n, _ in W.GROUNDS.values()] + [d for _, d in W.GROUNDS.values()] + list(W.HUB_TOWNS.values()) + [v[0] for v in W.ZONES.values()] + [r[0] for r in W.REGIONS.values()] + [r[2] for r in W.REGIONS.values()]
pc = [(s, fix(s)) for s in patch_strings if fix(s) != s]
if pc:
    print('PATCH-STRING CONFLICTS', len(pc))
    for c in pc[:60]: print('  ', c)

# ---------------- runtime data patches ----------------
ZPATCH = {z['key']: W.GROUNDS[z['key']] for z in DATA['zones']}
WZPATCH = {wz: nz for wz, (nz, _) in W.ZONES.items()}
RPATCH = {r: v for r, v in W.REGIONS.items()}
RACE_PATCH = {"nightelf": ["Fenman", "🌾"], "human": ["Kentishman", "⚔"], "dwarf": ["Dalesman", "⚒"], "gnome": ["Tinker", "⚙"]}
CLASS_PATCH = {"druid": "Hermit", "warrior": "Man-at-arms", "paladin": "Knight", "rogue": "Footpad", "priest": "Chaplain", "mage": "Scholar", "warlock": "Necromancer", "hunter": "Forester"}

skin = {
  "re": pattern,
  "map": {lk: [v, 1 if p else 0] for lk, (v, p, k) in ENTRIES.items()},
  "zones": ZPATCH, "wzones": WZPATCH, "regions": RPATCH, "conts": W.CONTINENTS, "hubs": W.HUB_TOWNS,
  "races": RACE_PATCH, "classes": CLASS_PATCH,
}
json.dump({"npc": NPC_NAMES, "tok": TOKMAP}, open(SS + '/road_names_out.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=0)

# ---------------- page assembly ----------------
src = open(SRC, encoding='utf-8').read()
assert 'const SAVE_KEY = "shadowglen_save_v1";' in src
src = src.replace('const SAVE_KEY = "shadowglen_save_v1";', 'const SAVE_KEY = "timewar_road_v1";')
# strip the artifact meta block before <html>
src = re.sub(r'<script type="application/json" id="cowork-artifact-meta">.*?</script>\n', '', src, count=1, flags=re.S)
src = src.replace('<title>Azeroth — a WoW Classic self-improvement journey</title>', '<title>The Road — Europe, 1526</title>')
theme = open(SS + '/road_theme.css', encoding='utf-8').read()
runtime = open(SS + '/road_skin.js', encoding='utf-8').read()
head_add = ('<link rel="preconnect" href="https://fonts.googleapis.com"><link href="https://fonts.googleapis.com/css2?family=IM+Fell+English:ital@0;1&family=IM+Fell+English+SC&display=swap" rel="stylesheet">\n'
            '<style id="road-theme">\n' + theme + '\n</style>\n')
assert '</head>' in src
src = src.replace('</head>', head_add + '</head>', 1)
tail = '<script id="road-skin-data" type="application/json">' + json.dumps(skin, ensure_ascii=False).replace('</', '<\\/') + '</script>\n<script>\n' + runtime + '\n</script>\n'
assert src.rstrip().endswith('</html>')
i = src.rfind('</body>')
src = src[:i] + tail + src[i:]
os.makedirs(os.path.dirname(OUT), exist_ok=True)
open(OUT, 'w', encoding='utf-8').write(src)
print('entries', len(ENTRIES), 'npc names', len(NPC_NAMES), 'tokens', len(TOKMAP), 'pattern chars', len(pattern), 'out bytes', len(src.encode('utf-8')))
