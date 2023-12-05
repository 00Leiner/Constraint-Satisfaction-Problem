from ortools.sat.python import cp_model

def schedule_courses(course_units):
    if isinstance(course_units, int):
        # If course_units is an integer, generate a list from 1 to the input value.
        course_units = list(range(1, course_units + 1))

    # Constants for time slots and days.
    days = 5
    hours_per_day = 12  # 7 am to 7 pm
    time_slots = [(day, hour) for day in range(days) for hour in range(hours_per_day)]

    # Create the CP-SAT model.
    model = cp_model.CpModel()

    # Define variables representing the schedule for each course unit.
    schedule = {}
    for unit in course_units:
        for day, hour in time_slots:
            schedule[(unit, day, hour)] = model.NewBoolVar(f'schedule_{unit}_{day}_{hour}')

    # Ensure that each course unit is scheduled exactly once.
    for unit in course_units:
        model.Add(sum(schedule[(unit, day, hour)] for day, hour in time_slots) == 1)

    # Ensure that each time slot is occupied by at most one course unit.
    for day, hour in time_slots:
        model.Add(sum(schedule[(unit, day, hour)] for unit in course_units) <= 1)

    # Create a solver and solve the model.
    solver = cp_model.CpSolver()
    status = solver.Solve(model)

    # Print the solution.
    if status == cp_model.OPTIMAL:
        for unit in course_units:
            print(f"\nSchedule for Unit {unit}:")
            for day, hour in time_slots:
                if solver.Value(schedule[(unit, day, hour)]) == 1:
                    print(f"Day {day + 1}, Hour {hour + 7}:00 - {hour + 8}:00")
    else:
        print("No solution found.")

# Example: Schedule courses with different units and durations.
course_units = 3 

schedule_courses(course_units)
