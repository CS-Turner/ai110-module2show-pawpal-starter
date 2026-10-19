"""
pawpal_system.py
Logic layer for PawPal+ — class skeletons translated from diagrams/uml.mmd.
No scheduling logic implemented yet (Phase 1: structure only).
"""

from dataclasses import dataclass, field
from datetime import date
from enum import Enum
from typing import List, Optional


class Priority(Enum):
    HIGH = 3
    MEDIUM = 2
    LOW = 1


class Recurrence(Enum):
    NONE = "none"
    DAILY = "daily"
    WEEKLY = "weekly"


@dataclass
class Task:
    name: str
    category: str          # e.g. "walk", "feeding", "meds", "grooming", "enrichment"
    duration: int           # minutes
    priority: Priority
    recurrence: Recurrence = Recurrence.NONE
    weekday: Optional[int] = None       # 0=Mon..6=Sun; set when recurrence == WEEKLY
    last_completed: Optional[date] = None

    def is_due_today(self, today: date) -> bool:
        """Return whether this task should be scheduled on `today`,
        using recurrence, weekday, and last_completed."""
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
    available_time: int                  # minutes available per day
    day_start: str = "08:00"             # clock time the plan starts, "HH:MM"
    preferences: dict = field(default_factory=dict)   # e.g. {"preferred_walk_time": "morning"}
    pets: List[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to this owner's household and set pet.owner so the
        two-way link can't drift out of sync. If `pet` already belongs to
        another owner, reassign it (remove from the prior owner's list)."""
        raise NotImplementedError

    def get_daily_plan(self) -> "List[ScheduledTask]":
        """Return today's scheduled plan across all pets."""
        raise NotImplementedError


@dataclass
class ScheduledTask:
    """One entry in a generated plan: which pet, which task, and when."""
    pet: Pet
    task: Task
    start_time: str   # "HH:MM"


class Scheduler:
    def __init__(self, tasks: List[Task], time_available: int, preferences: Optional[dict] = None):
        self.tasks = tasks
        self.time_available = time_available
        self.preferences = preferences or {}
        self._last_plan: List[ScheduledTask] = []

    def generate_plan(self) -> List[ScheduledTask]:
        """Sort/filter tasks by priority and preferences, fit them into
        time_available, assign clock times, and store the result in
        self._last_plan so explain_plan() can describe it."""
        raise NotImplementedError

    def explain_plan(self) -> str:
        """Return a human-readable explanation of self._last_plan
        (the most recently generated plan)."""
        raise NotImplementedError
