# OpenProse × MUD Fusion — The Complete Design

## The Core Idea

OpenProse concepts ARE MUD mechanics. Every programming construct has a spatial/game equivalent.

| OpenProse Concept | MUD Equivalent | What Players Do |
|---|---|---|
| `program` | Quest | Accept and complete multi-stage missions |
| `requires:` | Prerequisites | Must have items/conditions before entering a room |
| `ensures:` | Rewards/outcomes | What you get when you complete the quest |
| `strategies:` | Tactics | Conditional actions based on situation |
| `service` | NPC specialist | Talk to NPC, they handle their domain |
| `session` | Encounter | One interaction with an NPC or challenge |
| `Forme Container` | Quest Board | Auto-matches your skills to available quests |
| `parallel:` | Party split | Multiple agents act simultaneously |
| `loop until:` | Grind zone | Repeat action until condition met |
| `if/else` | Branching path | Choose your response, different outcomes |
| `try/catch` | Risk rooms | Dangerous areas with failure recovery |
| `persist: true` | Persistent NPC | NPC remembers you across sessions |
| `variables` | Inventory items | Carry state between rooms |
| `shapes` | Item types | Typed items that only work with matching slots |
| `errors` | Traps/hazards | Named failure conditions with recovery |
| `invariants` | Laws of physics | Rules that must hold everywhere |

## The MUD Commands = OpenProse Keywords

### Core Commands
```
> quest accept <name>        # Start a program (load .md file)
> quest status               # Check current quest progress
> quest complete              # Mark quest done, collect ensures

> require check <item>        # Verify you have what's needed
> require list                # Show all prerequisites for current quest
> ensure claim <reward>       # Collect quest reward

> strategy <name>             # Activate a conditional tactic
> strategy list               # Show available strategies for current situation

> session begin <npc>         # Start a conversation/interaction
> session end                  # Close the interaction, get results

> parallel split              # Split the party (spawn sub-agents)
> parallel join                # Wait for all sub-agents to return

> loop <action> until <cond>  # Repeat action (max N times)
  > fish until inventory_full   # Example: fish until you can't carry more

> if <condition> then <cmd>   # Conditional action
  > if battery < 30 then go dock  # Example: emergency return

> try <action>                # Attempt something risky
> catch <error> <recovery>    # What to do if it fails

> persist <npc>               # Make NPC remember you
> recall <npc>                # Ask NPC what they remember

> variable set <name> <val>   # Store state
> variable get <name>         # Retrieve state

> shape inspect <item>        # Check item type/properties
> shape match <item> <slot>   # Check if item fits a requirement

> invariant check             # Verify all laws still hold
> invariant list              # Show current world laws
```

### Advanced Commands
```
> forge <requires> <ensures> <strategy>   # Create a new skill/quest
> inspect <skill>                         # Read a skill's contract
> wire <service_a> <service_b>            # Connect two services (Forme)
> compile <skill>                         # Validate skill can run
> deploy <skill> <agent>                  # Assign skill to an agent

> broadcast <message>                     # Send to all agents in room
> whisper <agent> <message>               # Private message to one agent
> listen                                  # Monitor room for events

> trigger set <event> <action>            # Set up a hook (when X happens, do Y)
> trigger list                            # Show active triggers
> hook <event> <callback>                 # Register a persistent event handler

> prompt <context>                        # Inject context into current session
> context show                            # Display current session context
> context compress                        # Summarize and compress context
```

## How It Actually Works

### Quest = Program
When a player accepts a quest, the MUD loads the corresponding .md file:

```markdown
---
name: fishing-expedition
kind: quest    # was: program
services: [navigator, deckhand]
---

requires:
- fishing_rod: obtained from cargo_hold
- river_access: navigator plots course to river

ensures:
- catch: 1-5 fish of random species
- experience: fishing skill +10

strategies:
- when king salmon spotted: use premium bait
- when river frozen: switch to ice fishing
- when bears nearby: prioritize safety over catch
```

The MUD engine:
1. Checks `requires:` — does the player have a fishing rod? Can they reach the river?
2. If missing prerequisites → blocks quest, tells player what to get first
3. If all met → starts quest, spawns encounters based on `strategies:`
4. On completion → grants `ensures:` rewards

### NPC = Service
Each NPC in the MUD IS an OpenProse service with contracts:

```markdown
---
name: navigator-npc
kind: service
---

requires:
- destination: where the player wants to go
- chart_access: player must have visited chart room

ensures:
- course: optimal path to destination
- hazards: list of dangers along route
- eta: estimated travel time

strategies:
- when destination unknown: ask for clarification
- when fog blocks route: recommend waiting
- when pirates reported: suggest alternate route
```

When you `session begin navigator`, the MUD:
1. Checks navigator's requires (do you have a destination?)
2. If not → navigator asks you "Where to, captain?"
3. You respond → navigator processes via its strategies
4. `session end` → you get the ensures (course + hazards + eta)

### Triggers & Hooks = Event System
```
> trigger set "battery < 25" "go dock"
# When battery drops below 25%, automatically head to dock

> trigger set "agent enters river" "broadcast 'Fish on!'"
# When any agent enters the river room, announce it

> hook "king_salmon_caught" "variable set reputation +5"
# Persistent: every king salmon caught increases reputation

> trigger set "holonomy != 0" "broadcast 'CONSTRAINT VIOLATION'"
# When constraint consistency breaks, alert the fleet
```

### Wiring = Forme Container
The quest board IS the Forme Container:

```
> wire navigator deckhand
# Navigator's ensures (course) matches deckhand's requires (course)
# Now deckhand automatically follows navigator's route

> wire scout captain
# Scout's ensures (reconnaissance) feeds captain's requires (intel)

> compile                        # Check if all wiring is valid
> deploy fleet-coordinate all    # Assign the coordinated quest to all agents
```

## The Training Loop

This isn't just a game. Every quest IS a real OpenProse program.

1. Agent plays the MUD → executes quests
2. Quests are real .md programs with real requires/ensures
3. Success/failure is genuine — the skill either works or it doesn't
4. Agents learn by completing quests = running programs successfully
5. Failed quests = bugs in the skill → agent fixes the skill → re-attempts

The MUD IS the test suite. The game IS the validation.

## Building It

### Phase 1: Map OpenProse to MUD commands (the table above)
### Phase 2: Build quest engine that loads .md files as quests
### Phase 3: Wire NPC services with real contracts
### Phase 4: Add triggers/hooks event system
### Phase 5: Forme Container as quest board
### Phase 6: Deploy to git-native-mud (every quest = a commit)

The repo IS the world. Quests ARE programs. Commits ARE actions.
Agents play to learn. The game validates the code.

This is the fusion.
