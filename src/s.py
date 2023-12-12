from ortools.sat.python import cp_model

def create_worker_schedule():
    model = cp_model.CpModel()

    # Number of days in a week
    num_days = 7

    # Number of days a worker can work in a week
    work_days = 5

    # Create variables for each day indicating whether the worker is working on that day
    working = [model.NewBoolVar(f'working_{day}') for day in range(num_days)]

    # Create variables for each day indicating whether the worker is resting on that day
    resting = [model.NewBoolVar(f'resting_{day}') for day in range(num_days)]

    # The worker should be either working or resting on each day
    for day in range(num_days):
        model.Add(working[day] + resting[day] == 1)

    # The worker should work for 5 days in a week
    model.Add(sum(working) == work_days)

    # The worker should have 2 days of rest in a week
    model.Add(sum(resting) == 2)

    # Create a solver and solve the model
    solver = cp_model.CpSolver()
    status = solver.Solve(model)

    # Print the schedule without showing resting days
    if status == cp_model.OPTIMAL:
        print("Optimal Schedule:")
        for day in range(num_days):
            if solver.Value(working[day]):
                print(f"Day {day + 1}: Working")
    else:
        print("No solution found.")

if __name__ == "__main__":
    create_worker_schedule()
