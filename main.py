"""
main.py
Temporary CLI testing ground for PawPal+ logic (pawpal_system.py).
Run with: python main.py
"""

from pawpal_system import Owner, Pet, Task, Priority, Recurrence, Scheduler, ScheduledTask

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

print("\n-- Sorting demo --")
out_of_order = list(reversed(scheduler.sort_by_time()))
print("Out-of-order:")
for st in out_of_order:
    print(f"  {st.start_time} — {st.pet.name}: {st.task.name}")

print("Sorted by time:")
for st in scheduler.sort_by_time(out_of_order):
    print(f"  {st.start_time} — {st.pet.name}: {st.task.name}")

print("\n-- Filtering demo --")
print("Biscuit's tasks:")
for pet, task in owner.filter_tasks(pet_name="Biscuit"):
    print(f"  {task.name}")

print("Incomplete tasks:")
for pet, task in owner.filter_tasks(completed=False):
    print(f"  {pet.name}: {task.name}")

print("\n-- Recurring task demo --")
checkup = Task(
    name="Give daily medication", category="meds", duration=5,
    priority=Priority.HIGH, recurrence=Recurrence.DAILY,
)
biscuit.add_task(checkup)
print(f"Before: Biscuit has {len(biscuit.tasks)} tasks")
biscuit.complete_task(checkup)
print(f"After completing a daily task: Biscuit has {len(biscuit.tasks)} tasks")
print(f"Next occurrence due: {biscuit.tasks[-1].due_date}")

print("\n-- Conflict detection demo --")
conflicting_plan = scheduler.sort_by_time() + [
    ScheduledTask(
        pet=whiskers,
        task=Task(name="Vet checkup", category="meds", duration=15, priority=Priority.HIGH),
        start_time="08:00",
    )
]
conflicts = scheduler.detect_conflicts(conflicting_plan)
if conflicts:
    for warning in conflicts:
        print(f"  WARNING: {warning}")
else:
    print("  No conflicts detected.")
