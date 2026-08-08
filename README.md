# Lightshift

> **Linux-native smart-light control built around intent, capability, and verification.**

Lightshift is a local control plane for smart lighting.

It discovers lighting devices, builds a normalized picture of what each device can actually do, and turns Linux-side input into deliberate scene changes.

The important part is not just *sending a command to a light*.

Lightshift is built around a fuller loop:

```text
observe
   ↓
identify capability
   ↓
express intent
   ↓
build a plan
   ↓
apply
   ↓
verify
   ↓
report what actually happened
```

A scene should not be considered successful merely because the program survived.

**Discover the system. Define the scene. Shift the light.**

---

## Why

Most smart-light systems work really well inside their own ecosystem.

The problem gets more interesting when I want the lights to behave like part of the Linux environment itself.

I want to be able to do things like:

```bash
lumenctl scene apply vec-lock
```

or:

```bash
lumenctl adjust area:office --brightness +5
```

and eventually bind those same intents to:

* keyboard shortcuts;
* a macro pad;
* rotary controls;
* desktop state;
* scripts;
* other local automation.

I also don't want the scene engine to care whether the light behind an alias happens to be Hue, WLED, or something exposed through Home Assistant.

That leads to the central Lightshift idea:

```text
Linux input expresses intent.

Lightshift determines what that intent means.

The provider determines how the hardware gets there.
```

---

# Current status

**Early development.**

The project is currently establishing its models, CLI, logging, configuration boundaries, and fake-device path before talking seriously to real hardware.

The first target is intentionally narrow:

```text
Linux machine
    ↓
discover one light
    ↓
identify its capabilities
    ↓
build one portable scene
    ↓
dry-run the execution plan
    ↓
apply it
    ↓
read the resulting state
    ↓
report whether reality matched the request
```

Before that path touches a real light, the same flow should work against a deterministic fake provider.

Current work includes:

* normalized device, capability, state, command, and result models;
* `lumenctl` CLI scaffolding;
* runtime configuration;
* independent console and DEBUG-file logging;
* per-run metadata and log identity;
* provider abstraction planning;
* scene/config format design;
* failure-state and degraded-operation modeling.

Device discovery and real provider execution are not implemented yet.

---

# Design thesis

Lightshift separates five things that are easy to accidentally blur together:

```text
CAPABILITY
    what the device CAN do

STATE
    what the device IS doing

INTENT
    what the operator wants

COMMAND
    what Lightshift asks the hardware to do

RESULT
    evidence of what actually happened
```

That distinction drives most of the architecture.

A color-capable light, for example, might advertise:

```text
temperature ........ supported
CIE xy color ....... supported
effects ............ candle, prism
mirek range ........ 153–500
```

while its current state may be:

```text
power .............. ON
brightness ......... 82%
temperature ........ 275 mirek
color .............. not active
```

Those are different facts.

Lightshift tries to preserve that distinction all the way through execution.

---

# Architecture

The intended flow looks roughly like this:

```text
                       ┌─────────────────────┐
                       │     Linux input     │
                       │                     │
                       │ CLI / shortcut /    │
                       │ keypad / encoder    │
                       └──────────┬──────────┘
                                  │
                                  ▼
                       ┌─────────────────────┐
                       │     InputIntent     │
                       └──────────┬──────────┘
                                  │
                                  ▼
                       ┌─────────────────────┐
                       │    Scene engine     │
                       │                     │
                       │ parse               │
                       │ validate            │
                       │ resolve targets     │
                       │ build plan          │
                       └──────────┬──────────┘
                                  │
                                  ▼
                       ┌─────────────────────┐
                       │ Capability layer    │
                       │                     │
                       │ power               │
                       │ brightness          │
                       │ color temperature   │
                       │ CIE xy / RGB        │
                       │ effects             │
                       │ transitions         │
                       └──────────┬──────────┘
                                  │
                                  ▼
                       ┌─────────────────────┐
                       │ Provider interface  │
                       └──────┬───────┬──────┘
                              │       │
                 ┌────────────┘       └────────────┐
                 ▼                                 ▼
       ┌──────────────────┐              ┌──────────────────┐
       │ Home Assistant   │              │   Direct Hue     │
       │                  │              │     later        │
       └────────┬─────────┘              └────────┬─────────┘
                │                                 │
                └──────────────┬──────────────────┘
                               ▼
                     ┌──────────────────┐
                     │ Physical lights  │
                     └──────────────────┘
```

The scene engine should never need to know how a Hue API payload is shaped.

Likewise, the keyboard handler should never need to know whether a lamp supports CIE xy.

Each layer gets a bounded problem.

---

# Device model

A normalized Lightshift device is intended to look roughly like:

```python
LightDevice(
    name="Office Key",
    device_id="light.office_key",
    device_type="bulb",
    device_rev="1.0",
    handle="office-key",
    manufacturer="Philips Hue",
    capabilities=...,
    state=...,
)
```

A human-friendly handle such as:

```text
office-key
desk-fill
bedside
```

is kept separate from whatever identifier the provider uses.

That means scenes can remain readable and relatively portable even if the underlying provider changes.

---

# Scenes

Scenes describe **desired state**, not vendor-specific commands.

Planned scene configuration uses TOML:

```toml
schema_version = 1

[scenes.vec-lock]
description = "Focused technical work with bounded peripheral light."
transition_ms = 700

[[scenes.vec-lock.targets]]
selector = "office-key"
power = true
brightness = 82
color_temp_kelvin = 3900

[[scenes.vec-lock.targets]]
selector = "office-fill"
power = true
brightness = 18
color = "#163252"
```

Another scene can express a different environment using the same device model:

```toml
[scenes.jess-glow]
description = "Warm, expressive room state."
transition_ms = 1100

[[scenes.jess-glow.targets]]
selector = "area:office"
power = true
brightness = 52
color_temp_kelvin = 2750
```

The interesting work happens between authored intent and hardware:

```text
scene
  ↓
resolve selectors
  ↓
inspect capabilities
  ↓
reject / skip / approximate unsupported values
  ↓
produce deterministic command plan
  ↓
apply
```

---

# `lumenctl`

The command-line interface is named:

```text
lumenctl
```

The initial CLI foundation is being built now.

The intended interface includes:

```bash
# Discover supported devices
lumenctl discover

# Inspect known devices
lumenctl devices
lumenctl devices --verbose

# List available scenes
lumenctl scene list

# Inspect a scene without executing it
lumenctl scene inspect vec-lock

# Compile the complete plan without changing hardware
lumenctl scene apply vec-lock --dry-run

# Apply a scene
lumenctl scene apply vec-lock

# Direct device control
lumenctl set office-key --brightness 70

# Relative adjustment
lumenctl adjust area:office --brightness +5
```

The goal is for that CLI to remain the stable operator boundary even as new input methods are added later.

A keyboard shortcut, for example, should ultimately express the same intent as the equivalent CLI command rather than creating another lighting-control path.

---

# Dry-run first

`--dry-run` is intended to be a real execution path, not a decorative flag.

It should perform:

```text
configuration parsing
        ↓
scene validation
        ↓
target resolution
        ↓
capability checks
        ↓
command generation
        ↓
execution-plan reporting
```

and stop only before hardware mutation.

Example:

```text
SCENE PLAN ⟡ vec-lock

office-key
  power ............ ON
  brightness ....... 82%
  temperature ...... 3900 K

office-fill
  power ............ ON
  brightness ....... 18%
  color ............ #163252

desk-right
  unavailable ...... command skipped

PLAN STATUS ⟡ DEGRADED
```

The dry-run should tell me what Lightshift **believes** will happen before I give it authority to make it happen.

---

# Failure is part of the model

Smart-home devices disappear.

Networks get weird.

A bridge responds while one lamp doesn't.

A device advertises a capability but fails to execute it.

Those aren't exceptional enough to pretend they don't exist.

Lightshift therefore uses explicit operation states:

```text
OK
SKIPPED
DEGRADED
INVALID
RECOVERABLE
FATAL
```

The intent is to distinguish:

```text
one lamp failed
```

from:

```text
the entire operation is meaningless
```

A scene containing six lights should not necessarily abort because the fifth one is offline.

Instead:

```text
SCENE APPLY ⟡ vec-lock

OK ............. office-key
OK ............. office-fill
OK ............. desk-left
OK ............. monitor-back
RECOVERABLE .... desk-right — unavailable
SKIPPED ........ bedside — already off

STATUS ........ DEGRADED
```

That is a much more useful answer than either:

```text
success
```

or:

```text
failed
```

---

# Observe → command → verify

The control loop I want Lightshift to preserve is:

```text
OBSERVE
current device state

    ↓

COMMAND
requested transition

    ↓

ACKNOWLEDGE
did the provider/hardware receive it?

    ↓

OBSERVE AGAIN
what state does the system now report?

    ↓

COMPARE
requested vs. observed

    ↓

REPORT
what can Lightshift actually claim?
```

Requested state and observed state are not the same piece of evidence.

That distinction matters.

---

# Logging

Lightshift currently uses separate logging thresholds for the operator console and logfile.

The basic model is:

```text
                    application logger
                           │
                    root = DEBUG
                      /          \
                     /            \
              console             file
           selected level         DEBUG
```

Normal execution can stay readable:

```text
INFO and above
```

while the logfile preserves:

```text
DEBUG and above
```

`--verbose` changes what the operator sees.

It should not reduce what the system preserves.

Run logs are currently written under:

```text
output/
```

with per-run timestamps in the filename.

---

# Provider strategy

The first real provider is planned around **Home Assistant**.

That gives Lightshift a normalized entry point to multiple lighting ecosystems while the scene engine is still being proven.

Later provider work may include:

```text
Home Assistant
Direct Philips Hue
WLED
other locally controllable lighting systems
```

Provider-specific behavior belongs behind the provider interface.

The rest of Lightshift should care about things like:

```text
SET_POWER
SET_BRIGHTNESS
SET_COLOR_TEMPERATURE
SET_COLOR
APPLY_SCENE
```

rather than individual vendor request formats.

---

# Project layout

The intended package structure is:

```text
lightshift/
├── pyproject.toml
├── README.md
├── config/
│   ├── devices.json
│   ├── scenes.toml
│   └── inputs.toml
│
├── src/
│   └── lightshift/
│       ├── __init__.py
│       ├── __main__.py
│       ├── cli.py
│       ├── config.py
│       ├── models.py
│       ├── anomalies.py
│       ├── registry.py
│       ├── scenes.py
│       ├── planner.py
│       ├── executor.py
│       │
│       ├── providers/
│       │   ├── base.py
│       │   ├── fake.py
│       │   └── home_assistant.py
│       │
│       └── inputs/
│           ├── cli.py
│           ├── socket.py
│           └── evdev.py
│
└── tests/
    ├── fixtures/
    ├── test_models.py
    ├── test_scenes.py
    ├── test_planner.py
    └── test_executor.py
```

Not all of these modules exist yet.

The structure represents where the current design is headed rather than a claim of completed functionality.

---

# Development

Clone the repository:

```bash
git clone https://github.com/jess-being-kind/lightshift.git
cd lightshift
```

Create the environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install the project for development:

```bash
python -m pip install --upgrade pip
python -m pip install -e '.[dev]'
```

Run tests:

```bash
python -m pytest -vv
```

Run the module:

```bash
python -m lightshift --help
```

The repository also uses separate **DayShift** and **NightShift** VS Code workspaces for development.

---

# Credentials

Provider credentials are local configuration and should never become repository state.

Expected local-only values may eventually include:

```text
HOME_ASSISTANT_URL
HOME_ASSISTANT_TOKEN
LIGHTSHIFT_CONFIG_DIR
```

At minimum:

```gitignore
.venv/
.env
__pycache__/
*.py[cod]
.pytest_cache/
.mypy_cache/
.ruff_cache/
output/
*.log
```

Lightshift should not print provider secrets into:

* console output;
* exceptions;
* execution reports;
* DEBUG logs.

Evidence is useful.

Credentials are not evidence.

---

# Engineering principles

### Observe before mutation

Know as much about current state as practical before changing it.

### Reject impossible state early

If two options contradict each other, prevent that combination at the boundary instead of deciding later which one wins.

### Preserve evidence

Requested state, transmitted command, acknowledgement, and observed state are distinct facts.

### Degrade honestly

Partial success should be represented as partial success.

### Keep failure bounded

One failed light should not automatically become one failed room.

### Make behavior deterministic

The same inputs against the same known state should produce the same execution plan.

### Keep policy visible

Retries, approximations, unsupported capabilities, and failure thresholds should be deliberate behavior—not accidental side effects.

### Test without hardware

The core engine should be provable against fake devices before real hardware gets involved.

---

# Roadmap

## v0.1 — prove the path

* [x] repository/bootstrap;
* [x] CLI foundation;
* [x] runtime configuration model;
* [x] console + file logging architecture;
* [x] initial normalized model design;
* [ ] fake light fixtures;
* [ ] fake provider;
* [ ] device registry;
* [ ] TOML scene parser;
* [ ] capability-aware scene planner;
* [ ] deterministic dry-run;
* [ ] scene executor;
* [ ] per-command results;
* [ ] requested-versus-observed verification;
* [ ] Home Assistant provider;
* [ ] first real light controlled through `lumenctl`.

## After the core path works

* [ ] Linux desktop shortcuts;
* [ ] Unix-domain control socket;
* [ ] `lumenctld` user daemon;
* [ ] systemd user service;
* [ ] dedicated `evdev` input device;
* [ ] rotary brightness control;
* [ ] direct Hue bridge provider;
* [ ] WLED provider;
* [ ] richer area/tag selectors;
* [ ] native effects and dynamic scenes;
* [ ] transition choreography;
* [ ] state history;
* [ ] rollback / restore;
* [ ] optional graphical scene editor.

---

# What Lightshift is not

At least for now:

Lightshift is not trying to replace Home Assistant.

It is not trying to become a giant home-automation platform.

It is not trying to hide every failure behind one generic `success` flag.

It is a smaller tool with a narrower job:

> **Take lighting intent from Linux, understand the devices available to satisfy it, execute the transition, and tell the operator what actually happened.**

That boundary is enough.

---

# Name

**Lightshift**:

```text
light + state transition
```

The project is:

```text
lightshift
```

The operator-facing executable is:

```text
lumenctl
```

And the basic workflow stays:

```text
discover
define
plan
apply
verify
```

---

## License

License selection is still TBD while the project is in early development.
