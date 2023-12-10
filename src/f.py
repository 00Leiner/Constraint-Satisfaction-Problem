from ortools.sat.python import cp_model

def solve_scheduling_problem():
    model = cp_model.CpModel()

    # Define parameters
    num_students = 10
    days_in_week = 5
    available_time_range = range(7, 20)  # 7am to 7pm
    max_continuous_hours = 3
    rest_duration = 2

    # Variables
    schedule = {}
    for student in range(num_students):
        for day in range(days_in_week):
            for time_slot in available_time_range:
                schedule[(student, day, time_slot)] = model.NewBoolVar(f'st_{student}_day_{day}_time_{time_slot}')

    # Constraints
    # Add constraints to ensure 5 days or less
    for student in range(num_students):
        model.Add(sum(schedule[(student, day, time_slot)] for day in range(days_in_week) for time_slot in available_time_range) <= 5)

    # Add constraints to ensure rest of 2 days
    for student in range(num_students):
        for day in range(days_in_week - rest_duration):
            model.Add(sum(schedule[(student, day + rest_day, time_slot)] for rest_day in range(rest_duration + 1) for time_slot in available_time_range) == 0)

    # Add constraints for maximum continuous learning hours
    for student in range(num_students):
        for day in range(days_in_week):
            for time_slot in range(len(available_time_range) - max_continuous_hours + 1):
                model.Add(sum(schedule.get((student, day, time_slot + i), 0) for i in range(max_continuous_hours)) <= 3)


    # Solve the model
    solver = cp_model.CpSolver()
    status = solver.Solve(model)

    if status == cp_model.OPTIMAL:
        # Retrieve the solution
        for student in range(num_students):
            for day in range(days_in_week):
                for time_slot in available_time_range:
                    if solver.Value(schedule[(student, day, time_slot)]) == 1:
                        print(f"Student {student} is scheduled on Day {day} at Time {time_slot}")
    else:
        print("No feasible solution found.")

if __name__ == "__main__":
    solve_scheduling_problem()
