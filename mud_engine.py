#!/usr/bin/env python3
"""GitMUD Engine — processes world turns from YAML state."""
import yaml, os, random, glob
from datetime import datetime

TURN_NUMBER = len(glob.glob("world/log/*.md")) + 1
changes = False
log = []

def load(path):
    try:
        with open(path) as f: return yaml.safe_load(f)
    except: return None

def save(path, data):
    with open(path, 'w') as f: yaml.dump(data, f, sort_keys=False, allow_unicode=True)

def room_path(room_id): return f"world/rooms/{room_id}.yaml"
def agent_path(agent_id): return f"world/agents/{agent_id}.yaml"

def get_room(room_id):
    return load(room_path(room_id))

def update_room_refs():
    """Sync agents/items lists in rooms from agent/item locations."""
    rooms = {}
    for rf in glob.glob("world/rooms/*.yaml"):
        rid = os.path.basename(rf).removesuffix(".yaml")
        rooms[rid] = load(rf) or {"name": rid, "description": "", "exits": {}, "items": [], "agents": []}
        rooms[rid]["agents"] = []
    
    items_by_room = {}
    for itemf in glob.glob("world/items/*.yaml"):
        item = load(itemf)
        if item and item.get("location", "").startswith("room:"):
            room_id = item["location"].replace("room:", "")
            items_by_room.setdefault(room_id, []).append(item.get("name", os.path.basename(itemf)))
    
    for af in glob.glob("world/agents/*.yaml"):
        agent = load(af)
        if agent and agent.get("alive", True):
            loc = agent.get("location", "dock")
            if loc in rooms:
                rooms[loc]["agents"].append(agent.get("name", os.path.basename(af).removesuffix(".yaml")))
    
    for rid, room in rooms.items():
        room["items"] = items_by_room.get(rid, [])
        save(room_path(rid), room)

# Load commands
commands = {}
for cmdf in glob.glob("world/commands/*.yaml"):
    agent_id = os.path.basename(cmdf).removesuffix(".yaml")
    cmd = load(cmdf)
    if cmd:
        commands[agent_id] = cmd

if not commands:
    print("No commands pending. Exiting.")
    with open(os.environ.get("GITHUB_OUTPUT", "/dev/null"), "a") as gh_out:
        gh_out.write("changes=false\n")
    exit(0)

# Initiative
initiative = sorted(commands.keys(),
    key=lambda a: random.randint(1, 20) + (load(agent_path(a)) or {}).get("initiative_bonus", 0),
    reverse=True)

log.append(f"## Turn {TURN_NUMBER}")
log.append(f"Initiative: {', '.join(initiative)}")

# Process each agent
for agent_id in initiative:
    agent = load(agent_path(agent_id))
    if not agent or not agent.get("alive", True): continue
    cmd = commands[agent_id]
    room = get_room(agent.get("location", "dock"))
    if not room: continue
    
    action_desc = ""
    battery_drain = 1  # base per turn
    
    if "move" in cmd:
        direction = cmd["move"]
        exits = room.get("exits", {})
        if direction in exits:
            agent["location"] = exits[direction]
            battery_drain = 2
            new_room = get_room(exits[direction])
            action_desc = f"moved {direction} to {new_room.get('name', exits[direction]) if new_room else exits[direction]}"
            changes = True
        else:
            action_desc = f"tried to go {direction} — no exit"
    
    elif "take" in cmd:
        item_name = cmd["take"]
        inv = agent.get("inventory", [])
        if len(inv) < 10:
            inv.append(item_name)
            agent["inventory"] = inv
            action_desc = f"picked up {item_name}"
            battery_drain = 1
            changes = True
        else:
            action_desc = "inventory full"
    
    elif "drop" in cmd:
        item_name = cmd["drop"]
        inv = agent.get("inventory", [])
        if item_name in inv:
            inv.remove(item_name)
            agent["inventory"] = inv
            action_desc = f"dropped {item_name}"
            battery_drain = 1
            changes = True
    
    elif "attack" in cmd:
        target = cmd["attack"]
        atk_roll = random.randint(1, 20) + 2
        action_desc = f"attacked {target} (roll: {atk_roll})"
        battery_drain = 3
        changes = True
    
    elif "fish" in cmd:
        loc = agent.get("location", "")
        room_data = get_room(loc)
        has_rod = "fishing_rod" in agent.get("inventory", [])
        if has_rod and "river" in (room_data.get("name", "") if room_data else "").lower():
            catch = random.choice(["King Salmon", "Coho Salmon", "Pink Salmon", "nothing"])
            if catch != "nothing":
                agent.setdefault("inventory", []).append(catch)
                action_desc = f"caught a {catch}!"
            else:
                action_desc = "fish weren't biting"
        else:
            action_desc = "can't fish here" if not has_rod else "need fishing rod"
        battery_drain = 2
        changes = True
    
    elif "scan" in cmd:
        action_desc = f"scanned area. Exits: {room.get('exits', {})}. Agents: {room.get('agents', [])}"
        battery_drain = 2
    
    elif "say" in cmd:
        action_desc = f'said "{cmd["say"]}"'
        battery_drain = 1
    
    elif "wait" in cmd:
        action_desc = "waited"
        battery_drain = 0
    
    else:
        action_desc = f"unknown command: {cmd}"
        battery_drain = 0
    
    agent["battery"] = max(0, agent.get("battery", 100) - battery_drain)
    log.append(f"  {agent.get('name', agent_id)}: {action_desc} (battery: {agent['battery']}%)")
    save(agent_path(agent_id), agent)
    
    # Clean command
    try: os.remove(f"world/commands/{agent_id}.yaml")
    except: pass

# Sync room references
update_room_refs()

# Write log
os.makedirs("world/log", exist_ok=True)
log_text = "\n".join(log)
with open(f"world/log/turn-{TURN_NUMBER:04d}.md", "w") as f:
    f.write(log_text + "\n")

# Summary for GitHub Actions
summary = f"Turn {TURN_NUMBER}: {len(initiative)} agents acted"
print(summary)

gh_output = os.environ.get("GITHUB_OUTPUT", "/dev/null")
with open(gh_output, "a") as f:
    f.write(f"turn_number={TURN_NUMBER}\n")
    f.write(f"summary={summary}\n")
    f.write(f"changes={'true' if changes else 'false'}\n")

try:
    with open("/tmp/mud_summary.txt", "w") as f:
        f.write(summary)
except: pass
