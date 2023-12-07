from ortools.sat.python import cp_model

class ScheduleSolutionPrinter(cp_model.CpSolverSolutionCallback):
    def __init__(self, working, resting, max_solutions):
        cp_model.CpSolverSolutionCallback.__init__(self)
        self.working = working
        self.resting = resting
        self.solutions = []
        self.solution_count = 0
        self.max_solutions = max_solutions

    def on_solution_callback(self):
        current_solution = []
        for day in range(len(self.working)):
            current_solution.append((day + 1, 'Working' if self.Value(self.working[day]) else 'Resting'))
        self.solutions.append(current_solution)
        self.solution_count += 1

        if self.solution_count >= self.max_solutions:
            self.StopSearch()

    def get_solutions(self):
        return self.solutions

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

    # Limit the number of solutions to 3
    max_solutions = 3

    # Create a solution collector
    solution_printer = ScheduleSolutionPrinter(working, resting, max_solutions)

    # Create a solver and solve the model
    solver = cp_model.CpSolver()
    solver.SearchForAllSolutions(model, solution_printer)

    # Print all solutions
    for solution in solution_printer.get_solutions():
        print("Solution:")
        for day, status in solution:
            print(f"Day {day}: {status}")
        print()

if __name__ == "__main__":
    create_worker_schedule()
