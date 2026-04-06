"""
app.py  —  PawPal+ Streamlit UI
Run with: python3 -m streamlit run app.py
"""

from datetime import date
import streamlit as st
from pawpal_system import Owner, Pet, Task, Scheduler

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="wide")
st.title("🐾 PawPal+")
st.caption("Smart pet-care scheduling for busy owners.")

# ── Session state bootstrap ───────────────────────────────────────────────────
if "owner" not in st.session_state:
    st.session_state.owner = None
if "scheduler" not in st.session_state:
    st.session_state.scheduler = None

# ── Sidebar – Owner & Pet setup ───────────────────────────────────────────────
with st.sidebar:
    st.header("👤 Owner")
    owner_name = st.text_input("Your name", value="Jordan")
    if st.button("Set owner", use_container_width=True):
        st.session_state.owner     = Owner(owner_name)
        st.session_state.scheduler = Scheduler(st.session_state.owner)
        st.success(f"Welcome, {owner_name}!")

    st.divider()
    st.header("🐶 Add a Pet")
    pet_name    = st.text_input("Pet name", value="Mochi")
    pet_species = st.selectbox("Species", ["dog", "cat", "rabbit", "bird", "other"])
    if st.button("Add pet", use_container_width=True):
        if st.session_state.owner is None:
            st.error("Set an owner first.")
        else:
            st.session_state.owner.add_pet(Pet(pet_name, pet_species))
            st.success(f"{pet_name} added!")

    if st.session_state.owner:
        st.divider()
        st.subheader("Current pets")
        for pet in st.session_state.owner.pets:
            st.write(f"• {pet}")

# ── Guard ─────────────────────────────────────────────────────────────────────
if st.session_state.owner is None:
    st.info("👈 Set an owner name in the sidebar to get started.")
    st.stop()

owner:     Owner     = st.session_state.owner
scheduler: Scheduler = st.session_state.scheduler

tab_add, tab_schedule, tab_complete = st.tabs(
    ["➕ Add Task", "📅 Today's Schedule", "✅ Complete a Task"]
)

# ── Tab 1: Add Task ───────────────────────────────────────────────────────────
with tab_add:
    st.subheader("Add a Task")
    if not owner.pets:
        st.warning("Add at least one pet first (sidebar).")
    else:
        col1, col2 = st.columns(2)
        with col1:
            target_pet = st.selectbox("Assign to pet", [p.name for p in owner.pets], key="add_pet")
            task_title = st.text_input("Task title", value="Morning walk")
            task_time  = st.text_input("Time (HH:MM)", value="07:30")
        with col2:
            duration  = st.number_input("Duration (min)", 1, 480, 20)
            priority  = st.selectbox("Priority", ["low", "medium", "high"], index=1)
            frequency = st.selectbox("Frequency", ["once", "daily", "weekly"])
            due_date  = st.date_input("Due date", value=date.today())

        if st.button("Add task", type="primary"):
            try:
                h, m = map(int, task_time.split(":"))
                assert 0 <= h <= 23 and 0 <= m <= 59
            except Exception:
                st.error("Time must be in HH:MM format (e.g. 07:30).")
            else:
                new_task = Task(
                    title=task_title,
                    time=task_time,
                    duration_minutes=int(duration),
                    priority=priority,
                    frequency=frequency,
                    due_date=due_date,
                )
                for pet in owner.pets:
                    if pet.name == target_pet:
                        pet.add_task(new_task)
                st.success(f"'{task_title}' added to {target_pet}!")

# ── Tab 2: Schedule ───────────────────────────────────────────────────────────
with tab_schedule:
    st.subheader("📅 Today's Schedule")
    view_date  = st.date_input("View schedule for", value=date.today(), key="view_date")
    filter_pet = st.selectbox("Filter by pet", ["All"] + [p.name for p in owner.pets], key="filter_pet")

    schedule = scheduler.sort_by_time()
    schedule = [
        (n, t) for n, t in schedule
        if t.due_date == view_date and (filter_pet == "All" or n == filter_pet)
    ]

    conflicts = scheduler.detect_conflicts()
    if conflicts:
        with st.expander(f"⚠️ {len(conflicts)} conflict(s) detected", expanded=True):
            for w in conflicts:
                st.warning(w)

    if not schedule:
        st.info("No tasks for this date / filter.")
    else:
        PRIORITY_EMOJI = {"high": "🔴", "medium": "🟡", "low": "🟢"}
        STATUS_EMOJI   = {True: "✅", False: "⏳"}
        rows = [
            {
                "Status":   STATUS_EMOJI[t.completed],
                "Time":     t.time,
                "Task":     t.title,
                "Pet":      n,
                "Duration": f"{t.duration_minutes} min",
                "Priority": f"{PRIORITY_EMOJI[t.priority]} {t.priority.capitalize()}",
                "Freq":     t.frequency.capitalize(),
            }
            for n, t in schedule
        ]
        st.table(rows)
        st.caption(f"{len(schedule)} task(s) shown.")

# ── Tab 3: Complete a Task ────────────────────────────────────────────────────
with tab_complete:
    st.subheader("✅ Mark Task Complete")
    if not owner.pets:
        st.warning("No pets added yet.")
    else:
        comp_pet = st.selectbox("Pet", [p.name for p in owner.pets], key="comp_pet")
        incomplete = [
            t.title
            for pet in owner.pets if pet.name == comp_pet
            for t in pet.tasks if not t.completed
        ]
        if not incomplete:
            st.info(f"No incomplete tasks for {comp_pet}.")
        else:
            comp_task = st.selectbox("Task to complete", incomplete)
            if st.button("Mark complete", type="primary"):
                msg = scheduler.mark_task_complete(comp_pet, comp_task)
                if "✅" in msg:
                    st.success(msg)
                else:
                    st.warning(msg)
