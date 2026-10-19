"""
tests/test_pawpal.py
Quick unit tests for core PawPal+ behaviors.
Run with: python -m pytest
"""

from datetime import date, timedelta

from pawpal_system import Pet, Task, Priority, Recurrence, Owner, Scheduler, ScheduledTask


def test_mark_complete_changes_status():
    task = Task(name="Walk", category="walk", duration=30, priority=Priority.HIGH)
    assert task.completed is False
    task.mark_complete()
    assert task.completed is True
    assert task.last_completed is not None


def test_add_task_increases_pet_task_count():
    pet = Pet(name="Biscuit", species="Golden Retriever")
    assert len(pet.tasks) == 0
    pet.add_task(Task(name="Feeding", category="feeding", duration=10, priority=Priority.HIGH))
    assert len(pet.tasks) == 1


def test_sort_by_time_returns_chronological_order():
    pet = Pet(name="Biscuit", species="dog")
    task = Task(name="A", category="walk", duration=10, priority=Priority.HIGH)
    scheduler = Scheduler(Owner(name="X", available_time=60))
    tasks = [
        ScheduledTask(pet=pet, task=task, start_time="09:00"),
        ScheduledTask(pet=pet, task=task, start_time="08:00"),
        ScheduledTask(pet=pet, task=task, start_time="08:30"),
    ]
    sorted_tasks = scheduler.sort_by_time(tasks)
    assert [st.start_time for st in sorted_tasks] == ["08:00", "08:30", "09:00"]


def test_complete_daily_task_creates_next_occurrence():
    pet = Pet(name="Biscuit", species="dog")
    task = Task(name="Meds", category="meds", duration=5, priority=Priority.HIGH, recurrence=Recurrence.DAILY)
    pet.add_task(task)
    today = date(2026, 10, 19)
    pet.complete_task(task, today=today)
    assert len(pet.tasks) == 2
    new_task = pet.tasks[-1]
    assert new_task.completed is False
    assert new_task.due_date == today + timedelta(days=1)


def test_complete_one_off_task_does_not_create_new_task():
    pet = Pet(name="Biscuit", species="dog")
    task = Task(name="Vet visit", category="meds", duration=30, priority=Priority.HIGH)
    pet.add_task(task)
    pet.complete_task(task)
    assert len(pet.tasks) == 1
    assert pet.tasks[0].completed is True


def test_detect_conflicts_flags_duplicate_times():
    pet_a = Pet(name="Biscuit", species="dog")
    pet_b = Pet(name="Whiskers", species="cat")
    scheduler = Scheduler(Owner(name="X", available_time=60))
    tasks = [
        ScheduledTask(pet=pet_a, task=Task(name="Walk", category="walk", duration=10, priority=Priority.HIGH), start_time="08:00"),
        ScheduledTask(pet=pet_b, task=Task(name="Feed", category="feeding", duration=10, priority=Priority.HIGH), start_time="08:00"),
    ]
    conflicts = scheduler.detect_conflicts(tasks)
    assert len(conflicts) == 1
    assert "08:00" in conflicts[0]


def test_detect_conflicts_no_warning_when_times_differ():
    pet = Pet(name="Biscuit", species="dog")
    scheduler = Scheduler(Owner(name="X", available_time=60))
    tasks = [
        ScheduledTask(pet=pet, task=Task(name="Walk", category="walk", duration=10, priority=Priority.HIGH), start_time="08:00"),
        ScheduledTask(pet=pet, task=Task(name="Feed", category="feeding", duration=10, priority=Priority.HIGH), start_time="08:30"),
    ]
    assert scheduler.detect_conflicts(tasks) == []


def test_generate_plan_handles_pet_with_no_tasks():
    owner = Owner(name="X", available_time=60)
    owner.add_pet(Pet(name="Biscuit", species="dog"))
    scheduler = Scheduler(owner)
    assert scheduler.generate_plan() == []


def test_generate_plan_skips_task_that_does_not_fit():
    owner = Owner(name="X", available_time=15, day_start="08:00")
    pet = Pet(name="Biscuit", species="dog")
    owner.add_pet(pet)
    pet.add_task(Task(name="Big walk", category="walk", duration=30, priority=Priority.HIGH))
    pet.add_task(Task(name="Quick feed", category="feeding", duration=10, priority=Priority.MEDIUM))
    scheduler = Scheduler(owner)
    names = [st.task.name for st in scheduler.generate_plan()]
    assert "Big walk" not in names
    assert "Quick feed" in names
