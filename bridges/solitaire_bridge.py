#!/usr/bin/env python3
"""Solitaire Bridge — MUD commands control a real solitaire game.

Proof of concept for the MUD-to-World Gateway.
Uses pure Python (no browser needed for text mode).
Playwright version would screenshot an actual solitaire website.

Two modes:
1. Text mode: pure Python Klondike, no browser needed
2. Browser mode: controls real solitaire game via Playwright
"""
import random, json, os
from typing import List, Optional, Tuple

SUITS = ["♥", "♠", "♦", "♣"]
RANKS = ["A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"]
RANK_VALUES = {r: i for i, r in enumerate(RANKS)}

class Card:
    def __init__(self, suit, rank, face_up=False):
        self.suit = suit
        self.rank = rank
        self.face_up = face_up
    
    def is_red(self): return self.suit in ["♥", "♦"]
    def value(self): return RANK_VALUES[self.rank]
    
    def __repr__(self):
        return f"{self.rank}{self.suit}" if self.face_up else "[XX]"
    
    def to_dict(self):
        return {"suit": self.suit, "rank": self.rank, "face_up": self.face_up}


class SolitaireGame:
    """Full Klondike Solitaire — text-playable, MUD-controllable."""
    
    def __init__(self):
        self.stock: List[Card] = []
        self.waste: List[Card] = []
        self.foundations: List[List[Card]] = [[] for _ in range(4)]
        self.tableau: List[List[Card]] = [[] for _ in range(7)]
        self.score = 0
        self.moves = 0
        self.new_game()
    
    def new_game(self):
        deck = [Card(s, r) for s in SUITS for r in RANKS]
        random.shuffle(deck)
        
        self.tableau = [[] for _ in range(7)]
        for i in range(7):
            for j in range(i + 1):
                card = deck.pop()
                card.face_up = (j == i)
                self.tableau[i].append(card)
        
        self.stock = deck
        self.waste = []
        self.foundations = [[] for _ in range(4)]
        self.score = 0
        self.moves = 0
    
    def draw(self) -> bool:
        if not self.stock:
            if self.waste:
                self.stock = list(reversed(self.waste))
                for c in self.stock: c.face_up = False
                self.waste = []
                return True
            return False
        card = self.stock.pop()
        card.face_up = True
        self.waste.append(card)
        self.moves += 1
        return True
    
    def can_move_to_foundation(self, card: Card, found_idx: int) -> bool:
        pile = self.foundations[found_idx]
        if not pile:
            return card.rank == "A"
        top = pile[-1]
        return card.suit == top.suit and card.value() == top.value() + 1
    
    def can_move_to_tableau(self, card: Card, col_idx: int) -> bool:
        col = self.tableau[col_idx]
        if not col:
            return card.rank == "K"
        top = col[-1]
        if not top.face_up: return False
        return card.is_red() != top.is_red() and card.value() == top.value() - 1
    
    def move_waste_to_foundation(self, found_idx: int) -> bool:
        if not self.waste: return False
        card = self.waste[-1]
        if self.can_move_to_foundation(card, found_idx):
            self.waste.pop()
            self.foundations[found_idx].append(card)
            self.score += 10
            self.moves += 1
            return True
        return False
    
    def move_waste_to_tableau(self, col_idx: int) -> bool:
        if not self.waste: return False
        card = self.waste[-1]
        if self.can_move_to_tableau(card, col_idx):
            self.waste.pop()
            self.tableau[col_idx].append(card)
            self.score += 5
            self.moves += 1
            return True
        return False
    
    def move_tableau_to_foundation(self, col_idx: int, found_idx: int) -> bool:
        col = self.tableau[col_idx]
        if not col: return False
        card = col[-1]
        if not card.face_up: return False
        if self.can_move_to_foundation(card, found_idx):
            col.pop()
            self.foundations[found_idx].append(card)
            self.score += 10
            self.moves += 1
            self._flip_top(col_idx)
            return True
        return False
    
    def move_tableau_to_tableau(self, from_col: int, to_col: int, count: int = 1) -> bool:
        src = self.tableau[from_col]
        if not src: return False
        
        # Find the card to move (count cards from bottom of face-up stack)
        face_up_start = len(src) - 1
        while face_up_start > 0 and src[face_up_start - 1].face_up:
            face_up_start -= 1
        
        move_start = len(src) - count
        if move_start < face_up_start: return False
        
        card = src[move_start]
        if self.can_move_to_tableau(card, to_col):
            cards = src[move_start:]
            del src[move_start:]
            self.tableau[to_col].extend(cards)
            self.moves += 1
            self._flip_top(from_col)
            return True
        return False
    
    def auto_foundation(self) -> int:
        """Auto-move obvious cards to foundation. Returns count moved."""
        moved = 0
        changed = True
        while changed:
            changed = False
            # Try waste
            if self.waste:
                for fi in range(4):
                    if self.can_move_to_foundation(self.waste[-1], fi):
                        self.move_waste_to_foundation(fi)
                        moved += 1
                        changed = True
                        break
            # Try tableau tops
            for ci in range(7):
                col = self.tableau[ci]
                if col and col[-1].face_up:
                    for fi in range(4):
                        if self.can_move_to_foundation(col[-1], fi):
                            self.move_tableau_to_foundation(ci, fi)
                            moved += 1
                            changed = True
                            break
        return moved
    
    def _flip_top(self, col_idx: int):
        col = self.tableau[col_idx]
        if col and not col[-1].face_up:
            col[-1].face_up = True
            self.score += 5
    
    def is_won(self) -> bool:
        return all(len(f) == 13 for f in self.foundations)
    
    def describe(self) -> str:
        """Generate MUD-friendly text description of game state."""
        lines = []
        lines.append("╔══════════════════════════════════════════╗")
        lines.append("║          ♠ SOLITAIRE ROOM ♠              ║")
        lines.append("╠══════════════════════════════════════════╣")
        
        # Stock and waste
        stock_count = len(self.stock)
        waste_top = str(self.waste[-1]) if self.waste else "---"
        lines.append(f"║  Stock: [{stock_count} cards]  Waste: {waste_top:<6}       ║")
        
        # Foundations
        found_str = " ".join(f"{str(f[-1]) if f else '___':>4}" for f in self.foundations)
        lines.append(f"║  Foundation: {found_str}            ║")
        
        lines.append("╠══════════════════════════════════════════╣")
        lines.append("║  Tableau:                                 ║")
        
        for i, col in enumerate(self.tableau):
            cards_str = " ".join(str(c) for c in col) if col else "(empty)"
            lines.append(f"║  Col {i+1}: {cards_str}")
        
        lines.append("╠══════════════════════════════════════════╣")
        lines.append(f"║  Score: {self.score}  Moves: {self.moves}  {'🎉 WON!' if self.is_won() else ''}      ║")
        lines.append("╚══════════════════════════════════════════╝")
        lines.append("")
        lines.append("Commands: draw | move waste to foundation|tableau N | move col N to foundation|col N | auto | new | look")
        
        return "\n".join(lines)
    
    def state_json(self) -> dict:
        return {
            "stock": len(self.stock),
            "waste": [c.to_dict() for c in self.waste],
            "foundations": [[c.to_dict() for c in f] for f in self.foundations],
            "tableau": [[c.to_dict() for c in col] for col in self.tableau],
            "score": self.score,
            "moves": self.moves,
            "won": self.is_won()
        }


class SolitaireBridge:
    """Bridge between MUD commands and SolitaireGame.
    
    This is the pattern that generalizes to ANY external application:
    - capture_state() → get current state
    - describe_state() → render as MUD text
    - execute_command() → translate MUD command to action
    """
    
    def __init__(self):
        self.game = SolitaireGame()
    
    def capture_state(self) -> dict:
        return self.game.state_json()
    
    def describe_state(self, state=None) -> str:
        return self.game.describe()
    
    def execute_command(self, cmd: str) -> str:
        """Execute a MUD command, return result text."""
        parts = cmd.lower().strip().split()
        
        if not parts:
            return self.describe_state()
        
        if parts[0] == "look":
            return self.describe_state()
        
        elif parts[0] == "draw":
            if self.game.draw():
                return f"Drew {self.game.waste[-1]}\n" + self.describe_state()
            return "Stock empty, waste recycled.\n" + self.describe_state()
        
        elif parts[0] == "new":
            self.game.new_game()
            return "New game started.\n" + self.describe_state()
        
        elif parts[0] == "auto":
            moved = self.game.auto_foundation()
            return f"Auto-moved {moved} cards.\n" + self.describe_state()
        
        elif parts[0] == "score":
            return f"Score: {self.game.score}, Moves: {self.game.moves}"
        
        elif parts[0] == "move":
            # move waste to foundation N
            if "waste" in parts and "foundation" in parts:
                fi = int(parts[-1]) - 1
                if self.game.move_waste_to_foundation(fi):
                    return f"Moved to foundation.\n" + self.describe_state()
                return "Can't move that card there."
            
            # move waste to tableau N
            elif "waste" in parts and "tableau" in parts:
                ci = int(parts[-1]) - 1
                if self.game.move_waste_to_tableau(ci):
                    return f"Moved to tableau.\n" + self.describe_state()
                return "Can't move that card there."
            
            # move col N to foundation M
            elif "col" in parts and "foundation" in parts:
                ci = int(parts[parts.index("col")+1]) - 1
                fi = int(parts[-1]) - 1
                if self.game.move_tableau_to_foundation(ci, fi):
                    return f"Moved to foundation.\n" + self.describe_state()
                return "Can't move that card there."
            
            # move col N to col M
            elif "col" in parts:
                ci = int(parts[parts.index("col")+1]) - 1
                to_idx = parts.index("to")
                ti = int(parts[to_idx+1].replace("col","")) - 1 if "col" in parts[to_idx+1] else int(parts[-1]) - 1
                if self.game.move_tableau_to_tableau(ci, ti):
                    return f"Moved cards.\n" + self.describe_state()
                return "Can't move those cards there."
        
        elif parts[0] == "hint":
            # Simple hint: find first valid move
            # Try auto-foundation first
            for ci in range(7):
                col = self.game.tableau[ci]
                if col and col[-1].face_up:
                    for fi in range(4):
                        if self.game.can_move_to_foundation(col[-1], fi):
                            return f"Hint: move {col[-1]} from col {ci+1} to foundation {fi+1}"
            # Try waste to foundation
            if self.game.waste:
                for fi in range(4):
                    if self.game.can_move_to_foundation(self.game.waste[-1], fi):
                        return f"Hint: move {self.game.waste[-1]} from waste to foundation {fi+1}"
            return "Hint: try drawing from stock"
        
        return f"Unknown command: {cmd}. Try: look, draw, move, auto, hint, new, score"


if __name__ == "__main__":
    bridge = SolitaireBridge()
    print(bridge.describe_state())
    print()
    
    # Simulate an agent playing
    commands = ["draw", "draw", "hint", "auto", "look", "score"]
    for cmd in commands:
        print(f"> {cmd}")
        result = bridge.execute_command(cmd)
        # Just show first 3 lines of result
        lines = result.split("\n")[:3]
        for l in lines:
            print(f"  {l}")
        print()
    
    # Save state for MUD room
    state = bridge.capture_state()
    os.makedirs("world/rooms", exist_ok=True)
    with open("world/rooms/solitaire_state.json", "w") as f:
        json.dump(state, f, indent=2)
    print("Game state saved to world/rooms/solitaire_state.json")
