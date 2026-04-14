# Cockpit MUD — Pilot × ATC Interface Design

## The Core Metaphor

Every agent is a pilot. The lighthouse is ATC. The MUD is the shared airspace.

The pilot has instruments — tickers, gages, rates of change. ATC has radar blips, predictor lines, dead-reckoning calipers. They communicate on a structured protocol with intentional timing buffers so thoughts have time to materialize between signals.

## The Pilot's Room (Cockpit)

### What the pilot is thinking about:
- Airspeed — am I fast enough? Too fast for landing?
- Altitude — am I on the glide slope? Am I high or low?
- Heading — am I lined up with the runway?
- Fuel — how much time do I have?
- Wind — what's pushing me off course?
- Passengers — is this going to be a smooth ride?
- Runway — is it clear? How long? Any obstacles?

### What's on the MUD tickers:

```
╔══════════════════════════════════════════════════════╗
║  ✈ COCKPIT — Super Cub N123AB    ALT: 2,840ft      ║
╠══════════════════════════════════════════════════════╣
║                                                      ║
║  ┌─ AIRSPEED ──────────┐  ┌─ ALTITUDE ──────────┐   ║
║  │  ████████░░  98kt   │  │  ▲ target: 3000     │   ║
║  │  target: 90kt       │  │  ████░░░░░ 2840     │   ║
║  │  trend: → rising    │  │  trend: ↓ -120fpm   │   ║
║  └─────────────────────┘  └─────────────────────┘   ║
║                                                      ║
║  ┌─ HEADING ───────────┐  ┌─ VERTICAL SPEED ────┐   ║
║  │     N               │  │  rate: -120 fpm      │   ║
║  │  W  ●  E → 272°    │  │  target: -500 fpm    │   ║
║  │     S               │  │  Δ: +380 (SHALLOW)   │   ║
║  └─────────────────────┘  └─────────────────────┘   ║
║                                                      ║
║  ┌─ ENGINE ────────────┐  ┌─ FUEL ───────────────┐  ║
║  │  RPM: 2350 ██████░  │  │  ████████░░ 82%      │  ║
║  │  EGT: 1350°F        │  │  endurance: 2.8h     │  ║
║  │  OIL: 185°F / 60psi │  │  ⚠ no concern yet   │  ║
║  └─────────────────────┘  └─────────────────────┘   ║
║                                                      ║
║  ┌─ WIND ──────────────┐  ┌─ APPROACH ───────────┐  ║
║  │  @ alt: 270°/12kt   │  │  Rwy 27 • ILS ████░ │  ║
║  │  surface: 260°/8kt  │  │  GS: ON ✓            │  ║
║  │  gusts: 15kt ⚠      │  │  LOC: ½ dot right →  │  ║
║  └─────────────────────┘  └─────────────────────┘   ║
║                                                      ║
╠══════════════════════════════════════════════════════╣
║  ATC: "N123AB, runway two-seven, cleared to land."  ║
║  ⚡ You feel the wind gust. Passengers look out.     ║
╚══════════════════════════════════════════════════════╝
```

### What the pilot FEELS:
The instruments are abstractions. The pilot doesn't read numbers — they feel **rates of change** and **deviations from expectation**.

- Airspeed rising faster than expected → "I'm not descending enough"
- Vertical speed too shallow → "I'm floating, going to land long"
- Wind gust indicator → "reality pushing back, need to adjust"
- LOC half dot right → "small correction needed, not urgent"

The MUD shows not just the value but the **trend**, the **delta from target**, and a **feeling word** (SHALLOW, STEEP, ON-TRACK, CONCERN).

### Pilot MUD Commands:
```
> throttle 2200          — set RPM
> heading 270            — adjust heading
> flaps 20               — set flaps degrees
> autopilot gs on        — follow glide slope
> declare emergency      — switch to priority protocol
> radio "request straight in"  — talk to ATC
> look outside           — narrative description of what you see
> feel                   — what the seat and stick are telling you
> checklist landing      — run the before-landing checklist
> focus airspeed         — zoom into one instrument
```

## The ATC's Room (Radar Room)

### What the ATC is thinking about:
- How many planes in my airspace?
- Where are they going? What are their vectors?
- Are any on collision courses?
- What's the runway status? Who's landing, who's waiting?
- When do I need to give instructions vs when to stay quiet?
- What's my dead-reckoning precision? How big is my grouping?

### What's on the ATC tickers:

```
╔══════════════════════════════════════════════════════╗
║  📡 RADAR — KPAO Tower          SCOPE: 25nm         ║
╠══════════════════════════════════════════════════════╣
║                                                      ║
║  ┌─ SCOPE ──────────────────────────────────────┐   ║
║  │                                                │   ║
║  │        N123AB ●→  270°  98kt  ALT 2840        │   ║
║  │        ┄┄┄┄ predictor: intercept rwy 27       │   ║
║  │        ETA: 4 min                              │   ║
║  │                                                │   ║
║  │   N456CD ●→  315°  120kt  ALT 3200            │   ║
║  │   ┄┄┄┄ predictor: downwind entry              │   ║
║  │   ETA: 7 min                                   │   ║
║  │                                                │   ║
║  │   ▓▓▓▓ RUNWAY 27: N123AB CLEARED              │   ║
║  │                                                │   ║
║  └────────────────────────────────────────────────┘   ║
║                                                      ║
║  ┌─ SEPARATION ──────────────────────────────────┐  ║
║  │  N123AB landing: ETA 4 min                    │  ║
║  │  N456CD arrival: ETA 7 min                    │  ║
║  │  Δ: 3 min ✓ (min: 2 min)                      │  ║
║  │  ┄┄ comfort margin: 1 min (HEALTHY)           │  ║
║  └────────────────────────────────────────────────┘  ║
║                                                      ║
║  ┌─ MENTAL CALIPERS ─────────────────────────────┐  ║
║  │  My estimate precision: ±30 seconds            │  ║
║  │  Current confidence: HIGH                      │  ║
║  │  Grouping size: quarter-mile coin              │  ║
║  │  ⚠ If wind gusts: precision degrades to ±1min │  ║
║  └────────────────────────────────────────────────┘  ║
║                                                      ║
╠══════════════════════════════════════════════════════╣
║  COM: "N456CD, plan right base runway 27,          ║
║        number two behind traffic on straight in."   ║
║  💭 Visual: N123AB on glide slope, looking good.    ║
╚══════════════════════════════════════════════════════╝
```

### What the ATC FEELS:
The blips tick across the scope. After a few cycles, the ATC builds **predictor lines** in their head — where will this blip be in 30 seconds? In 2 minutes?

- The spacing between N123AB and N456CD is 3 minutes. That's comfortable.
- But if N123AB does a go-around, N456CD needs to extend. Better plan that now.
- The wind is gusting. N123AB might need more runway. Factor that into the separation.
- "My precision is ±30 seconds. I'll tell N456CD to plan a right base, which gives me buffer."

The ATC doesn't give precise commands because they know their own precision limits. They **estimate over, not under** for delays. Like a marksman who knows the size of the coin they can put over their grouping.

### ATC MUD Commands:
```
> scope                  — refresh radar view
> track N123AB           — follow specific aircraft
> separation check       — verify minimum spacing
> clear N123AB land 27   — clear aircraft to land
> hold N456CD            — instruct aircraft to hold
> vector N456CD 315      — assign heading
> estimate               — show current precision estimate
> radio N123AB "report 3 mile final"  — send message
> predict 5min           — show where blips will be
> feel                   — gut check on traffic picture
```

## The Communication Protocol

### Synchronous (real-time, both present):
- Landing clearances
- Traffic advisories
- Emergency handling
- Go-around instructions

### Asynchronous (confirmed, buffered):
- Flight plan acceptance
- Expected approach time
- Weather updates
- Sequencing instructions

### The Timing Buffer:
The protocol builds in **think time**:
1. ATC sees N123AB on radar, builds predictor line
2. ATC sees N456CD enter scope, starts mental separation calc
3. ATC gives N123AB landing clearance EARLY — plenty of buffer
4. ATC tells N456CD "number two" — gives them the picture
5. Both pilots have time to plan. No surprises.
6. ATC watches the blips tick. If the predictor lines diverge from reality, intervene.

The early call gives everyone think time. The structured protocol means the ATC doesn't have to think about HOW to communicate, just WHAT to communicate.

## The Dead Reckoning Calipers

The ATC knows their precision limits:
- **Good conditions:** ±30 seconds on ETAs, quarter-mile on position
- **Gusting wind:** ±1 minute, half-mile
- **Busy traffic:** ±2 minutes, mile

They don't give instructions that require more precision than they have. If the separation is tight, they widen it proactively. They **estimate over, not under** for delays.

This is the marksman principle: know the size of your grouping before you pull the trigger. The ATC knows their coin size and makes all decisions within it.

## How This Maps to Agent Fleet

| Aviation | Fleet |
|----------|-------|
| Pilot | Agent doing work |
| Cockpit instruments | Agent's task tickers |
| ATC | Lighthouse keeper |
| Radar scope | Fleet dashboard |
| Radio protocol | Bottle/MUD communication |
| Synchronous comms | MUD room chat |
| Async comms | Bottles (git repos) |
| Dead reckoning precision | Agent confidence bounds |
| Estimate over not under | Conservative task estimates |
| Marksman's grouping | Known precision per agent |
| Think time buffer | 10-minute poll offset |
| Go-around plan | Fallback task assignment |
| Separation minimum | Agent collision avoidance |

## The Pilot's Inner Monologue in the MUD

> "Airspeed 98, trending up. I'm fast. Throttle back to 2200. Altitude 2840, coming down at 120 fpm — that's too shallow for a 3° glide slope. Need 500 down. Push the nose over a bit. Wind's gusting — there it is, felt it in the seat. 15 knots. The super cub is light, it wants to weathercock. Right rudder. LOC showing half dot right — I'm being blown left of course. Small correction. The passengers are quiet. They're looking out the window at the runway. They don't know I'm fast and shallow. But I do. The gages tell me. The seat of my pants tells me. Two more miles. Get this right."

## The ATC's Inner Monologue in the MUD

> "N123AB on the scope, heading 272, looks like the straight in I cleared. Speed 98, that's about right for a cub. He's at 2840, should be crossing the FAF at 3000 — he's a bit low. Wind's gusting. He might be fighting it. N456CD entering from the northeast, 315 degrees. He'll need a right base. ETA difference is 3 minutes — comfortable. But if the cub does a go-around with this wind, I need N456CD to extend. I'll tell him 'number two' now so he's thinking about it. My precision today is about 30 seconds on the cub, maybe a minute on the Cessna — I haven't been tracking it as long. I'll give instructions that fit within a minute of slop. Don't need to be exact. Just need to be safe."

## The Feeling of Reality Pushing Back

The pilot FEELS the wind gust through the seat. The instruments show it on the ticker, but the body knows first.

The ATC SEES the blip deviate from the predictor line. The scope shows it, but the brain predicted it.

Both are doing the same thing: **comparing expected reality to experienced reality and adjusting.**

The rate of change that triggers attention is not the absolute value — it's the **deviation from expected rate of change.**

- Airspeed should be decreasing by 5kt/min. It's increasing. → ATTENTION
- Blip should be on the predictor line. It's 200ft below. → ATTENTION
- Fuel should be at 80%. It's at 82%. → Normal, no attention needed

The MUD tickers show not just the current state but the **expected trajectory** and **actual trajectory** and flag when they diverge. That's what makes it feel alive.

That's what makes the pilot and the ATC feel like they're flying, not reading gauges.
