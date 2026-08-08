#!/usr/bin/env python3
# src/lightshift/models.py

# Imports and metadata
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto

# LightDevice contains device-intrinsic information
@dataclass(slots=True)
class LightDevice:
    name: str
    device_id: str
    device_type: str
    device_rev: str
    handle: str
    manufacturer: str
    capabilities: LightCapabilities
    state: LightState

# LightCapabilities carries lightshift-supported light modes
@dataclass(frozen=True, slots=True)
class LightCapabilities:
    temperature: bool
    color: bool
    supported_color_modes: tuple[str,...]
    min_mirek: int | None
    max_mirek: int | None
    effects: tuple[str,...]
    entertainment: bool

# LightState maps current light behavior
@dataclass(slots=True)
class LightState:
    on: bool
    brightness: int
    temperature_mirek: int | None
    color_xy: tuple[float, float] | None
    pairing: bool

# InputIntent carries command/ack + temporal information
@dataclass(frozen=True, slots=True)
class InputIntent:
    intent: str
    transmitted: bool
    ack_received: bool
    ack_time: float

# LightCommand is built from CommandAction
@dataclass(slots=True)
class LightCommand:
    command: CommandAction

class CommandAction(Enum):
    START = auto()
    STOP = auto()
    PAUSE = auto()
    RESUME = auto()
    SKIP = auto()
    BACK = auto()

# CommandResult contains command-response information
@dataclass(slots=True)
class CommandResult:
    transmitted: bool
    ack_received: bool
    ack_time: float | None
    message: str | None
    status: Status

# Generic Status enum
class Status(Enum):
    OK = auto()
    SKIPPED = auto()
    DEGRADED = auto()
    INVALID = auto()
    RECOVERABLE = auto()
    FATAL = auto()

# SceneResult tracks scene and success
@dataclass(frozen=True, slots=True)
class SceneResult:
    scene: str | None
    success: bool

# ColorMode encodes light color modes
class ColorMode(Enum):
    XY = auto()
    COLOR_TEMPERATURE = auto()
    BRIGHTNESS = auto()


test_light_capabilities = LightCapabilities(
    temperature=True,
    color=True,
    supported_color_modes=("XY",),
    min_mirek=115,
    max_mirek=255,
    effects=("sparkle", "fireplace",),
    entertainment=False
)

test_light_state = LightState(
    on=True,
    brightness=255,
    temperature_mirek=114,
    color_xy=(110.3, 224.5),
    pairing=True
)

test_light = LightDevice(
    name="philips-hue", device_id="001", device_type="hue-go", device_rev="0.1.0",
    handle="test_device", manufacturer="philips", capabilities=test_light_capabilities,
    state = test_light_state,
)

print(test_light)
