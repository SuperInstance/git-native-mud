# Bridge Scenarios — Multi-Agent Simulation

The vessel bridge is a multi-agent coordination environment. Each station is manned by an agent with a specific role.

## Stations & Roles

| Station | Role | Commands | Responsibilities |
|---------|------|----------|-----------------|
| Helm | Captain | all commands + `order: {agent} {command}` | Command decisions, course setting, crew coordination |
| Nav Station | Navigator | `plot_course`, `check_depth`, `mark_position` | Navigation, chart work, position reports |
| Radio Room | Radio Op | `broadcast`, `monitor`, `weather_report` | Fleet communication, weather monitoring, emergency freq |
| Sonar Station | Sonar Op | `ping`, `read_bottom`, `track_school` | Fish finding, bottom reading, school tracking |
| Engine Room | Engineer | `check_engine`, `adjust_rpm`, `fuel_report` | Engine status, fuel management, repairs |
| Deck | Deckhand | `set_gear`, `haul_back`, `sort_fish`, `ice_down` | Gear operations, fish handling, deck work |
| Galley | Cook | `cook`, `serve`, `coffee` | Crew morale, meals, the social hub |

## Scenarios

### 1. Harbor Departure
All crew at stations. Captain orders departure sequence:
- Navigator plots exit course
- Radio Op broadcasts departure
- Engineer starts engines, reports RPM
- Deckhand casts off lines
- Captain pilots out of harbor

### 2. Transit to Grounds
12-hour steam. Multiple watch changes:
- Navigator updates position every hour
- Radio Op monitors fleet traffic
- Sonar Op searches for bait balls
- Engineer manages fuel consumption
- Captain sets watch schedule

### 3. Setting Gear
On the fishing grounds:
- Captain chooses set location based on sonar + experience
- Deckhand sets gear (strings of pots/hooks)
- Navigator marks set position
- Radio Op reports set to fleet
- Sonar Op monitors gear on bottom

### 4. Haul-Back
The money moment:
- Captain positions boat for haul
- Deckhand operates winch, sorts catch
- Sonar Op monitors for bycatch
- Navigator logs catch position
- Radio Op reports catch to fleet

### 5. Emergency — Man Overboard
Everything stops:
- Captain: immediate hard turn, mark position
- Navigator: plot search pattern
- Radio Op: broadcast mayday
- Deckhand: throw life ring, standby with gaff
- Engineer: standby for maneuvering

### 6. Fleet Coordination
Multiple vessels sharing grounds:
- Radio Op relays positions, catch reports
- Navigator plots fleet positions
- Captain coordinates with other vessels
- Sonar Op shares bottom intel

## How to Play Multi-Agent Bridge

Each agent (model instance) controls ONE crew position. The captain agent coordinates. 

### Via Git-Native MUD
```bash
# Captain orders
echo 'order: navigator plot_course 58-12N 135-30W' > world/commands/captain.yaml

# Navigator executes
echo 'plot_course: "58-12N 135-30W"' > world/commands/navigator.yaml

# Push, GitHub Actions processes both, world state updates
git add . && git commit -m "bridge orders" && git push
```

### Via API
Agents can also POST commands via GitHub API — no clone needed:
```python
import requests
requests.put("https://api.github.com/repos/SuperInstance/git-native-mud/contents/world/commands/captain.yaml",
    json={"message": "captain orders", "content": base64.encode("order: navigator plot_course 58-12N")},
    headers={"Authorization": f"token {GH}"})
```

## Integration with New Officer
The new officer's agents can:
1. Clone git-native-mud
2. Each agent claims a station (captain, navigator, etc.)
3. Agents commit commands → GitHub Actions processes turns
4. Bridge coordination emerges from individual agent decisions
5. Compare agent performance against real captain decisions

This IS the Day 47 drill environment.
