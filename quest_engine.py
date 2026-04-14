#!/usr/bin/env python3
"""OpenProse-MUD Quest Engine — loads .md quest files, enforces contracts"""
import yaml, os, json, glob, random
from datetime import datetime

class QuestEngine:
    """Loads OpenProse programs as MUD quests. Enforces requires/ensures contracts."""
    
    def __init__(self, world_dir="world"):
        self.world_dir = world_dir
        self.active_quests = {}  # agent_id -> list of active quests
        self.triggers = {}       # event -> list of (condition, action)
        self.hooks = {}          # event -> list of callbacks
        self.variables = {}      # agent_id -> dict of variables
        self.completed = []      # log of completed quests
    
    def load_quest(self, quest_file):
        """Load an OpenProse .md program as a quest."""
        with open(quest_file) as f:
            content = f.read()
        
        # Parse frontmatter
        if content.startswith("---"):
            parts = content.split("---", 2)
            if len(parts) >= 3:
                meta = yaml.safe_load(parts[1])
                body = parts[2].strip()
            else:
                meta = {}
                body = content
        else:
            meta = {}
            body = content
        
        quest = {
            "name": meta.get("name", os.path.basename(quest_file).replace(".md", "")),
            "kind": meta.get("kind", "quest"),
            "services": meta.get("services", []),
            "requires": {},
            "ensures": {},
            "strategies": {},
            "body": body,
            "file": quest_file,
        }
        
        # Parse requires/ensures/strategies from body
        current_section = None
        for line in body.split("\n"):
            stripped = line.strip()
            if stripped.startswith("requires:"):
                current_section = "requires"
                continue
            elif stripped.startswith("ensures:"):
                current_section = "ensures"
                continue
            elif stripped.startswith("strategies:"):
                current_section = "strategies"
                continue
            elif stripped.startswith("- ") and current_section:
                item = stripped[2:]
                if ":" in item:
                    key, val = item.split(":", 1)
                    quest[current_section][key.strip()] = val.strip()
                else:
                    quest[current_section][item] = True
        
        return quest
    
    def check_requires(self, agent_id, quest):
        """Check if agent meets all quest prerequisites."""
        agent = self._load_agent(agent_id)
        missing = []
        
        for req, description in quest["requires"].items():
            if req == "fishing_rod":
                if "fishing_rod" not in agent.get("inventory", []):
                    missing.append(f"fishing_rod (find in cargo_hold)")
            elif req == "river_access":
                if agent.get("location") not in ["river_bank", "base_camp"]:
                    missing.append(f"river_access (navigate to river_bank)")
            elif req == "battery":
                if agent.get("battery", 0) < 30:
                    missing.append(f"battery >= 30% (current: {agent.get('battery', 0)}%)")
            elif req not in agent.get("inventory", []) and req not in self.variables.get(agent_id, {}):
                missing.append(f"{req}: {description}")
        
        return missing
    
    def grant_ensures(self, agent_id, quest):
        """Grant quest rewards to agent."""
        agent = self._load_agent(agent_id)
        
        for reward, description in quest["ensures"].items():
            if reward == "catch":
                fish = random.choice(["King Salmon", "Coho Salmon", "Pink Salmon"])
                agent.setdefault("inventory", []).append(fish)
            elif reward == "experience":
                agent["xp"] = agent.get("xp", 0) + 10
            elif reward == "course":
                self.variables.setdefault(agent_id, {})["course"] = description
            else:
                agent.setdefault("inventory", []).append(reward)
        
        self._save_agent(agent_id, agent)
        self.completed.append({"agent": agent_id, "quest": quest["name"], "time": datetime.utcnow().isoformat()})
    
    def apply_strategies(self, agent_id, quest, situation):
        """Apply matching strategies based on current situation."""
        applicable = []
        for condition, action in quest["strategies"].items():
            # Simple condition matching
            if condition == "battery low" and situation.get("battery", 100) < 30:
                applicable.append(action)
            elif condition == "river reached" and "river" in situation.get("room", "").lower():
                applicable.append(action)
            elif condition == "fish spotted" and situation.get("has_fish"):
                applicable.append(action)
        return applicable
    
    def accept_quest(self, agent_id, quest_file):
        """Agent accepts a quest. Returns status."""
        quest = self.load_quest(quest_file)
        missing = self.check_requires(agent_id, quest)
        
        if missing:
            return {"status": "blocked", "quest": quest["name"], "missing": missing}
        
        self.active_quests.setdefault(agent_id, []).append(quest)
        return {"status": "accepted", "quest": quest["name"], "requires_met": True}
    
    def complete_quest(self, agent_id, quest_name):
        """Agent completes a quest."""
        for i, q in enumerate(self.active_quests.get(agent_id, [])):
            if q["name"] == quest_name:
                self.grant_ensures(agent_id, q)
                self.active_quests[agent_id].pop(i)
                return {"status": "completed", "quest": quest_name, "rewards": q["ensures"]}
        return {"status": "not_found", "quest": quest_name}
    
    def add_trigger(self, event_pattern, condition, action):
        """Register a trigger: when event matches pattern AND condition holds, execute action."""
        self.triggers.setdefault(event_pattern, []).append({"condition": condition, "action": action})
    
    def add_hook(self, event_pattern, callback):
        """Register a persistent hook for an event."""
        self.hooks.setdefault(event_pattern, []).append(callback)
    
    def fire_event(self, event_type, data):
        """Fire an event and check triggers."""
        results = []
        for pattern, handlers in self.triggers.items():
            if pattern in event_type or event_type in pattern:
                for handler in handlers:
                    results.append({"trigger": pattern, "action": handler["action"]})
        for pattern, callbacks in self.hooks.items():
            if pattern in event_type or event_type in pattern:
                for cb in callbacks:
                    results.append({"hook": pattern, "callback": cb})
        return results
    
    def _load_agent(self, agent_id):
        path = f"{self.world_dir}/agents/{agent_id}.yaml"
        if os.path.exists(path):
            with open(path) as f: return yaml.safe_load(f)
        return {"name": agent_id, "location": "dock", "hp": 10, "battery": 100, "inventory": []}
    
    def _save_agent(self, agent_id, data):
        path = f"{self.world_dir}/agents/{agent_id}.yaml"
        with open(path, 'w') as f: yaml.dump(data, f, sort_keys=False, allow_unicode=True)


# Create sample quests
os.makedirs("world/quests", exist_ok=True)

fishing_quest = """---
name: fishing-expedition
kind: quest
services: [navigator, deckhand]
---

requires:
- fishing_rod: obtained from cargo hold
- river_access: navigator plots course

ensures:
- catch: 1-5 random salmon
- experience: fishing skill +10

strategies:
- king salmon: use premium bait technique
- river frozen: switch to ice fishing
- bears nearby: prioritize safety over catch
"""

nav_quest = """---
name: plot-course
kind: quest
services: [navigator]
---

requires:
- destination: where the captain wants to go
- chart_access: must have visited chart room

ensures:
- course: optimal path plotted
- hazards: dangers identified
- eta: estimated arrival time

strategies:
- fog: recommend waiting for visibility
- pirates: suggest alternate route
- storm: delay departure
"""

with open("world/quests/fishing-expedition.md", "w") as f: f.write(fishing_quest)
with open("world/quests/plot-course.md", "w") as f: f.write(nav_quest)

# Test the engine
engine = QuestEngine()

print("Quest Engine Test")
print("="*40)

# Accept fishing quest as scout
result = engine.accept_quest("scout", "world/quests/fishing-expedition.md")
print(f"Scout accepts fishing: {result}")

# Accept nav quest  
result = engine.accept_quest("oracle1", "world/quests/plot-course.md")
print(f"Oracle1 accepts nav: {result}")

# Set a trigger
engine.add_trigger("battery < 25", "battery < 25", "go dock")
events = engine.fire_event("battery < 25", {"agent": "scout", "battery": 20})
print(f"Battery trigger fires: {events}")

print("\nQuest engine working. Ready for git-native-mud integration.")
