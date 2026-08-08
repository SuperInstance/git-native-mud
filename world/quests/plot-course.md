---
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
