# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**
I made four classes: Task, Pet, Owner, and Scheduler. Task stored activity details like time, frequency, and completion status. Pet held a list of tasks for one animal. Owner managed multiple pets. Scheduler pulled all the tasks together and handled sorting, filtering, and conflict detection.

**b. Design changes**

Yes, I added a pet_name field directly to the Task class. I did not include it at first, but when I started writing the filter and conflict methods I kept having to dig through Pet objects just to get the name. Adding it to Task directly made things a lot simpler.
---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

The scheduler considers time of day, due date, and task frequency. I prioritized time first because a daily schedule only makes sense in chronological order. Due date keeps the view focused on today, and frequency handles whether a task repeats. These felt like the most practical constraints for a pet owner checking what needs to get done.

**b. Tradeoffs**

Conflict detection only flags tasks at the exact same time. Two tasks 15 minutes apart will not trigger a warning. This is fine for a pet care app since most tasks are short and owners are not scheduling things down to the minute anyway.

---

## 3. AI Collaboration

**a. How you used AI**

I used AI to help design the class structure, generate the code, and draft the test suite. Prompts that referenced a specific file and asked for a concrete change were the most useful, like asking it to improve a specific method rather than asking something vague.

**b. Judgment and verification**

The AI suggested using a nested loop for conflict detection. I switched it to a dictionary keyed by (time, date) since it only needs one pass through the list instead of comparing every task against every other task. I wrote two tests to verify it , one that expects a conflict warning and one that expects none.

---

## 4. Testing and Verification

**a. What you tested**

I tested task completion, sorting, daily and weekly recurrence, conflict detection, and edge cases like empty pets and owners. These were important because they cover the core things the scheduler is supposed to do and the situations most likely to cause bugs.

**b. Confidence**

Pretty confident in what is covered by the tests. If I had more time I would test bad time formats, marking the same task complete twice, and a pet with duplicate task names to make sure nothing breaks unexpectedly.
---

## 5. Reflection

**a. What went well**

Building and testing the logic before touching the UI was the right call. It made connecting everything to Streamlit much less stressful because I already knew the backend worked.

**b. What you would improve**

I would add task duration so conflict detection can catch overlapping windows instead of just exact time matches. I would also add data persistence so nothing resets when the app reloads.

**c. Key takeaway**

The more specific your prompt, the better the output. Vague questions waste time. Knowing what you want before asking AI makes the whole process faster and cleaner.