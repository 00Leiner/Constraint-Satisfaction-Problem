from ortools.sat.python import cp_model

class ScheduleSolutionPrinter(cp_model.CpSolverSolutionCallback):
    def __init__(self, working, worker_names, max_solutions):
        cp_model.CpSolverSolutionCallback.__init__(self)
        self.working = working
        self.worker_names = worker_names
        self.solutions = []
        self.solution_count = 0
        self.max_solutions = max_solutions

    def on_solution_callback(self):
        current_solution = []
        for worker in range(len(self.working)):
            for day in range(len(self.working[worker])):
                current_solution.append((self.worker_names[worker], day + 1, 'Working' if self.Value(self.working[worker][day]) else 'Resting'))
        self.solutions.append(current_solution)
        self.solution_count += 1

        if self.solution_count >= self.max_solutions:
            self.StopSearch()

    def get_solutions(self):
        return self.solutions

def create_worker_schedule(max_solutions=3):
    model = cp_model.CpModel()

    # Number of days in a week
    num_days = 7

    # Number of working days for each worker
    work_days_per_week = 3

    # Worker names
    worker_names = ['john', 'mark']

    # Create variables for each day indicating whether each worker is working on that day
    working = [[model.NewBoolVar(
        f'working_{worker}_{day}'
        ) for day in range(num_days)] for worker in worker_names]

    # Each worker should work for 3 days in a week
    for worker in range(len(worker_names)):
        model.Add(sum(working[worker]) == work_days_per_week)

    # Workers should have non-overlapping schedules
    for day in range(num_days):
        model.Add(sum(working[worker][day] for worker in range(len(worker_names))) <= 1)

    # Create a solution printer to collect and print solutions
    solution_printer = ScheduleSolutionPrinter(working, worker_names, max_solutions)
    solver = cp_model.CpSolver()

    # Solve the model and print solutions
    solver.SearchForAllSolutions(model, solution_printer)

    # Print all solutions
    all_solutions = solution_printer.get_solutions()
    for i, solution in enumerate(all_solutions):
        print(f"Solution {i + 1}:")
        for worker, day, status in solution:
            print(f"Worker {worker}: Day {day}: {status}")

if __name__ == "__main__":
    create_worker_schedule()
