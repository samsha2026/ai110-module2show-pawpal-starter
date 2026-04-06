"""
tests/test_pawpal.py
Run with: python3 -m pytest
"""

import pytest
from datetime import date, timedelta
from pawpal_system import Owner, Pet, Task, Scheduler


# ── Fixtures ─────────────────────────────────────────────────────────────────

@pytest.fixture
def today():
    return date.today()

@pytest.fixture
def sample_owner(today):
    owner = Owner("Jordan")
    dog = Pet("Mochi", "dog")
    dog.add_task(Task("Morning walk", "07:30", 25, "high",   "daily",  due_date=today))
    dog.add_task(Task("Breakfast",    "07:00", 5,  "high",   "daily",  due_date=today))
    dog.add_task(Task("Evening walk", "18:00", 30, "high",   "daily",  due_date=today))
    dog.add_task(Task("Grooming",     "10:00", 20, "medium", "weekly", due_date=today))
    owner.add_pet(dog)
    cat = Pet("Luna", "cat")
    cat.add_task(Task("Wet food", "07:15", 5,  "high",   "daily", due_date=today))
    cat.add_task(Task("Playtime", "19:00", 15, "medium", "daily", due_date=today))
    owner.add_pet(cat)
    return owner


# ── Task tests ────────────────────────────────────────────────────────────────

class TestTask:
    def test_mark_complete_changes_status(self, today):
        t = Task("Meds", "09:00", 5, due_date=today)
        assert not t.completed
        t.mark_complete()
        assert t.completed

    def test_mark_complete_once_returns_none(self, today):
        t = Task("Vet visit", "14:00", 60, frequency="once", due_date=today)
        assert t.mark_complete() is None

    def test_daily_recurrence_creates_next_day_task(self, today):
        t = Task("Morning walk", "07:30", 25, frequency="daily", due_date=today)
        next_t = t.mark_complete()
        assert next_t is not None
        assert next_t.due_date == today + timedelta(days=1)
        assert next_t.completed is False

    def test_weekly_recurrence_creates_next_week_task(self, today):
        t = Task("Grooming", "10:00", 20, frequency="weekly", due_date=today)
        next_t = t.mark_complete()
        assert next_t is not None
        assert next_t.due_date == today + timedelta(weeks=1)


# ── Pet tests ─────────────────────────────────────────────────────────────────

class TestPet:
    def test_add_task_increases_count(self, today):
        pet = Pet("Mochi", "dog")
        assert pet.task_count() == 0
        pet.add_task(Task("Walk", "08:00", 20, due_date=today))
        assert pet.task_count() == 1

    def test_remove_task_decreases_count(self, today):
        pet = Pet("Mochi", "dog")
        pet.add_task(Task("Walk", "08:00", 20, due_date=today))
        assert pet.remove_task("Walk") is True
        assert pet.task_count() == 0

    def test_remove_nonexistent_task_returns_false(self):
        pet = Pet("Mochi", "dog")
        assert pet.remove_task("Nonexistent") is False


# ── Scheduler tests ───────────────────────────────────────────────────────────

class TestScheduler:
    def test_sort_by_time_is_chronological(self, sample_owner):
        sched = Scheduler(sample_owner)
        times = [t.time for _, t in sched.sort_by_time()]
        assert times == sorted(times)

    def test_filter_by_pet_returns_only_that_pet(self, sample_owner):
        sched = Scheduler(sample_owner)
        results = sched.filter_by_pet("Luna")
        assert all(name == "Luna" for name, _ in results)
        assert len(results) == 2

    def test_filter_by_status_incomplete(self, sample_owner):
        sched = Scheduler(sample_owner)
        assert all(not t.completed for _, t in sched.filter_by_status(False))

    def test_filter_by_priority_high(self, sample_owner):
        sched = Scheduler(sample_owner)
        assert all(t.priority == "high" for _, t in sched.filter_by_priority("high"))

    def test_conflict_detection_flags_overlap(self, today):
        owner = Owner("Test")
        pet = Pet("Rex", "dog")
        pet.add_task(Task("Task A", "07:00", 10, due_date=today))
        pet.add_task(Task("Task B", "07:05", 5,  due_date=today))
        owner.add_pet(pet)
        warnings = Scheduler(owner).detect_conflicts()
        assert len(warnings) >= 1

    def test_no_conflict_when_tasks_sequential(self, today):
        owner = Owner("Test")
        pet = Pet("Rex", "dog")
        pet.add_task(Task("Task A", "07:00", 10, due_date=today))
        pet.add_task(Task("Task B", "07:10", 5,  due_date=today))
        owner.add_pet(pet)
        assert Scheduler(owner).detect_conflicts() == []

    def test_mark_task_complete_adds_recurrence(self, sample_owner, today):
        sched = Scheduler(sample_owner)
        before = sample_owner.pets[0].task_count()
        sched.mark_task_complete("Mochi", "Morning walk")
        assert sample_owner.pets[0].task_count() == before + 1

    def test_todays_schedule_excludes_completed(self, today):
        owner = Owner("Test")
        pet = Pet("Rex", "dog")
        t = Task("Walk", "08:00", 20, due_date=today)
        t.completed = True
        pet.add_task(t)
        owner.add_pet(pet)
        assert Scheduler(owner).todays_schedule() == []