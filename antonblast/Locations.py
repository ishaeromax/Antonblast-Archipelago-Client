from BaseClasses import Location

# base IDs, keep em far apart from items
LOC_OFFSET = 42000000
ANNIE_OFFSET = 5000

class AntonLocationData:
  def __init__(self, code: int, region: str, stage_key: str = ''):
    self.code = code
    self.region = region
    self.stage_key = stage_key

class AntonLocation(Location):
  game = 'Antonblast'

# big table of every check in the game (help me)
location_table: dict[str, AntonLocationData] = {}

def _add(name: str, code: int, region: str, stage_key: str = '') -> None:
  location_table[name] = AntonLocationData(code, region, stage_key)

def _add_annie(name: str, anton_code: int, region: str, stage_key: str = '') -> None:
  annie_name = f'Annie - {name}'
  annie_region = f'Annie - {region}'
  location_table[annie_name] = AntonLocationData(LOC_OFFSET + ANNIE_OFFSET + (anton_code - LOC_OFFSET), annie_region, stage_key)

# main story stages
STAGES = [
  ('Boiler City', 'boilerCity'),
  ('Slowroast Sewer', 'slowroastSewer'),
  ('Cinnamon Springs', 'cinnamonSprings'),
  ('Bomb Candy Mines', 'bombCandyMines'),
  ('The Big Bath', 'theBigBath'),
  ('Concrete Jungle', 'concreteJungle'),
  ('The Mad Mall', 'theMadMall'),
  ('Pinball Mire', 'pinballMire'),
  ('Crimson Factory', 'crimsonFactory'),
  ('The Mysterious Glasshouse', 'theMysteriousGlasshouse'),
  ('Devilled Gardens', 'devilledGardens'),
  ('Hell Manor', 'hellManor'),
]

# main bosses
BOSSES = [
  ('Brawlbuster', 'brawlbuster'),
  ('Jewel Ghoul', 'jewelGhoul'),
  ('Tallbuster', 'tallbuster'),
  ('Freako Dragon', 'freakoDragon'),
  ('Smallbuster', 'smallbuster'),
  ('Maulbuster', 'maulbuster'),
  ('Ring-A-Ding', 'ringADing'),
  ('Satan', 'satan'),
]

# optional ex bosses
EX_BOSSES = [
  ('Kaz', 'kaz'),
  ('Parrot', 'parrot'),
  ('Computer', 'computer'),
  ('Chameleon', 'chameleon'),
  ('Tag Team', 'tagTeam'),
]

# lime time trials
LIMES = [
  ('Shark Tank', 'sharkTank'),
  ('Limes a Beach', 'limesABeach'),
  ('Distilled Hill', 'distilledHill'),
  ('Devil\'s a Beach', 'devilsABeach'),
]

# shop stuff
SHOP_TRINKETS = [
  'Trinket: Shutter Shades',
  'Trinket: Cowboy Hat',
  'Trinket: Funny TV',
  'Trinket: Funny TV Big',
  'Trinket: Pet Color',
  'Screen Palette: VB',
  'Screen Palette: GB',
]

SHOP_VINYLS = [
  'Shop Vinyl: Collen Cyte',
  'Shop Vinyl: Element 27',
  'Shop Vinyl: Fred Fuchs',
  'Shop Vinyl: Joseph Cassin',
  'Shop Vinyl: Logan Gerrol',
  'Shop Vinyl: Pear Basket',
  'Shop Vinyl: Rom M',
  'Shop Vinyl: Impetus',
  'Shop Vinyl: William',
]

UPGRADES = [
  'HP Beet Up',
  'Bonus HP Up',
  'Balloon Add-On',
  'Pet Add-On',
  'Spirit Timer Add-On',
]

# autogenerate collectible locations for every stage
_off = 0
for _stage_name, _stage_key in STAGES:
  _code = LOC_OFFSET + _off
  _add(f'Vinyl: {_stage_name}', _code + 0, _stage_name, _stage_key)
  _add(f'Trash: {_stage_name}', _code + 1, _stage_name, _stage_key)
  _add(f'Spray: {_stage_name}', _code + 2, _stage_name, _stage_key)
  _add(f'Spirit: {_stage_name}', _code + 3, _stage_name, _stage_key)
  _add_annie(f'Vinyl: {_stage_name}', _code + 0, _stage_name, _stage_key)
  _add_annie(f'Trash: {_stage_name}', _code + 1, _stage_name, _stage_key)
  _add_annie(f'Spray: {_stage_name}', _code + 2, _stage_name, _stage_key)
  _add_annie(f'Spirit: {_stage_name}', _code + 3, _stage_name, _stage_key)
  _off += 10

# stage clear checks
_stage_clear_off = 150
for _stage_name, _stage_key in STAGES:
  _code = LOC_OFFSET + _stage_clear_off
  _add(f'Clear: {_stage_name}', _code, _stage_name, _stage_key)
  _add_annie(f'Clear: {_stage_name}', _code, _stage_name, _stage_key)
  _stage_clear_off += 1

_boss_clear_off = 200
for _boss_name, _boss_key in BOSSES:
  _code = LOC_OFFSET + _boss_clear_off
  _add(f'Clear: {_boss_name}', _code, _boss_name, _boss_key)
  _boss_clear_off += 1

# ex boss clears
_ex_clear_off = 250
for _boss_name, _boss_key in EX_BOSSES:
  _code = LOC_OFFSET + _ex_clear_off
  _add(f'Clear: {_boss_name}', _code, _boss_name, _boss_key)
  _ex_clear_off += 1

# lime trial clears
_lime_off = 300
for _lime_name, _lime_key in LIMES:
  _code = LOC_OFFSET + _lime_off
  _add(f'Clear: {_lime_name}', _code, _lime_name, _lime_key)
  _lime_off += 1

# shop purchases
_shop_off = 320
for _trinket_name in SHOP_TRINKETS:
  _add(_trinket_name, LOC_OFFSET + _shop_off, 'Shop', '')
  _shop_off += 1

_shop_vinyl_off = 335
for _vinyl_name in SHOP_VINYLS:
  _add(_vinyl_name, LOC_OFFSET + _shop_vinyl_off, 'Shop', '')
  _shop_vinyl_off += 1

_upgrade_off = 360
for _upgrade_name in UPGRADES:
  _add(f'Buy: {_upgrade_name}', LOC_OFFSET + _upgrade_off, 'Shop', '')
  _upgrade_off += 1

# final goal check
_add('Goal: Defeat Satan', LOC_OFFSET + 500, 'Satan', 'satan')

# stage checkpoint checks
_checkpoint_off = 400
for _stage_name, _stage_key in STAGES:
  _code = LOC_OFFSET + _checkpoint_off
  _add(f'Checkpoint: {_stage_name}', _code, _stage_name, _stage_key)
  _add_annie(f'Checkpoint: {_stage_name}', _code, _stage_name, _stage_key)
  _checkpoint_off += 1

ALL_STAGE_REGIONS = [s[0] for s in STAGES]
ALL_BOSS_REGIONS = [b[0] for b in BOSSES]
ALL_EX_REGIONS = [b[0] for b in EX_BOSSES]
ALL_LIME_REGIONS = [l[0] for l in LIMES]

OPTION_KEY_TO_STAGE = {
  'boiler_city': 'Boiler City',
  'slowroast_sewer': 'Slowroast Sewer',
  'cinnamon_springs': 'Cinnamon Springs',
  'bomb_candy_mines': 'Bomb Candy Mines',
  'the_big_bath': 'The Big Bath',
  'concrete_jungle': 'Concrete Jungle',
  'the_mad_mall': 'The Mad Mall',
  'pinball_mire': 'Pinball Mire',
  'crimson_factory': 'Crimson Factory',
  'the_mysterious_glasshouse': 'The Mysterious Glasshouse',
  'devilled_gardens': 'Devilled Gardens',
  'hell_manor': 'Hell Manor',
}

STAGE_TO_KEY_ITEM = {s: f'Level Key: {s}' for s, _ in STAGES + BOSSES + EX_BOSSES + LIMES}

# time trial checks (optional)
TIME_TRIAL_LOCS = {}
_par_off = 42200000
for _s, _sk in STAGES:
  _loc_name = f'Time Trial: {_s}'
  _loc_code = _par_off
  location_table[_loc_name] = AntonLocationData(_loc_code, _s, _sk)
  TIME_TRIAL_LOCS[_sk] = _loc_code
  _par_off += 1

# cracked combo checks (optional)
CRACKED_LOCS = {}
_cracked_off = 42200100
for _s, _sk in STAGES:
  _loc_name = f'Cracked: {_s}'
  _loc_code = _cracked_off
  location_table[_loc_name] = AntonLocationData(_loc_code, _s, _sk)
  CRACKED_LOCS[_sk] = _loc_code
  _cracked_off += 1

for _b, _sk in BOSSES:
  if _b == 'Satan':
    continue
  _loc_name = f'Cracked: {_b}'
  _loc_code = _cracked_off
  location_table[_loc_name] = AntonLocationData(_loc_code, _b, _sk)
  CRACKED_LOCS[_sk] = _loc_code
  _cracked_off += 1
