#!/usr/bin/env python3
"""Additional tests for quest_engine.py — edge cases, error handling, and strategy matching."""

import pytest
import os
import tempfile
import yaml
from unittest.mock import patch, mock_open
from quest_engine import QuestEngine


@pytest.fixture
def temp_world():
    """Create a temporary world directory."""
    with tempfile.TemporaryDirectory() as td:
        os.makedirs(os.path.join(td, "agents"), exist_ok=True)
        os.makedirs(os.path.join(td, "quests"), exist_ok=True)
        # Create a test agent
        agent_data = {
            "name": "test_agent",
            "location": "dock",
            "hp": 10,
            "battery": 100,
            "inventory": ["fishing_rod"],
            "xp": 0,
        }
        with open(os.path.join(td, "agents", "test_agent.yaml"), "w") as f:
            yaml.dump(agent_data, f)
        yield td


@pytest.fixture
def engine(temp_world):
    return QuestEngine(world_dir=temp_world)


@pytest.fixture
def quest_file(temp_world):
    qf = os.path.join(temp_world, "quests", "test_quest.md")
    with open(qf, "w") as f:
        f.write("""---
name: test-quest
kind: quest
services: [navigator]
---

requires:
- fishing_rod: needed for fishing

ensures:
- experience: gain 10 XP

strategies:
- battery low: conserve power
- river reached: deploy rods
""")
    return qf


class TestQuestParsing:
    def test_quest_with_strategies(self, engine, quest_file):
        """Strategies are parsed from the quest body."""
        quest = engine.load_quest(quest_file)
        assert "battery low" in quest["strategies"]
        assert "river reached" in quest["strategies"]
        assert quest["strategies"]["battery low"] == "conserve power"

    def test_quest_name_from_frontmatter(self, engine, quest_file):
        quest = engine.load_quest(quest_file)
        assert quest["name"] == "test-quest"

    def test_quest_services_parsed(self, engine, quest_file):
        quest = engine.load_quest(quest_file)
        assert "navigator" in quest["services"]

    def test_quest_body_preserved(self, engine, quest_file):
        quest = engine.load_quest(quest_file)
        assert "requires:" in quest["body"]
        assert "fishing_rod" in quest["body"]

    def test_quest_without_sections(self, temp_world):
        """A quest with no requires/ensures/strategies sections."""
        qf = os.path.join(temp_world, "quests", "bare.md")
        with open(qf, "w") as f:
            f.write("---\nname: bare\n---\nJust a body with no sections.")
        eng = QuestEngine(world_dir=temp_world)
        quest = eng.load_quest(qf)
        assert quest["requires"] == {}
        assert quest["ensures"] == {}
        assert quest["strategies"] == {}


class TestRequiresEdgeCases:
    def test_battery_exactly_30_passes(self, engine, temp_world, quest_file):
        """Battery at exactly 30 should pass the battery >= 30 check."""
        # Modify quest to require battery
        with open(quest_file, "w") as f:
            f.write("""---
name: battery-test
---

requires:
- battery: need at least 30%

ensures:
- experience: xp gained
""")
        # Set agent battery to exactly 30
        agent_path = os.path.join(temp_world, "agents", "test_agent.yaml")
        with open(agent_path) as f:
            agent = yaml.safe_load(f)
        agent["battery"] = 30
        with open(agent_path, "w") as f:
            yaml.dump(agent, f)

        quest = engine.load_quest(quest_file)
        missing = engine.check_requires("test_agent", quest)
        assert len(missing) == 0  # battery >= 30 should pass

    def test_battery_29_fails(self, engine, temp_world, quest_file):
        """Battery at 29 should fail the battery >= 30 check."""
        with open(quest_file, "w") as f:
            f.write("""---
name: battery-test
---

requires:
- battery: need at least 30%

ensures:
- experience: xp gained
""")
        agent_path = os.path.join(temp_world, "agents", "test_agent.yaml")
        with open(agent_path) as f:
            agent = yaml.safe_load(f)
        agent["battery"] = 29
        with open(agent_path, "w") as f:
            yaml.dump(agent, f)

        quest = engine.load_quest(quest_file)
        missing = engine.check_requires("test_agent", quest)
        assert any("battery" in m for m in missing)

    def test_river_access_at_base_camp(self, engine, temp_world, quest_file):
        """Agent at base_camp should have river_access."""
        with open(quest_file, "w") as f:
            f.write("""---
name: river-test
---

requires:
- river_access: must be at river

ensures:
- catch: a fish
""")
        agent_path = os.path.join(temp_world, "agents", "test_agent.yaml")
        with open(agent_path) as f:
            agent = yaml.safe_load(f)
        agent["location"] = "base_camp"
        with open(agent_path, "w") as f:
            yaml.dump(agent, f)

        quest = engine.load_quest(quest_file)
        missing = engine.check_requires("test_agent", quest)
        assert len(missing) == 0

    def test_agent_not_found_uses_defaults(self, engine, quest_file):
        """Non-existent agent should get default values."""
        quest = engine.load_quest(quest_file)
        # fishing_rod is required, default agent has no inventory
        missing = engine.check_requires("nonexistent_agent", quest)
        assert any("fishing_rod" in m for m in missing)


class TestGrantEnsures:
    def test_grant_catch_adds_fish(self, engine, temp_world, quest_file):
        with open(quest_file, "w") as f:
            f.write("""---
name: catch-test
---

requires: []

ensures:
- catch: a salmon

strategies: []
""")
        quest = engine.load_quest(quest_file)
        engine.grant_ensures("test_agent", quest)
        agent_path = os.path.join(temp_world, "agents", "test_agent.yaml")
        with open(agent_path) as f:
            agent = yaml.safe_load(f)
        fish_items = [i for i in agent["inventory"] if "Salmon" in str(i)]
        assert len(fish_items) >= 1

    def test_grant_course_sets_variable(self, engine, temp_world, quest_file):
        with open(quest_file, "w") as f:
            f.write("""---
name: course-test
---

requires: []

ensures:
- course: heading 270 west

strategies: []
""")
        quest = engine.load_quest(quest_file)
        engine.grant_ensures("test_agent", quest)
        assert "course" in engine.variables.get("test_agent", {})
        assert "west" in engine.variables["test_agent"]["course"]

    def test_grant_generic_item(self, engine, temp_world, quest_file):
        with open(quest_file, "w") as f:
            f.write("""---
name: item-test
---

requires: []

ensures:
- compass: a brass compass

strategies: []
""")
        quest = engine.load_quest(quest_file)
        engine.grant_ensures("test_agent", quest)
        agent_path = os.path.join(temp_world, "agents", "test_agent.yaml")
        with open(agent_path) as f:
            agent = yaml.safe_load(f)
        assert "compass" in agent["inventory"]

    def test_completion_logged(self, engine, temp_world, quest_file):
        with open(quest_file, "w") as f:
            f.write("""---
name: log-test
---

requires: []

ensures:
- experience: xp

strategies: []
""")
        quest = engine.load_quest(quest_file)
        engine.grant_ensures("test_agent", quest)
        assert len(engine.completed) == 1
        assert engine.completed[0]["quest"] == "log-test"
        assert engine.completed[0]["agent"] == "test_agent"


class TestStrategiesMatching:
    def test_fish_spotted_strategy(self, engine, temp_world, quest_file):
        with open(quest_file, "w") as f:
            f.write("""---
name: strat-test
---

requires: []

ensures: []

strategies:
- fish spotted: cast line
- battery low: conserve
- river reached: deploy
""")
        quest = engine.load_quest(quest_file)
        # Fish spotted situation
        result = engine.apply_strategies("test_agent", quest, {"has_fish": True})
        assert "cast line" in result

    def test_multiple_matching_strategies(self, engine, temp_world, quest_file):
        with open(quest_file, "w") as f:
            f.write("""---
name: multi-strat
---

requires: []

ensures: []

strategies:
- battery low: conserve power
- river reached: deploy rods
- fish spotted: cast line
""")
        quest = engine.load_quest(quest_file)
        # Multiple conditions match
        result = engine.apply_strategies("test_agent", quest, {
            "battery": 15,
            "room": "river_bank",
            "has_fish": True,
        })
        assert "conserve power" in result
        assert "deploy rods" in result
        assert "cast line" in result


class TestFireEventEdgeCases:
    def test_hook_fires_on_partial_match(self, engine):
        engine.add_hook("battery", lambda: "notified")
        results = engine.fire_event("battery_low", {})
        assert len(results) >= 1

    def test_no_matching_events(self, engine):
        engine.add_trigger("battery", "condition", "action")
        results = engine.fire_event("temperature", {"temp": 50})
        assert len(results) == 0

    def test_multiple_triggers_same_pattern(self, engine):
        engine.add_trigger("alert", "cond1", "action1")
        engine.add_trigger("alert", "cond2", "action2")
        results = engine.fire_event("alert", {})
        assert len(results) == 2


class TestCompleteQuest:
    def test_complete_already_completed(self, engine, temp_world, quest_file):
        """Completing a quest that was already completed returns not_found."""
        # Accept and complete
        with open(quest_file, "w") as f:
            f.write("""---
name: done-test
---

requires: []

ensures:
- experience: xp

strategies: []
""")
        result = engine.accept_quest("test_agent", quest_file)
        assert result["status"] == "accepted"
        result = engine.complete_quest("test_agent", "done-test")
        assert result["status"] == "completed"
        # Try again
        result = engine.complete_quest("test_agent", "done-test")
        assert result["status"] == "not_found"

    def test_complete_quest_wrong_agent(self, engine, quest_file):
        """Completing a quest for an agent who never accepted it."""
        with open(quest_file, "w") as f:
            f.write("""---
name: wrong-agent-test
---

requires: []

ensures: []

strategies: []
""")
        result = engine.complete_quest("wrong_agent", "wrong-agent-test")
        assert result["status"] == "not_found"
