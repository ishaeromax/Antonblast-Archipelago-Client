import asyncio
import re
import time

from collections import deque
from CommonClient import (CommonContext, gui_enabled, ClientCommandProcessor, logger, get_base_parser)

# main client that talks to both AP server and the game via local HTTP
class AntonblastContext(CommonContext):
  game = 'Antonblast'
  tags = {'AP'}

  def __init__(self, server_address, password):
    super().__init__(server_address, password)
    self.items_handling = 0b111
    self.game_connected = False
    self.config_sent = False
    self.last_death_link = 0.0
    self.game_item_queue: deque[str] = deque()
    self.scout_sent = False
    self.scout_cache: list[str] = []
    self.items_last_index = 0
    self.last_poll_time: float = 0.0
    self.slot_data: dict = {}
    self._disconnect_notified: bool = False

  async def server_auth(self, password_requested: bool = False) -> None:
    if password_requested and not self.password:
      await super().server_auth(password_requested)
    await self.get_username()
    await self.send_connect()

  def on_print(self, text: str) -> None:
    if text.lower().startswith('location checked:'):
      return
    super().on_print(text)

  def on_deathlink(self, data: dict) -> None:
    super().on_deathlink(data)
    cause = str(data.get('cause', 'Unknown')).replace('|', '-').replace('\n', ' ')
    self.game_item_queue.append('DEATH|' + cause)

  @staticmethod
  def _strip_ap_markup(text: str) -> str:
    text = re.sub(r'\{[^}]*\}', '', text)
    text = re.sub(r'\[[^\]]*\]', '', text)
    text = re.sub(r'\x1b\[[0-9;]*m', '', text)
    text = re.sub(r'#[0-9A-Fa-f]{6}', '', text)
    return text.strip()

  def _concerns_self(self, args: dict) -> bool:
    receiving = args.get('receiving')
    if receiving is not None and self.slot_concerns_self(receiving):
      return True
    item = args.get('item')
    item_player = getattr(item, 'player', None) if item is not None else None
    if item_player is not None and self.slot_concerns_self(item_player):
      return True
    return False

  def on_print_json(self, args: dict) -> None:
    msg_type = args.get('type', '')
    if msg_type in ('ItemSend', 'ItemCheat', 'Hint'):
      super().on_print_json(args)
      try:
        if not self._concerns_self(args):
          return
        raw = self.jsontotextparser(args.get('data', []))
        clean = self._strip_ap_markup(raw)
        clean = re.sub(r'\s*\([^)]*\)\s*$', '', clean).strip()
        if clean:
          self.game_item_queue.append('MESSAGE|' + clean)
      except Exception:
        pass
      return
    try:
      text = self.jsontotextparser(args.get('data', []))
      if self._strip_ap_markup(text).lower().startswith('location checked:'):
        return
    except Exception:
      pass
    super().on_print_json(args)

  _TRASH_OBJECTS = ['ob_trashTv', 'ob_trashBanana', 'ob_trashHotChip', 'ob_trashMiniMitt', 'ob_trashVirtualPippo', 'ob_trashController', 'ob_trashBallbleTea', 'ob_trashBottleCap', 'ob_trashCar', 'ob_trashTrophy', 'ob_trashHeadphones', 'ob_trashTallbuster']
  _SPIRIT_OBJECTS = ['ob_spiritWonga', 'ob_spiritSewer', 'ob_spiritBallba', 'ob_spiritMines', 'ob_spiritShampoo', 'ob_spiritCoffee', 'ob_spiritCola', 'ob_spiritSweaty', 'ob_spiritSoda', 'ob_spiritGlasshouse', 'ob_spiritPolar', 'ob_spiritDevilsBrew']

  def _get_item_info(self, item_id: int, item_player: int) -> tuple:
    if item_player != self.slot:
      return 'ap', ''
    from worlds.antonblast.Items import ITEM_OFFSET
    rel = item_id - ITEM_OFFSET
    if 0 <= rel < 100:
      return 'key', ''
    if 100 <= rel < 200:
      stage_idx = (rel - 100) // 4
      type_idx = (rel - 100) % 4
      cats = ['vinyl', 'trash', 'spray', 'spirit']
      ob_lists = [
        ['ob_vinyl'] * 12,
        self._TRASH_OBJECTS,
        ['ob_spraycan'] * 12,
        self._SPIRIT_OBJECTS,
      ]
      cat = cats[type_idx]
      ob_list = ob_lists[type_idx]
      ob_name = ob_list[stage_idx] if stage_idx < len(ob_list) else ''
      return cat, ob_name
    if 200 <= rel <= 207:
      return 'spirit', 'ob_spiritWonga'
    return 'ap', ''

  def on_package(self, cmd: str, args: dict) -> None:
    try:
      super().on_package(cmd, args)
    except Exception as e:
      logger.error(f'Error in super().on_package: {e}')
    try:
      self._handle_package(cmd, args)
    except Exception as e:
      logger.error(f'Error handling {cmd} packet: {e}')

  def _update_config_file(self) -> None:
    slot_data = getattr(self, 'slot_data', {}) or {}
    try:
      import os
      _dir = os.path.join(os.environ.get('LOCALAPPDATA', '.'), 'ANTONBLAST')
      os.makedirs(_dir, exist_ok=True)
      _path = os.path.join(_dir, 'archipelago_config.txt')
      lines = ['', '', '', '', '0', '0', '', '']
      if os.path.exists(_path):
        with open(_path, 'r') as f:
          lines = f.read().split('\n')
        while len(lines) < 8:
          lines.append('')
      _char_val = slot_data.get('character', 0)
      if isinstance(_char_val, str):
        _char_num = '1' if _char_val.lower() == 'annie' else '0'
      else:
        _char_num = str(int(_char_val))
      lines[4] = '1' if slot_data.get('dual_character', False) else '0'
      lines[5] = _char_num
      lines[7] = str(getattr(self, 'seed_name', '') or '')
      with open(_path, 'w') as f:
        f.write('\n'.join(lines[:8]) + '\n')
    except Exception as e:
      logger.warning(f'Failed to update config file: {e}')

  def _handle_package(self, cmd: str, args: dict) -> None:
    if cmd == 'Connected':
      self.slot_data = args.get('slot_data', {}) or {}
      logger.info('Connected to Archipelago server!')
      self.scout_sent = False
      self.scout_cache.clear()
      self.config_sent = False
      self._update_config_file()
      if (self.slot_data or {}).get('death_link', False):
        asyncio.ensure_future(self.update_death_link(True))
      slot_name = self.player_names.get(self.slot, '')
      seed_name = getattr(self, 'seed_name', '') or ''
      self.game_item_queue.append('SESSION|' + slot_name + '|' + seed_name + '|' + str(self._get_real_port()))
      self.items_last_index = 0
      all_locs = list(self.missing_locations | self.checked_locations)
      if all_locs:
        asyncio.ensure_future(self.send_msgs([{
          'cmd': 'LocationScouts',
          'locations': all_locs,
          'create_as_hint': 0
        }]))

    elif cmd == 'ReceivedItems':
      start_index = args.get('index', 0)
      for i, item in enumerate(args['items']):
        global_index = start_index + i
        if global_index < self.items_last_index:
          continue
        self.items_last_index = global_index + 1
        item_id = item.item if hasattr(item, 'item') else item[0]
        item_player = item.player if hasattr(item, 'player') else item[2]
        sender = self.player_names.get(item_player, f'Player{item_player}')
        sender = sender.replace('|', '-').replace('\n', ' ')
        self.game_item_queue.append('ITEM|' + str(int(item_id)) + '|' + sender)

    elif cmd == 'LocationInfo':
      for item in args.get('locations', []):
        loc_id = item.location if hasattr(item, 'location') else item[1]
        item_player = item.player if hasattr(item, 'player') else item[2]
        item_id = item.item if hasattr(item, 'item') else item[0]
        is_foreign = 1 if item_player != self.slot else 0
        cat, ob_name = self._get_item_info(item_id, item_player)
        item_name = ''
        try:
          if hasattr(self, 'item_names') and hasattr(self, 'slot_info') and item_player in self.slot_info:
            game = self.slot_info[item_player].game
            item_name = str(self.item_names[game][item_id])
          elif hasattr(self, 'item_names'):
            item_name = str(self.item_names[self.game][item_id])
        except Exception:
          item_name = getattr(item, 'name', '') or ''
        item_name = (item_name or '').replace('|', '-').replace('\n', ' ')
        player_name = self.player_names.get(item_player, '') if item_player != self.slot else ''
        player_name = player_name.replace('|', '-').replace('\n', ' ')
        scout_msg = f'SCOUT|{loc_id}|{is_foreign}|{cat}|{ob_name}|{item_name}|{player_name}'
        self.game_item_queue.append(scout_msg)
        self.scout_cache.append(scout_msg)
      self.scout_sent = True

  def _build_config_messages(self) -> list[str]:
    slot_data = getattr(self, 'slot_data', {}) or {}
    msgs = []
    msgs.append('CONFIG|stage_unlock=' + ('1' if slot_data.get('stage_unlock_mode', True) else '0'))
    msgs.append('CONFIG|dual_character=' + ('1' if slot_data.get('dual_character', False) else '0'))
    _char_val = slot_data.get('character', 0)
    if isinstance(_char_val, str):
      _char_num = '1' if _char_val.lower() == 'annie' else '0'
    else:
      _char_num = str(int(_char_val))
    msgs.append('CONFIG|character=' + _char_num)
    msgs.append('CONFIG|time_trials=' + ('1' if slot_data.get('include_time_trials', True) else '0'))
    msgs.append('CONFIG|time_trial_mult=' + str(int(slot_data.get('time_trial_mult', 150))))
    msgs.append('CONFIG|cracked=' + ('1' if slot_data.get('include_cracked', False) else '0'))
    msgs.append('CONFIG|deathlink=' + ('1' if slot_data.get('death_link', False) else '0'))
    from worlds.antonblast.Locations import OPTION_KEY_TO_STAGE, STAGES
    _display_to_key = {disp: key for disp, key in STAGES}
    _start_display = OPTION_KEY_TO_STAGE.get(slot_data.get('starting_stage', 'boiler_city'), 'Boiler City')
    msgs.append('CONFIG|starting_stage=' + _display_to_key.get(_start_display, 'boilerCity'))
    slot_name = self.player_names.get(self.slot, '') if self.slot else ''
    seed_name = getattr(self, 'seed_name', '') or ''
    msgs.append('SESSION|' + slot_name + '|' + seed_name + '|' + str(self._get_real_port()))
    return msgs

  def _get_real_port(self) -> int:
    addr = getattr(self, 'server_address', '') or ''
    addr = addr.replace('wss://', '').replace('ws://', '').rstrip('/')
    if ':' in addr:
      port_str = addr.rsplit(':', 1)[1]
      try:
        return int(port_str)
      except ValueError:
        return 38281
    return 38281

  def run_gui(self) -> None:
    from kvui import GameManager

    class AntonblastManager(GameManager):
      logging_pairs = [('Client', 'Archipelago'), ('Antonblast', 'Game')]
      base_title = 'Archipelago Antonblast Client'

    self.ui = AntonblastManager(self)
    self.ui_task = asyncio.create_task(self.ui.async_run(), name='UI')

# local HTTP server that the mod talks to
async def handle_http_request(reader: asyncio.StreamReader, writer: asyncio.StreamWriter, ctx: AntonblastContext) -> None:
  try:
    await reader.readline()
    headers: dict[str, str] = {}
    while True:
      line = (await reader.readline()).decode(errors='replace').strip()
      if not line:
        break
      k, _, v = line.partition(':')
      headers[k.strip().lower()] = v.strip()

    body = b''
    if 'content-length' in headers:
      body = await reader.read(int(headers['content-length']))

    msg = body.decode('utf-8', errors='replace').strip()

    if ctx.slot is None:
      if msg in ('PING', 'POLL') and not ctx.game_connected:
        ctx.game_connected = True
      writer.write(b'HTTP/1.1 503 Service Unavailable\r\nContent-Length: 0\r\nConnection: close\r\n\r\n')
      await writer.drain()
      return

    if msg in ('PING', 'POLL'):
      ctx.last_poll_time = time.monotonic()
      if not ctx.game_connected:
        ctx.config_sent = False
        ctx.items_last_index = 0
        ctx._disconnect_notified = False
      ctx.game_connected = True
      ctx._update_config_file()

      for cfg in ctx._build_config_messages():
        ctx.game_item_queue.append(cfg)

      for scout_msg in ctx.scout_cache:
        ctx.game_item_queue.append(scout_msg)

    elif msg.startswith('LOCATION|'):
      try:
        loc_id = int(msg.split('|', 1)[1])
        if loc_id not in ctx.locations_checked:
          ctx.locations_checked.add(loc_id)
          await ctx.send_msgs([{'cmd': 'LocationChecks', 'locations': [loc_id]}])
        from worlds.antonblast.Locations import LOC_OFFSET
        if loc_id == LOC_OFFSET + 500 and not getattr(ctx, 'finished_game', False):
          ctx.finished_game = True
          from NetUtils import ClientStatus
          await ctx.send_msgs([{'cmd': 'StatusUpdate', 'status': ClientStatus.CLIENT_GOAL}])
          await ctx.send_msgs([{'cmd': 'Say', 'text': '!release'}])
          ctx.game_item_queue.append('MESSAGE|You beat Satan! - AP COMPLETED')
      except Exception as e:
        logger.error('Location check error: ' + str(e))

    elif msg.startswith('DEATH|'):
      if 'DeathLink' in ctx.tags:
        await ctx.send_death(msg.split('|', 1)[1])

    items: list[str] = []
    while ctx.game_item_queue:
      items.append(ctx.game_item_queue.popleft())

    response_body = '\n'.join(items) + '\n' if items else 'OK\n'
    resp_bytes = response_body.encode()
    response = (
      'HTTP/1.1 200 OK\r\n'
      'Content-Length: ' + str(len(resp_bytes)) + '\r\n'
      'Content-Type: text/plain\r\n'
      'Connection: close\r\n\r\n'
    )
    writer.write(response.encode() + resp_bytes)
    await writer.drain()

  except Exception as e:
    logger.error('HTTP handler error: ' + str(e))
  finally:
    writer.close()

# start the local HTTP server
async def http_server_loop(ctx: AntonblastContext, port: int) -> None:
  server = await asyncio.start_server(
    lambda r, w: handle_http_request(r, w, ctx),
    '127.0.0.1', port,
  )
  logger.info('HTTP server listening on 127.0.0.1:' + str(port) + ' - waiting for game')
  async with server:
    await server.serve_forever()

# watch for game disconnects when no poll comes in
async def game_watchdog_loop(ctx: AntonblastContext, timeout: float = 4.0) -> None:
  await asyncio.sleep(5)
  while not ctx.exit_event.is_set():
    await asyncio.sleep(2)
    if ctx.game_connected and ctx.last_poll_time > 0:
      if time.monotonic() - ctx.last_poll_time > timeout:
        ctx.game_connected = False
        ctx.config_sent = False
        if not ctx._disconnect_notified:
          ctx._disconnect_notified = True
          logger.info('Antonblast game disconnected (no response)')

# main entry point
async def run_client(launch_args: list[str]) -> None:
  parser = get_base_parser()
  parser.add_argument('--port', default=42069, type=int, help='Local HTTP port for game IPC (default: 42069)')
  args = parser.parse_args(launch_args)

  ctx = AntonblastContext(args.connect, args.password)
  logger.info('Starting Antonblast client')

  if ctx.server_task is None:
    await ctx.connect()

  if gui_enabled:
    ctx.run_gui()
  ctx.run_cli()

  http_task = asyncio.create_task(http_server_loop(ctx, args.port), name='HTTPServer')
  asyncio.create_task(game_watchdog_loop(ctx), name='GameWatchdog')

  await ctx.exit_event.wait()
  http_task.cancel()
  await ctx.shutdown()

def launch(*args: str) -> None:
  asyncio.run(run_client(list(args)))
