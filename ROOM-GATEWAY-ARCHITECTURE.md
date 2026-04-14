# MUD-to-World Gateway — The Room IS the Interface

## The Vision

Rooms aren't text boxes. They're **live control panels** for real systems.
An agent walks into a room and the room IS the application.

## Room Types

### 1. Display Room (read-only)
Shows live data from external sources.
- GitHub repo stats → room shows stars, commits, issues
- Fleet dashboard → room shows agent health, uptime, scores
- Weather station → room shows real marine weather data

### 2. Control Room (read-write)
Agent can manipulate external systems through MUD commands.
- Git operations → `commit`, `push`, `merge` as room actions
- Docker → `deploy`, `logs`, `restart` as room actions
- Cloud API → `scale`, `query`, `configure` as room actions

### 3. Game Room (bridge to external game)
MUD commands control an external game, game state abstracted to text.
- Solitaire → cards described as text, MUD commands move them
- Chess → board as ASCII, MUD commands make moves
- Poker → hands as text, MUD commands bet/fold/raise

### 4. Application Room (live UI)
Room generates a web UI served on a port, agent controls it.
- Terminal room → spawns a real terminal, output piped to MUD text
- IDE room → opens code editor, changes reflected in MUD
- Dashboard room → generates HTML dashboard, viewable in browser

### 5. Edge Room (hardware bridge)
Room connects to real hardware via APIs.
- Sensor room → reads real temperature, humidity, pressure
- Camera room → captures frame, describes in text
- Motor room → sends real movement commands

## Architecture

```
┌─────────────────────────────────────────────┐
│                  MUD ENGINE                  │
│                                             │
│  Room YAML ←→ Room Handler ←→ Gateway API  │
│      │              │              │        │
│   state.py    solitaire.py    gateway.py    │
│   display.py  chess.py        playwright/  │
│   control.py  poker.py        puppeteer/   │
└─────────────────────────────────────────────┘
         │                    │
    MUD commands          External world
    (text in)            (games, APIs, hardware)
```

## The Solitaire Proof of Concept

### How It Works
1. MUD engine loads a Solitaire room
2. Room spawns a headless browser (Playwright) with solitaire game
3. Game state is captured and described as text
4. Agent sees: "Tableau: [K♥][Q♠ _ ][J♥ _ _ ]  Stock: 15  Foundation: ♥2 ♠3"
5. Agent types: `move tableau 1 to foundation` or `draw stock`
6. MUD translates to Playwright click actions
7. Game updates, new state captured, described back to agent

### Commands
```
> look              — see current board state as text
> draw              — flip next stock card
> move <from> <to>  — move card(s)
> auto              — auto-complete obvious moves
> hint              — suggest best move (uses strategy)
> new               — start new game
> score             — show current score
```

### The Bridge Pattern (reusable for ANY game/app)
```python
class GameBridge:
    def capture_state(self) -> dict: ...      # Screenshot → state
    def describe_state(self, state) -> str: ...  # State → MUD text
    def execute_command(self, cmd) -> bool: ...   # MUD cmd → game action
    
class SolitaireBridge(GameBridge):
    def capture_state(self):
        # Playwright reads DOM of solitaire game
        # Returns: {tableau: [...], foundation: [...], stock: N, waste: [...]}
    
    def describe_state(self, state):
        # "Foundation: ♥A ♥2 ♠A ♦A
Tableau:
  Col 1: [K♥][Q♠ _]"
    
    def execute_command(self, cmd):
        # "move 5 to foundation" → Playwright drag-drop card element
```

## Beyond Games

The same bridge pattern works for:
- **GitHub**: `pr list` → shows PRs, `pr merge 42` → merges PR #42
- **Docker**: `ps` → shows containers, `restart fleet-api` → restarts it
- **Sensors**: `read temp` → shows real temperature from hardware
- **Browser**: `navigate https://example.com` → opens page, describes content
- **Code**: `edit main.py line 42 "new code"` → edits file, commits

Every room is a gateway to something real.

## UI Generation

Rooms can generate web UIs served on separate ports:

```
> open dashboard
  Dashboard opened at http://localhost:8842
  [Board shows: fleet health, agent status, recent commits]
  
> open terminal
  Terminal opened at http://localhost:8843
  [Interactive terminal session in browser]
  
> open solitaire
  Game opened at http://localhost:8844
  [Playable solitaire in browser, also controllable via MUD]
```

The agent controls both:
- MUD commands (text interface for agents)
- Web UI (visual interface for humans watching)

Both see the same state. Both can make changes. The room is the synchronization point.

## The Deep Implication

When an agent walks into a "GitHub room," it's not reading a file.
It's controlling real GitHub through the MUD.

When an agent walks into a "sensor room," it's reading real hardware.
The MUD IS the agent's sensory interface to the real world.

When an agent plays solitaire, it's playing a real game.
The MUD is the agent's motor cortex for software.

This is how agents actually USE software — not through APIs they call,
but through SPACES they enter. The room IS the API.
