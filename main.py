"""
main.py
Temporary CLI testing ground for PawPal+ logic (pawpal_system.py).
Run with: python main.py
"""

from pawpal_system import Owner, Pet, Task, Priority, Scheduler

owner = Owner(name="Charity", available_time=90, day_start="08:00")

biscuit = Pet(name="Biscuit", species="Golden Retriever")
whiskers = Pet(name="Whiskers", species="Cat")
owner.add_pet(biscuit)
owner.add_pet(whiskers)

biscuit.add_task(Task(name="Morning walk", category="walk", duration=30, priority=Priority.HIGH))
biscuit.add_task(Task(name="Feeding", category="feeding", duration=10, priority=Priority.HIGH))
whiskers.add_task(Task(name="Litter box clean", category="grooming", duration=10, priority=Priority.MEDIUM))
whiskers.add_task(Task(name="Playtime", category="enrichment", duration=20, priority=Priority.LOW))

scheduler = Scheduler(owner)
scheduler.generate_plan()
print(scheduler.explain_plan())
