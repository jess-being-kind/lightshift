#!/usr/bin/env python3
# src/lightshift/config.py

from dataclasses import dataclass

HUE_BRIDGE = "10.0.0.205"

@dataclass(frozen=True)
class SystemConfig:
    bridge_ip: str = HUE_BRIDGE