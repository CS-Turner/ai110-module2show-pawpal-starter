"""
pawpal_system.py
Core logic layer for PawPal+.
"""

from dataclasses import dataclass, field
from datetime import date
from enum import Enum
from typing import List, Optional, Tuple


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
    """A single pet care activity: what, how long, how often, and whether it's done."""
    name: str
    category: str
    duration: int                        # minutes
    priority: Priority
    recurrence: Recurrence = Recurrence.NONE
    weekday: Optional[int] = None        # 0=Mon..6=Sun; required if recurrence == WEEKLY
    completed: bool = False
    last_completed: Optional[date] = None

    def mark_complete(self, today: Optional[date] = None) -> None:
        """Mark this task done and record when."""
        self.completed = True
        self.last_completed = today or date.today()

    def is_due_today(self, today: Optional[date] = None) -> bool:
        """Return whether this task should appear in today's plan."""
        today = today or date.today()
        if self.recurrence == Recurrence.NONE:
            return not self.completed
        if self.recurrence == Recurrence.DAILY:
            return self.last_completed != today
        if self.recurrence == Recurrence.WEEKLY:
            return self.weekday == today.weekday() and self.last_completed != today
        return False


@dataclass
class Pet:
    """A pet and the care tasks assigned to it."""
    name: str
    species: str
    owner: Optional["Owner"] = None
    tasks: List[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Add a care task to this pet."""
        self.tasks.append(task)

    def remove_task(self, task: Task) -> None:
        """Remove a care task from this pet, if present."""
        if task in self.tasks:
            self.tasks.remove(task)


@dataclass
class Owner:
    """A pet owner: their household of pets, time budget, and preferences."""
    name: str
    available_time: int                  # minutes available per day
    day_start: str = "08:00"             # "HH:MM"
    preferences: dict = field(default_factory=dict)
    pets: List[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to this household, keeping the owner<->pet link in sync."""
        if pet.owner is not None and pet.owner is not self and pet in pet.owner.pets:
            pet.owner.pets.remove(pet)
        pet.owner = self
        if pet not in self.pets:
            self.pets.append(pet)

    def get_all_tasks(self) -> List[Tuple[Pet, Task]]:
        """Return every (pet, task) pair across all of this owner's pets."""
        return [(pet, task) for pet in self.pets for task in pet.tasks]

    def get_daily_plan(self, today: Optional[date] = None) -> List["ScheduledTask"]:
        """Return today's scheduled plan across all pets, via Scheduler."""
        return Scheduler(self).generate_plan(today)


@dataclass
class ScheduledTask:
    """One entry in a generated plan: which pet, which task, and when it starts."""
    pet: Pet
    task: Task
    start_time: str   # "HH:MM"


class Scheduler:
    """Builds and explains a daily plan from an Owner's pets' tasks."""

    def __init__(self, owner: Owner):
        self.owner = owner

    def generate_plan(self, today: Optional[date] = None) -> List[ScheduledTask]:
        """Pick due tasks, sort by priority, fit them into available time, assign start times."""
        today = today or date.today()
        due = [(pet, task) for pet, task in self.owner.get_all_tasks() if task.is_due_today(today)]
        due.sort(key=lambda pair: pair[1].priority.value, reverse=True)

        plan: List[ScheduledTask] = []
        minutes_used = 0
        clock = self._to_minutes(self.owner.day_start)

        for pet, task in due:
            if minutes_used + task.duration > self.owner.available_time:
                continue
            plan.append(ScheduledTask(pet=pet, task=task, start_time=self._to_clock(clock)))
            minutes_used += task.duration
            clock += task.duration

        self._last_plan = plan
        return plan

    def explain_plan(self) -> str:
        """Return a human-readable explanation of the most recently generated plan."""
        if not getattr(self, "_last_plan", None):
            return "No tasks scheduled for today."
        lines = ["Today's Schedule:"]
        for st in self._last_plan:
            lines.append(
                f"  {st.start_time} — {st.pet.name}: {st.task.name} "
                f"({st.task.duration} min) [priority: {st.task.priority.name.lower()}]"
            )
        return "\n".join(lines)

    @staticmethod
    def _to_minutes(hhmm: str) -> int:
        h, m = map(int, hhmm.split(":"))
        return h * 60 + m

    @staticmethod
    def _to_clock(minutes: int) -> str:
        return f"{minutes // 60:02d}:{minutes % 60:02d}"
