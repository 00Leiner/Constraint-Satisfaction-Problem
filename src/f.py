from ortools.sat.python import cp_model

# Define Data
days = range(1, 6)  # 5 days a week (Monday to Friday)
time_slots = range(7, 19)  # Time slots from 7:00 to 18:00

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

rooms = [
    {
        'id': "1",
        'name': "Room 1",
        'type': "lec",
    }
]

# Initialize the CP-SAT solver
model = cp_model.CpModel()

# Define Variables
assignments = {}
for student in students:
    for course in student['courses']:
        for day in days:
            for start_time in time_slots:
                for room in rooms:
                    var = model.NewBoolVar(f"student_{student['id']}_course_{course['code']}_day_{day}_start_{start_time}_room_{room['id']}")
                    assignments[(student['id'], course['code'], day, start_time, room['id'])] = var

# Constraints for Consecutive Time Slot Assignment
for student in students:
    for course in student['courses']:
        for day in days:
            # Define consecutive assignment variables for the course units
            consecutive_assignments = [model.NewBoolVar(f"student_{student['id']}_course_{course['code']}_day_{day}_consecutive_{i}") for i in range(course['units'])]
            
            # Ensure consecutive time slot assignment for each unit
            for i in range(course['units']):
                model.Add(consecutive_assignments[i] == 1)
                
                # Ensure assignment to consecutive time slots
                for start_time in range(7, 16):  # Adjust range based on available time slots
                    model.Add(sum(assignments[(student['id'], course['code'], day, t, room['id'])] * (t >= start_time and t < start_time + course['units']) for t in time_slots for room in rooms) >= consecutive_assignments[i])
            
            # Ensure correct number of units for the course
            model.Add(sum(consecutive_assignments) == course['units'])

# Solve the model
solver = cp_model.CpSolver()
status = solver.Solve(model)

# Process the result
if status == cp_model.OPTIMAL:
    for student in students:
        print(f"Student ID: {student['id']}")
        for course in student['courses']:
            print(f"Course: {course['code']}")
            for day in days:
                for start_time in time_slots:
                    for room in rooms:
                        if solver.Value(assignments[(student['id'], course['code'], day, start_time, room['id'])]) == 1:
                            print(f"Day: {day}, Start Time: {start_time}:00, Room: {room['name']}")
else:
    print("No feasible solution found.")
