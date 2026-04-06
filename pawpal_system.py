"""
pawpal_system.py
PawPal+ backend: Owner, Pet, Task, and Scheduler classes.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from datetime import date, timedelta
from typing import Literal


# ---------------------------------------------------------------------------
# Task
# ---------------------------------------------------------------------------

@dataclass
class Task:
    """Represents a single pet-care activity."""

    title: str
    time: str
    duration_minutes: int
    priority: Literal["low", "medium", "high"] = "medium"
    frequency: Literal["once", "daily", "weekly"] = "once"
    completed: bool = False
    due_date: date = field(default_factory=date.today)

    def mark_complete(self) -> "Task | None":
        """Mark this task complete and return a new Task for the next occurrence (or None)."""
        self.completed = True
        if self.frequency == "daily":
            return Task(
                title=self.title,
                time=self.time,
                duration_minutes=self.duration_minutes,
                priority=self.priority,
                frequency=self.frequency,
                due_date=self.due_date + timedelta(days=1),
            )
        if self.frequency == "weekly":
            return Task(
                title=self.title,
                time=self.time,
                duration_minutes=self.duration_minutes,
                priority=self.priority,
                frequency=self.frequency,
                due_date=self.due_date + timedelta(weeks=1),
            )
        return None

    @property
    def priority_weight(self) -> int:
        """Numeric weight for sorting (lower = higher priority)."""
        return {"high": 0, "medium": 1, "low": 2}.get(self.priority, 1)

    def __str__(self) -> str:
        status = "✅" if self.completed else "⏳"
        return (
            f"{status} [{self.time}] {self.title} "
            f"({self.duration_minutes} min, {self.priority} priority)"
        )


# ---------------------------------------------------------------------------
# Pet
# ---------------------------------------------------------------------------

@dataclass
class Pet:
    """Stores pet info and its associated task list."""

    name: str
    species: str
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Add a task to this pet's task list."""
        self.tasks.append(task)

    def remove_task(self, title: str) -> bool:
        """Remove the first task whose title matches; return True if removed."""
        for i, t in enumerate(self.tasks):
            if t.title.lower() == title.lower():
                self.tasks.pop(i)
                return True
        return False

    def task_count(self) -> int:
        """Return the number of tasks assigned to this pet."""
        return len(self.tasks)

    def __str__(self) -> str:
        return f"{self.name} ({self.species}) — {self.task_count()} task(s)"


# ---------------------------------------------------------------------------
# Owner
# ---------------------------------------------------------------------------

class Owner:
    """Manages one or more pets and provides aggregate access to their tasks."""

    def __init__(self, name: str) -> None:
        """Initialize owner with a name and empty pet list."""
        self.name = name
        self.pets: list[Pet] = []

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to the owner's roster."""
        self.pets.append(pet)

    def remove_pet(self, name: str) -> bool:
        """Remove a pet by name; return True if removed."""
        for i, p in enumerate(self.pets):
            if p.name.lower() == name.lower():
                self.pets.pop(i)
                return True
        return False

    def get_all_tasks(self) -> list[tuple[str, Task]]:
        """Return all tasks as (pet_name, Task) tuples across every pet."""
        result = []
        for pet in self.pets:
            for task in pet.tasks:
                result.append((pet.name, task))
        return result

    def __str__(self) -> str:
        return f"Owner: {self.name} | Pets: {[p.name for p in self.pets]}"


# ---------------------------------------------------------------------------
# Scheduler
# ---------------------------------------------------------------------------

class Scheduler:
    """The brain: retrieves, sorts, filters, and validates tasks from an Owner."""

    def __init__(self, owner: Owner) -> None:
        """Initialize scheduler with an Owner instance."""
        self.owner = owner

    def get_all_tasks(self) -> list[tuple[str, Task]]:
        """Return every (pet_name, Task) pair from the owner."""
        return self.owner.get_all_tasks()

    def sort_by_time(self) -> list[tuple[str, Task]]:
        """Return tasks sorted by time (HH:MM), then by priority weight."""
        return sorted(
            self.get_all_tasks(),
            key=lambda pt: (pt[1].time, pt[1].priority_weight),
        )

    def filter_by_pet(self, pet_name: str) -> list[tuple[str, Task]]:
        """Return only tasks belonging to the named pet."""
        return [(n, t) for n, t in self.get_all_tasks() if n.lower() == pet_name.lower()]

    def filter_by_status(self, completed: bool) -> list[tuple[str, Task]]:
        """Return tasks matching the given completion status."""
        return [(n, t) for n, t in self.get_all_tasks() if t.completed == completed]

    def filter_by_priority(self, priority: str) -> list[tuple[str, Task]]:
        """Return tasks matching the given priority level."""
        return [(n, t) for n, t in self.get_all_tasks() if t.priority == priority]

    def detect_conflicts(self) -> list[str]:
        """Return warning strings for any two tasks whose start times overlap."""
        warnings: list[str] = []
        tasks = self.sort_by_time()

        def to_minutes(t: str) -> int:
            h, m = map(int, t.split(":"))
            return h * 60 + m

        for i in range(len(tasks)):
            for j in range(i + 1, len(tasks)):
                pet_a, task_a = tasks[i]
                pet_b, task_b = tasks[j]
                start_a = to_minutes(task_a.time)
                end_a   = start_a + task_a.duration_minutes
                start_b = to_minutes(task_b.time)
                if start_b < end_a:
                    warnings.append(
                        f"⚠️ CONFLICT: '{task_a.title}' ({pet_a}, {task_a.time}, "
                        f"{task_a.duration_minutes} min) overlaps with "
                        f"'{task_b.title}' ({pet_b}, {task_b.time})"
                    )
        return warnings

    def mark_task_complete(self, pet_name: str, task_title: str) -> str:
        """Mark a task complete; if recurring, add the next occurrence to that pet."""
        for pet in self.owner.pets:
            if pet.name.lower() != pet_name.lower():
                continue
            for task in pet.tasks:
                if task.title.lower() == task_title.lower() and not task.completed:
                    next_task = task.mark_complete()
                    if next_task:
                        pet.add_task(next_task)
                        return (
                            f"✅ '{task.title}' marked complete. "
                            f"Next occurrence scheduled for {next_task.due_date}."
                        )
                    return f"✅ '{task.title}' marked complete (one-time task)."
        return f"⚠️ Task '{task_title}' not found or already complete for {pet_name}."

    def todays_schedule(self, target_date: date | None = None) -> list[tuple[str, Task]]:
        """Return sorted, incomplete tasks due on target_date (default: today)."""
        target = target_date or date.today()
        filtered = [
            (n, t)
            for n, t in self.get_all_tasks()
            if not t.completed and t.due_date == target
        ]
        return sorted(filtered, key=lambda pt: (pt[1].time, pt[1].priority_weight))

    def summary(self) -> str:
        """Return a formatted daily schedule string."""
        schedule  = self.sort_by_time()
        conflicts = self.detect_conflicts()
        lines = [f"\n📅 Schedule for {self.owner.name}'s pets\n" + "=" * 40]
        for pet_name, task in schedule:
            lines.append(f"  {task}  [{pet_name}]")
        if not schedule:
            lines.append("  No tasks scheduled.")
        if conflicts:
            lines.append("\n" + "\n".join(conflicts))
        lines.append("=" * 40)
        return "\n".join(lines)