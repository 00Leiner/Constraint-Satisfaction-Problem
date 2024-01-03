from ortools.sat.python import cp_model

def assign_items_to_slots(items, slots):
    # Create a CP-SAT model
    model = cp_model.CpModel()

    # Create variables for start and end positions for each item
    start_positions = {}
    end_positions = {}
    for item in items:
        start_positions[item] = model.NewIntVar(0, len(slots), f'start_{item}')
        end_positions[item] = model.NewIntVar(0, len(slots), f'end_{item}')

    # Constraint: Ensure each item is assigned to 3 consecutive slots
    for item in items:
        model.Add(end_positions[item] == start_positions[item] + 2)

    # Constraint: Ensure no two items share the same 3 consecutive slots
    for item1 in items:
        for item2 in items:
            if item1 != item2:
                model.Add(start_positions[item1] != start_positions[item2])

    # Create a solver and solve the model
    solver = cp_model.CpSolver()
    status = solver.Solve(model)

    # Check if solution found
    if status == cp_model.OPTIMAL:
        assignment_solution = {}
        for item in items:
            start = solver.Value(start_positions[item])
            end = solver.Value(end_positions[item])
            assignment_solution[item] = (start, end)
        return assignment_solution
    else:
        return None

# Example data
items = ['item1', 'item2', 'item3', 'item4', 'item5', 'item6',  'item7', 'item8']
slots = range(9)

# Solve the assignment problem
solution = assign_items_to_slots(items, slots)

# Print the solution
if solution:
    for item, (start, end) in solution.items():
        print(f"{item} is assigned to slots from {start + 1} to {end + 1}")
else:
    print("No feasible solution found.")
