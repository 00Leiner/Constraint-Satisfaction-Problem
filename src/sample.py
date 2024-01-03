from ortools.sat.python import cp_model

# Data
days = range(1, 6)  # 5 days a week (Monday to Friday)
for i in days:
    print(i)
time_slots = [(day, start_time) for day in days for start_time in range(7, 19)]  # Time slots from 7:00 to 19:00

students = [
    {
        'id': "1",
        'courses': [
            {
                'code': "CS 2101",
                'units': 3,
                'type': "lec",
            }
        ]
    }
]

# Initialize the CP-SAT solver
model = cp_model.CpModel()

# Define Variables
assignments = {}
for student in students:
    for course in student['courses']:
        for day, start_time in time_slots:
            var = model.NewBoolVar(f"student_{student['id']}_course_{course['code']}_day_{day}_start_{start_time}")
            assignments[(student['id'], course['code'], day, start_time)] = var

# Add Constraints
for student in students:
    for course in student['courses']:

        for day in days:
            model.Add(sum(assignments[(student['id'], course['code'], day, start_time)] for start_time in range(7, 19)) == course['units'])  # Ensure units match
            
# Solve the model
solver = cp_model.CpSolver()
status = solver.Solve(model)

# Process the result
if status == cp_model.OPTIMAL:
    for student in students:
        for course in student['courses']:
            print(f"Student ID: {student['id']}, Course: {course['code']}")
            for day in days:
                for start_time in range(7, 19):
                    if solver.Value(assignments[(student['id'], course['code'], day, start_time)]) == 1:
                        dismissal_time = start_time + 3  # Assuming 3 units = 3 hours
                        print(f"Class Time: {start_time}:00, Dismissal Time: {dismissal_time}:00")
else:
    print("No feasible solution found.")
