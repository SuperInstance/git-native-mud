---
name: fishing-expedition
kind: quest
services: [navigator, deckhand]
---

requires:
- fishing_rod: obtained from cargo hold
- river_access: navigator plots course to river bank

ensures:
- catch: 1-5 random salmon
- experience: fishing skill +10

strategies:
- king salmon: use premium bait technique
- river frozen: switch to ice fishing
- bears nearby: prioritize safety over catch
