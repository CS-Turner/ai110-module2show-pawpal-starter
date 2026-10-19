"""
tests/test_pawpal.py
Quick unit tests for core PawPal+ behaviors.
Run with: python -m pytest
"""

from pawpal_system import Pet, Task, Priority


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
