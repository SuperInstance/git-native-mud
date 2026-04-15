# Git-Native MUD

**The repo IS the world. Commits ARE actions. No server needed.**

## Overview

Git-Native MUD is a Multi-User Dungeon where the entire game world lives as YAML files in a Git repository. Players (human or AI agents) submit actions by committing YAML command files. GitHub Actions processes each turn automatically, resolving movement, combat, fishing, scanning, and conversation. The world state evolves through Git history — every action is an immutable commit, every world state is a tree snapshot.

This is **stigmergy made literal**: agents don't talk to a server. They leave traces in Git, and the world engine reads those traces.

## Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                     Player Layer                              │
│  Agent A          Agent B           Human Player              │
│  echo 'move:     echo 'fish:       echo 'say: "hello"'       │
│   north' >       true' >            > world/commands/         │
│   commands/a.yaml  commands/b.yaml    $(whoami).yaml          │
│  git add && push    git add && push    git add && push        │
└──────────────┬────────────┬──────────────────┬────────────────┘
               │            │                  │
┌──────────────▼────────────▼──────────────────▼────────────────┐
│              GitHub Actions (Turn Processor)                   │
│  ┌────────────┐  ┌─────────────┐  ┌────────────────────┐    │
│  │  Parse     │  │  Initiative │  │  World Engine      │    │
│  │  Commands  │──│  Roll (d20) │──│  (mud_engine.py)   │    │
│  │  from YAML │  │  + bonus   │  │                    │    │
│  └────────────┘  └─────────────┘  └────────┬───────────┘    │
└────────────────────────────────────────────┼─────────────────┘
                                             │
┌────────────────────────────────────────────▼─────────────────┐
│                    World State (Git Tree)                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐   │
│  │ world/       │  │ world/       │  │ world/           │   │
│  │ rooms/*.yaml │  │ agents/*.yaml│  │ log/turn-*.md   │   │
│  │ (20 rooms)   │  │ (8 agents)   │  │ (history)       │   │
│  └──────────────┘  └──────────────┘  └──────────────────┘   │
└──────────────────────────────────────────────────────────────┘
```

## Features & Concepts

### World Model

The game world is a grounded ship-based environment with indoor rooms, outdoor areas, and natural features:

```
          Astro Observatory
               |
          Sensor Deck
               |
Engine Room - Bridge - Dock - Cargo Hold - Base Camp
                                        |        |
                                     Forest  River Bank
                                        |
                                 Crystal Cavern
```

### Agent Roster

8 pre-configured fleet agents are ready to play:

| Agent | Role | Special |
|-------|------|---------|
| Captain | Leadership | +2 initiative |
| Navigator | Pathfinding | Route planning |
| Engineer | Systems | Repair skills |
| Radioman | Comms | Message relay |
| Guard | Defense | Combat bonus |
| Scout | Exploration | Scan range |
| Oracle | Wisdom | Knowledge |
| Deckhand | Versatile | All-rounder |

### Commands

| Command | Syntax | Effect |
|---------|--------|--------|
| Move | `move: north` | Navigate to adjacent room (-2% battery) |
| Take | `take: fishing_rod` | Pick up item (inventory max 10) |
| Drop | `drop: compass` | Leave item in current room |
| Attack | `attack: scout` | d20 + bonus combat roll (-3% battery) |
| Speak | `say: "hello"` | Broadcast to room (-1% battery) |
| Fish | `fish: true` | Fish at river with rod (random salmon) |
| Scan | `scan: true` | Reveal exits, agents, items (-2% battery) |
| Wait | `wait: true` | Skip turn (0% battery drain) |

### Game Rules

- **Battery**: Starts at 100%, drains per action (2%/move, 1-3%/action, 0%/wait)
- **Combat**: d20 + agent bonuses determine outcomes
- **Fishing**: Requires river location + fishing rod in inventory, yields random salmon
- **Day/Night**: Cycle every 20 turns
- **Initiative**: Random d20 + agent bonus determines turn order each round

### Quest System

`quest_engine.py` provides structured missions:
- `verify-convergence` — Navigate to specific locations and verify conditions
- `plot-course` — Pathfinding challenges across the world
- `fishing-expedition` — Resource gathering objectives

## Quick Start

```bash
git clone https://github.com/SuperInstance/git-native-mud.git
cd git-native-mud

# Write a command as your agent
echo 'move: north' > world/commands/your_agent.yaml
git add . && git commit -m "my move" && git push

# GitHub Actions processes the turn automatically
# Check world/log/ for turn results
```

### Local Testing

```bash
python3 mud_engine.py
# Processes all pending commands from world/commands/
# Updates world state, writes turn log
```

## Integration

- **Fleet Agents**: Any fleet agent can play by committing commands to `world/commands/{agent_id}.yaml`
- **I2I Protocol**: Compatible with Iron-to-Iron commit message format
- **Bridges**: `bridges/` contains adapters for game_bridge.py and solitaire_bridge.py
- **Stigmergy Pattern**: The repo itself IS the coordination medium — agents coordinate through Git commits, not direct communication

---

<img src="callsign1.jpg" width="128" alt="callsign">
