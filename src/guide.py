from ortools.sat.python import cp_model
from itertools import combinations

def schedule_assignments(hours):
    # Create the CP-SAT model
    model = cp_model.CpModel()

    # Define the days and time constraints
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
    start_time = 7  # 7am
    end_time = 19   # 7pm

    # Define the variables
    assignments = {}
    for day in days:
        assignments[day] = model.NewIntVar(start_time, end_time - hours, f'{day}')

    # Ensure that each day has at most one assignment
    for day in days:
        for other_day in days:
            if other_day != day:
                # Ensure non-overlapping assignments
                model.Add(assignments[day] + hours <= assignments[other_day] or assignments[other_day] + hours <= assignments[day])

    # Ensure that the total number of assignments is equal to the number of hours
    model.Add(sum(model.NewBoolVar(f'count_{day}') for day in days) == hours)

    # Create the solver and solve the model
    solver = cp_model.CpSolver()
    status = solver.Solve(model)

    # Print all possible solutions
    if status == cp_model.OPTIMAL:
        for combination in combinations(days, hours):
            valid_combination = all(solver.Value(model.NewBoolVar(f'count_{day}')) == 1 for day in combination)
            if valid_combination:
                for day in combination:
                    start_hour = solver.Value(assignments[day])
                    print(f'Assignment for {hours} hours on {day} from {start_hour}:00 to {start_hour + hours}:00')
                print('---')
    else:
        print('No solution found.')

# Example usage:
schedule_assignments(3)
