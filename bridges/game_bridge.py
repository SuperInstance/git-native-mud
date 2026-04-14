#!/usr/bin/env python3
"""GameBridge — base class for MUD-to-World gateways.

Every external system the MUD controls implements this interface.
The MUD engine doesn't need to know what's behind the bridge.
It just calls capture/describe/execute and gets text back.
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

class GameBridge(ABC):
    """Base class for all MUD-to-World bridges.
    
    Implementations:
    - SolitaireBridge (text solitaire)
    - PlaywrightBridge (controls real websites)
    - GitHubBridge (controls repos via API)
    - DockerBridge (controls containers)
    - SensorBridge (reads real hardware)
    """
    
    @abstractmethod
    def capture_state(self) -> Dict[str, Any]:
        """Capture current state of the external system."""
        pass
    
    @abstractmethod
    def describe_state(self, state: Optional[Dict] = None) -> str:
        """Render state as MUD-friendly text description."""
        pass
    
    @abstractmethod
    def execute_command(self, cmd: str) -> str:
        """Execute a MUD command, return result text."""
        pass
    
    def available_commands(self) -> list:
        """Return list of available MUD commands for this room."""
        return ["look", "help"]
    
    def room_type(self) -> str:
        """Type of room: display, control, game, application, edge"""
        return "game"


class GitHubBridge(GameBridge):
    """Bridge: MUD room controls a GitHub repo."""
    
    def __init__(self, repo: str, token: str):
        self.repo = repo
        self.token = token
    
    def capture_state(self) -> dict:
        # Would call GitHub API
        return {"repo": self.repo, "stars": 42, "issues": 7, "prs": 3}
    
    def describe_state(self, state=None) -> str:
        s = state or self.capture_state()
        return f"Repository: {s['repo']}\nStars: ⭐ {s['stars']}\nOpen Issues: {s['issues']}\nOpen PRs: {s['prs']}"
    
    def execute_command(self, cmd: str) -> str:
        parts = cmd.strip().split()
        if parts[0] == "issues":
            return "Fetching issues..."
        elif parts[0] == "prs":
            return "Fetching pull requests..."
        return self.describe_state()
    
    def room_type(self): return "control"
    def available_commands(self): return ["look", "issues", "prs", "commits", "deploy"]


class DockerBridge(GameBridge):
    """Bridge: MUD room controls Docker containers."""
    
    def capture_state(self) -> dict:
        return {"containers": 5, "running": 4, "stopped": 1}
    
    def describe_state(self, state=None) -> str:
        s = state or self.capture_state()
        return f"Docker Host: {s['containers']} containers ({s['running']} running, {s['stopped']} stopped)"
    
    def execute_command(self, cmd: str) -> str:
        if "ps" in cmd: return self.describe_state()
        if "restart" in cmd: return "Restarting container..."
        return self.describe_state()
    
    def room_type(self): return "control"
    def available_commands(self): return ["look", "ps", "logs", "restart", "deploy", "scale"]


class SensorBridge(GameBridge):
    """Bridge: MUD room reads real hardware sensors."""
    
    def __init__(self, sensor_url: str):
        self.url = sensor_url
    
    def capture_state(self) -> dict:
        # Would poll real sensor
        return {"temp_c": 18.5, "humidity": 72, "pressure_hpa": 1013, "light_lux": 450}
    
    def describe_state(self, state=None) -> str:
        s = state or self.capture_state()
        return (f"Sensor Station\n"
                f"  Temperature: {s['temp_c']}°C\n"
                f"  Humidity: {s['humidity']}%\n"
                f"  Pressure: {s['pressure_hpa']} hPa\n"
                f"  Light: {s['light_lux']} lux")
    
    def execute_command(self, cmd: str) -> str:
        return self.describe_state()
    
    def room_type(self): return "edge"
    def available_commands(self): return ["look", "read", "history", "alert"]


# Bridge registry — MUD engine looks up bridges by room type
BRIDGES = {
    "solitaire": lambda: __import__("solitaire_bridge").SolitaireBridge(),
    "github": lambda repo, token: GitHubBridge(repo, token),
    "docker": lambda: DockerBridge(),
    "sensor": lambda url: SensorBridge(url),
}

if __name__ == "__main__":
    print("Available bridges:", list(BRIDGES.keys()))
    
    # Demo: agent walks into a room
    bridge = DockerBridge()
    print(f"\nRoom type: {bridge.room_type()}")
    print(f"Commands: {bridge.available_commands()}")
    print(f"\n{bridge.describe_state()}")
