import streamlit as st

from pawpal_system import Owner, Pet, Task, Priority, Recurrence, Scheduler

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")
st.title("🐾 PawPal+")

# --- Step 2: persist the Owner in session_state so it survives reruns ---
if "owner" not in st.session_state:
    st.session_state.owner = Owner(name="Jordan", available_time=90, day_start="08:00")
owner = st.session_state.owner

with st.expander("Owner settings", expanded=True):
    owner.name = st.text_input("Owner name", value=owner.name)
    owner.available_time = st.number_input(
        "Available time today (minutes)", min_value=10, max_value=600, value=owner.available_time
    )

st.divider()

# --- Step 3: Add a Pet -> Owner.add_pet() ---
st.subheader("Add a Pet")
with st.form("add_pet_form", clear_on_submit=True):
    pet_name = st.text_input("Pet name", value="")
    species = st.selectbox("Species", ["dog", "cat", "other"])
    if st.form_submit_button("Add pet") and pet_name:
        owner.add_pet(Pet(name=pet_name, species=species))
        st.success(f"Added {pet_name}")

if owner.pets:
    st.write("Pets:", ", ".join(p.name for p in owner.pets))
else:
    st.info("No pets yet. Add one above.")

st.divider()

# --- Step 3: Add a Task -> Pet.add_task() ---
st.subheader("Add a Task")
if owner.pets:
    with st.form("add_task_form", clear_on_submit=True):
        pet_choice = st.selectbox("Pet", [p.name for p in owner.pets])
        task_title = st.text_input("Task title", value="Morning walk")
        category = st.selectbox("Category", ["walk", "feeding", "meds", "grooming", "enrichment"])
        duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
        priority_label = st.selectbox("Priority", ["low", "medium", "high"], index=2)
        recurrence_label = st.selectbox("Recurrence", ["none", "daily", "weekly"])
        weekday_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        weekday_label = st.selectbox("Day of week (used only if Recurrence = weekly)", weekday_names)
        if st.form_submit_button("Add task"):
            pet = next(p for p in owner.pets if p.name == pet_choice)
            weekday_value = weekday_names.index(weekday_label) if recurrence_label == "weekly" else None
            pet.add_task(
                Task(
                    name=task_title,
                    category=category,
                    duration=int(duration),
                    priority=Priority[priority_label.upper()],
                    recurrence=Recurrence[recurrence_label.upper()],
                    weekday=weekday_value,
                )
            )
            st.success(f"Added '{task_title}' to {pet_choice}")
else:
    st.caption("Add a pet first.")

st.subheader("All Tasks")
filter_pet = st.selectbox("Filter by pet", ["All"] + [p.name for p in owner.pets]) if owner.pets else "All"
filter_status = st.selectbox("Filter by status", ["All", "Completed", "Incomplete"])

pet_filter = None if filter_pet == "All" else filter_pet
status_filter = {"All": None, "Completed": True, "Incomplete": False}[filter_status]

filtered = owner.filter_tasks(pet_name=pet_filter, completed=status_filter)
if filtered:
    st.table(
        [
            {"Pet": pet.name, "Task": task.name, "Priority": task.priority.name.title(), "Completed": task.completed}
            for pet, task in filtered
        ]
    )
else:
    st.info("No tasks match this filter.")

st.divider()

# --- Step 1 (Phase 6): Generate Schedule -> Scheduler, with sorting + conflict warnings ---
st.subheader("Build Schedule")
if st.button("Generate schedule"):
    scheduler = Scheduler(owner)
    plan = scheduler.generate_plan()
    ordered_plan = scheduler.sort_by_time(plan)

    conflicts = scheduler.detect_conflicts(ordered_plan)
    if conflicts:
        for warning in conflicts:
            st.warning(f"⚠️ {warning}")
    else:
        st.success("No scheduling conflicts detected.")

    if ordered_plan:
        st.table(
            [
                {
                    "Time": entry.start_time,
                    "Pet": entry.pet.name,
                    "Task": entry.task.name,
                    "Duration (min)": entry.task.duration,
                    "Priority": entry.task.priority.name.title(),
                }
                for entry in ordered_plan
            ]
        )
    else:
        st.info("No tasks due today.")
