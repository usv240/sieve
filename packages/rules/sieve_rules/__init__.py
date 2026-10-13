"""Deterministic safety rules engine. The language model never decides whether a gate fires."""

from .engine import Rule, RuleHit, RulesEngine, load_rules

__all__ = ["Rule", "RuleHit", "RulesEngine", "load_rules"]
