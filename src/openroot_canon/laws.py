"""Locked algorithms. Names match CANON.json ids. Do not alias."""
from __future__ import annotations
import math

K_BOLTZMANN = 1.380649e-23


def coord(N: float, T: float, R: float) -> float:
    """N03. At R=1.0 and T>=1 this is identically 0.0."""
    if R >= 1.0 and T >= 1:
        return 0.0
    return N * 0.001 * (1 + 0.1 * T) * ((1 - R) ** T)


def synergy(N: float, R: float, B: float = 6.0) -> float:
    """N05."""
    if N <= 0 or B <= 1:
        raise ValueError("N>0 and B>1")
    return 1.0 + (R * 0.5 * (math.log(N) / math.log(B)))


def eta(useful_joules: float, human_joules: float) -> float | None:
    """N01. None if human_joules is 0. Never invent the denominator."""
    if human_joules <= 0:
        return None
    return useful_joules / human_joules


def gamma(Y: float, L: float, P: float, F: float, Jh: float, Je: float, C: float) -> float | None:
    """N02."""
    den = Jh + Je + C
    if den <= 0:
        return None
    return (Y * L * P * F) / den


def landauer(bits: float, T_kelvin: float = 300.0) -> float:
    """N06 floor in joules."""
    return bits * T_kelvin * K_BOLTZMANN * math.log(2)
