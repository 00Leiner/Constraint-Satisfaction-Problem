from ortools.sat.python import cp_model

def schedule_courses(course_units, course_durations):
    # Constants for time slots and days.
    days = 5
    hours_per_day = 12  # 7 am to 7 pm
    time_slots = [(day, hour) for day in range(days) for hour in range(hours_per_day)]

    # Create the CP-SAT model.
    model = cp_model.CpModel()

    # Define variables representing the schedule for each course unit.
    schedule = {}
    for unit in range(len(course_units)):
        for day, hour in time_slots:
            schedule[(unit, day, hour)] = model.NewBoolVar(f'schedule_{unit}_{day}_{hour}')

    # Ensure that each course unit is scheduled exactly once.
    for unit in range(len(course_units)):
        model.Add(sum(schedule[(unit, day, hour)] for day, hour in time_slots) == 1)

    # Ensure that each time slot is occupied by at most one course unit.
    for day, hour in time_slots:
        model.Add(sum(schedule[(unit, day, hour)] for unit in range(len(course_units))) <= 1)

    # Add a constraint to ensure that the total duration is met.
    for unit in range(len(course_units)):
        model.Add(
            sum(schedule[(unit, day, hour)] * course_durations[unit] for day, hour in time_slots) == course_durations[unit]
        )

    # Create a solver and solve the model multiple times.
    solver = cp_model.CpSolver()
    solution_count = 0
    while solver.Solve(model) == cp_model.OPTIMAL:
        solution_count += 1
        print(f"\nSolution {solution_count}:")
        for unit in range(len(course_units)):
            print(f"Schedule for Unit {unit + 1}:")
            for day, hour in time_slots:
                if solver.Value(schedule[(unit, day, hour)]) == 1:
                    print(f"Day {day + 1}, Hour {hour + 7}:00 - {hour + 8}:00")

        # Exclude the current solution to find the next one.
        model.Add(sum(schedule[(unit, day, hour)] for unit in range(len(course_units)) for day, hour in time_slots
                      if solver.Value(schedule[(unit, day, hour)]) == 1) < len(course_units))

    if solution_count == 0:
        print("No solution found.")

# Example: Schedule courses with different units and durations.
course_units = [1, 2, 3]  # Course units
course_durations = [2, 3, 1]  # Duration of each course unit in hours

schedule_courses(course_units, course_durations)
