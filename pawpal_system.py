"""
pawpal_system.py
Logic layer for PawPal+ — class skeletons translated from diagrams/uml.mmd.
No scheduling logic implemented yet (Phase 1: structure only).
"""

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class Task:
    name: str
    category: str          # e.g. "walk", "feeding", "meds", "grooming", "enrichment"
    duration: int           # minutes
    priority: str            # e.g. "high", "medium", "low"
    recurrence: str = "none"  # "daily", "weekly", "none"

    def is_due_today(self) -> bool:
        """Return whether this task should be scheduled today."""
        raise NotImplementedError


@dataclass
class Pet:
    name: str
    species: str
    owner: Optional["Owner"] = None
    tasks: List[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Add a care task to this pet."""
        raise NotImplementedError

    def remove_task(self, task: Task) -> None:
        """Remove a care task from this pet."""
        raise NotImplementedError


@dataclass
class Owner:
    name: str
    available_time: int  # minutes available per day
    pets: List[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to this owner's household."""
        raise NotImplementedError

    def get_daily_plan(self) -> "list":
        """Return today's scheduled plan across all pets."""
        raise NotImplementedError


class Scheduler:
    def __init__(self, tasks: List[Task], time_available: int):
        self.tasks = tasks
        self.time_available = time_available

    def generate_plan(self) -> list:
        """Sort/filter tasks by priority and fit them into time_available."""
        raise NotImplementedError

    def explain_plan(self) -> str:
        """Return a human-readable explanation of the generated plan."""
        raise NotImplementedError