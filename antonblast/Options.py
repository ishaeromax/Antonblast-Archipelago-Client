from dataclasses import dataclass
from Options import Choice, Toggle, DefaultOnToggle, Range, OptionGroup, PerGameCommonOptions

# all the settings players can tweak
class StartingStage(Choice):
  display_name = 'Starting Stage'
  option_boiler_city = 0
  option_slowroast_sewer = 1
  option_cinnamon_springs = 2
  option_bomb_candy_mines = 3
  option_the_big_bath = 4
  option_concrete_jungle = 5
  option_the_mad_mall = 6
  option_pinball_mire = 7
  option_crimson_factory = 8
  option_the_mysterious_glasshouse = 9
  option_devilled_gardens = 10
  option_hell_manor = 11
  default = 0

class Goal(Choice):
  display_name = 'Goal'
  option_satan = 0
  option_all = 1
  default = 0

class IncludeEXBosses(Toggle):
  display_name = 'Include EX Bosses'
  default = False

class IncludeLimeTrials(Toggle):
  display_name = 'Include Lime Trials'
  default = True

class IncludeShopItems(Toggle):
  display_name = 'Include Shop Items'
  default = True

class DualCharacter(Toggle):
  display_name = 'Dual Character Mode'
  default = False

class Character(Choice):
  display_name = 'Character'
  option_anton = 0
  option_annie = 1
  default = 0

class StageUnlockMode(DefaultOnToggle):
  display_name = 'Stage Unlock Mode'
  default = True

class IncludeTimeTrials(DefaultOnToggle):
  display_name = 'Include Time Trials'
  default = True

class TimeTrialMult(Range):
  display_name = 'Time Trial Scale (%)'
  range_start = 100
  range_end = 300
  default = 150

class IncludeCracked(Toggle):
  display_name = 'Include Cracked'
  default = False

class DeathLinkToggle(Toggle):
  display_name = 'Death Link'
  default = False

@dataclass
class AntonOptions(PerGameCommonOptions):
  starting_stage: StartingStage
  goal: Goal
  include_ex_bosses: IncludeEXBosses
  include_lime_trials: IncludeLimeTrials
  include_shop_items: IncludeShopItems
  dual_character: DualCharacter
  character: Character
  stage_unlock_mode: StageUnlockMode
  include_time_trials: IncludeTimeTrials
  time_trial_mult: TimeTrialMult
  include_cracked: IncludeCracked
  death_link: DeathLinkToggle

anton_option_groups = [
  OptionGroup('Gameplay', [
    StartingStage,
    Goal,
    StageUnlockMode,
    DualCharacter,
    Character,
    IncludeEXBosses,
    IncludeLimeTrials,
    IncludeTimeTrials,
    TimeTrialMult,
    IncludeCracked,
  ]),
  
  OptionGroup('Items', [
    IncludeShopItems,
  ]),
]
