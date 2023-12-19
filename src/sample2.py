from ortools.sat.python import cp_model

def create_schedule():
    model = cp_model.CpModel()

    # Define rooms, teachers, and students
    rooms = ["Room1", "Room2", "Room3"]
    teachers = ["Teacher1", "Teacher2", "Teacher3"]
    students = ["Student1", "Student2", "Student3"]

    # Define courses and their durations
    courses = {
        "Math": {"duration": 2, "teacher": "Teacher1", "students": ["Student1", "Student2"]},
        "Physics": {"duration": 3, "teacher": "Teacher2", "students": ["Student2", "Student3"]},
        "History": {"duration": 1, "teacher": "Teacher3", "students": ["Student1", "Student3"]},
    }

    # Define time slots
    time_slots = range(10)  # Assuming 10 time slots in a day

    # Variables for room assignments
    room_assignments = {s: model.NewIntVar(0, len(rooms) - 1, f"Room_{s}") for s in students}

    # Variables for teacher assignments
    teacher_assignments = {s: model.NewIntVar(0, len(teachers) - 1, f"Teacher_{s}") for s in students}

    # Variables for time slot assignments
    time_slot_assignments = {s: model.NewIntVar(0, len(time_slots) - 1, f"TimeSlot_{s}") for s in students}

    # Constraints for room assignments
    for s in students:
        course = courses[s]
        model.AddElement(room_assignments[s], rooms).OnlyEnforceIf(
            model.Element(teacher_assignments[s], teachers) == teacher_assignments[s]
        )

    # Constraints for teacher assignments
    for s in students:
        course = courses[s]
        model.AddElement(teacher_assignments[s], teachers).OnlyEnforceIf(
            model.Element(time_slot_assignments[s], time_slots) == time_slot_assignments[s]
        )

    # Constraints for time slot assignments
    for s in students:
        model.AddElement(time_slot_assignments[s], time_slots).OnlyEnforceIf(
            model.Element(room_assignments[s], rooms) == room_assignments[s]
        )

    # Avoid conflicts: No two students can have classes at the same time in the same room
    for s1 in students:
        for s2 in students:
            if s1 != s2:
                model.AddBoolOr([
                    model.Element(time_slot_assignments[s1], time_slots) !=
                    model.Element(time_slot_assignments[s2], time_slots),
                    model.Element(room_assignments[s1], rooms) !=
                    model.Element(room_assignments[s2], rooms)
                ])

    # Meet curriculum requirements: Each student must attend their assigned courses
    for s in students:
        course = courses[s]
        model.AddElement(time_slot_assignments[s], time_slots).OnlyEnforceIf(
            model.Element(room_assignments[s], rooms) == room_assignments[s],
            model.Element(teacher_assignments[s], teachers) == teacher_assignments[s]
        )

    # Additional rules for teachers
    for t in teachers:
        # Rule: Teachers should work 6 hours per day
        model.Add(sum(
            [model.Element(teacher_assignments[s], teachers) == teachers.index(t) for s in students]
        ) <= 6)

        # Rule: No more than 3 hours of continuous teaching
        for i in range(len(time_slots) - 2):
            model.AddBoolOr([
                model.Element(teacher_assignments[s], teachers) == teachers.index(t)
                for s in students
                if i <= model.Element(time_slot_assignments[s], time_slots) <= i + 2
            ])

        # Rule: 1 day rest in 6 days of working in a week
        model.Add(sum(
            [model.Element(teacher_assignments[s], teachers) == teachers.index(t) for s in students]
        ) <= 5)

        # Rule: Force to teach (customize based on specific requirements)
        # For example, you might want to force a teacher to teach a specific course or block.

    # Additional rules for students
    for s in students:
        # Rule: No more than 3 hours of continuous learning
        for i in range(len(time_slots) - 2):
            model.AddBoolOr([
                model.Element(time_slot_assignments[s], time_slots) == i,
                model.Element(time_slot_assignments[s], time_slots) == i + 1,
                model.Element(time_slot_assignments[s], time_slots) == i + 2
            ])

        # Rule: Each student can have classes for a maximum of 5 days per week
        model.Add(sum(
            [model.Element(time_slot_assignments[s], time_slots) >= 0 for s in students]
        ) <= 5)

    # Objective: Maximize the usage of rooms (customize based on your goals)
    model.Maximize(sum([model.Element(room_assignments[s], rooms) >= 0 for s in students]))

    # Create the solver and solve the problem
    solver = cp_model.CpSolver()
    status = solver.Solve(model)

    # Print or process the results based on the solver status
    if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
        print("Optimal Schedule:")
        for s in students:
            print(f"{s}'s schedule - Room: {solver.Value(room_assignments[s])}, Teacher: {solver.Value(teacher_assignments[s])}, Time Slot: {solver.Value(time_slot_assignments[s])}")
        print(f"Total room usage: {solver.ObjectiveValue()}")
    else:
        print("No solution found.")

if __name__ == "__main__":
    create_schedule()
