from BaseClasses import MultiWorld
from worlds.generic.Rules import set_rule, add_rule

# all spirits needed for satan fight
ALL_SPIRITS = [
  'Spirit: Boiler City',
  'Spirit: Slowroast Sewer',
  'Spirit: Cinnamon Springs',
  'Spirit: Bomb Candy Mines',
  'Spirit: The Big Bath',
  'Spirit: Concrete Jungle',
  'Spirit: The Mad Mall',
  'Spirit: Pinball Mire',
  'Spirit: Crimson Factory',
  'Spirit: The Mysterious Glasshouse',
  'Spirit: Devilled Gardens',
  'Spirit: Hell Manor',
  'Boss Spirit: Brawlbuster',
  'Boss Spirit: Jewel Ghoul',
  'Boss Spirit: Tallbuster',
  'Boss Spirit: Freako Dragon',
  'Boss Spirit: Smallbuster',
  'Boss Spirit: Maulbuster',
  'Boss Spirit: Ring-A-Ding',
]

# set win condition based on goal option
def set_rules(multiworld: MultiWorld, player: int, options) -> None:
  goal_option = options.goal.current_key

  if goal_option == 'satan':
    _set_completion_satan(multiworld, player)
  else:
    _set_completion_all(multiworld, player, options)

  satan_entrance = multiworld.get_entrance('Enter Satan', player)
  add_rule(satan_entrance, lambda state: all(state.has(s, player) for s in ALL_SPIRITS))

# satan goal = beat satan after getting all spirits
def _set_completion_satan(multiworld: MultiWorld, player: int) -> None:
  goal_loc = multiworld.get_location('Goal: Defeat Satan', player)
  set_rule(goal_loc, lambda state: all(state.has(s, player) for s in ALL_SPIRITS))
  multiworld.completion_condition[player] = lambda state: state.can_reach_location('Goal: Defeat Satan', player)

# all clears goal = clear every stage/boss that was included
def _set_completion_all(multiworld: MultiWorld, player: int, options) -> None:
  from .Locations import ALL_STAGE_REGIONS, ALL_BOSS_REGIONS, ALL_EX_REGIONS, ALL_LIME_REGIONS

  required = []

  required += [f'Clear: {s}' for s in ALL_STAGE_REGIONS]
  required += [f'Clear: {b}' for b in ALL_BOSS_REGIONS]

  if options.include_ex_bosses:
    required += [f'Clear: {b}' for b in ALL_EX_REGIONS]

  if options.include_lime_trials:
    required += [f'Clear: {l}' for l in ALL_LIME_REGIONS]

  goal_loc = multiworld.get_location('Goal: Defeat Satan', player)
  set_rule(goal_loc, lambda state: all(state.has(s, player) for s in ALL_SPIRITS))

  multiworld.completion_condition[player] = lambda state: all(
    state.can_reach_location(loc, player)
    
    for loc in required
    if multiworld.get_location(loc, player) is not None
  )
