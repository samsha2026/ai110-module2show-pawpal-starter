"""
main.py
CLI demo — run with: python3 main.py
Verifies that the PawPal+ backend works before touching the Streamlit UI.
"""

from datetime import date
from pawpal_system import Owner, Pet, Task, Scheduler


def main() -> None:
    # ── Setup ──────────────────────────────────────────────────────────────
    owner = Owner("Jordan")

    mochi = Pet("Mochi", "dog")
    luna  = Pet("Luna", "cat")
    owner.add_pet(mochi)
    owner.add_pet(luna)

    today = date.today()

    # ── Tasks for Mochi ────────────────────────────────────────────────────
    mochi.add_task(Task("Evening walk",   "18:00", 30,  "high",   "daily",  due_date=today))
    mochi.add_task(Task("Morning walk",   "07:30", 25,  "high",   "daily",  due_date=today))
    mochi.add_task(Task("Breakfast",      "07:00", 5,   "high",   "daily",  due_date=today))
    mochi.add_task(Task("Flea treatment", "10:00", 5,   "medium", "weekly", due_date=today))

    # ── Tasks for Luna ─────────────────────────────────────────────────────
    luna.add_task(Task("Wet food",       "07:15", 5,  "high",   "daily", due_date=today))
    luna.add_task(Task("Playtime",       "19:00", 15, "medium", "daily", due_date=today))
    # Intentional conflict: overlaps Breakfast (07:00 + 5 min)
    luna.add_task(Task("Hairball meds",  "07:03", 3,  "high",   "daily", due_date=today))

    # ── Scheduler ─────────────────────────────────────────────────────────
    scheduler = Scheduler(owner)
    print(scheduler.summary())

    # ── Filtering ─────────────────────────────────────────────────────────
    print("\n🔍 Mochi's tasks only:")
    for pet_name, task in scheduler.filter_by_pet("Mochi"):
        print(f"  {task}")

    print("\n🔴 High-priority tasks:")
    for pet_name, task in scheduler.filter_by_priority("high"):
        print(f"  {task}  [{pet_name}]")

    # ── Mark a recurring task complete ─────────────────────────────────────
    print("\n" + "─" * 40)
    print("Marking 'Morning walk' complete...")
    msg = scheduler.mark_task_complete("Mochi", "Morning walk")
    print(msg)

    print("\nMochi's tasks after completion:")
    for _, task in scheduler.filter_by_pet("Mochi"):
        print(f"  {task}  (due: {task.due_date})")


if __name__ == "__main__":
    main()