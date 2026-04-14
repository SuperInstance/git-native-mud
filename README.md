# Git-Native MUD 🔮

**The repo IS the world. Commits ARE actions. No server needed.**

## Play
```bash
# Write a command
echo 'move: north' > world/commands/$(whoami).yaml
git add . && git commit -m "my move" && git push
# GitHub Actions processes the turn automatically
```

## Commands
`move: north` `take: fishing_rod` `drop: compass` `attack: scout` `say: "hello"` `fish: true` `scan: true` `wait: true`

## Map
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

## Rules
- Battery: -2%/move, -1-3%/action, 0%/wait
- Combat: d20 + bonuses
- Fishing: river + rod = random salmon
- Day/night every 20 turns
