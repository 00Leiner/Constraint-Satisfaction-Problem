from ortools.sat.python import cp_model

def schedule_courses(students, teachers, rooms):
    model = cp_model.CpModel()  # Initialize CP-SAT model
    
    # Create variables for each assignment
    assignments = []
    for student in range(len(students)):
        for teacher in range(len(teachers)):
            for room in range(len(rooms)):
                day = model.NewIntVar(0, 6, f'day_{student}_{teacher}_{room}')  # Days 0-6 represent Mon-Sun
                time = model.NewIntVar(0, 23, f'time_{student}_{teacher}_{room}')  # Hours 0-23 represent time
                
                assignments.append((student, teacher, room, day, time))
    
    # Add constraints
    for i in range(len(assignments)):
        for j in range(i + 1, len(assignments)):
            student_i, teacher_i, room_i, day_i, time_i = assignments[i]
            student_j, teacher_j, room_j, day_j, time_j = assignments[j]
            
            # Ensure no overlapping for the same room and time
            model.Add(day_i != day_j).OnlyEnforceIf([time_i == time_j])
            
            # Ensure no overlapping for the same teacher and time
            model.Add(day_i != day_j).OnlyEnforceIf([teacher_i == teacher_j])
            
            # Ensure no overlapping for the same student and time
            model.Add(day_i != day_j).OnlyEnforceIf([student_i == student_j])
    
    # Solve the model
    solver = cp_model.CpSolver()
    status = solver.Solve(model)
    
    # Print the assignments
    if status == cp_model.OPTIMAL:
        for student, teacher, room, day, time in assignments:
            print(f"{students[student]}, {teachers[teacher]}, {rooms[room]}, {solver.Value(day)}, {solver.Value(time)}, {teachers[teacher]}")
    else:
        print("No solution found.")

# Example data
students = ['student1', 'student2']
teachers = ['teacher1', 'teacher2']
rooms = ['room1', 'room2']

# Schedule courses using CP-SAT solver
schedule_courses(students, teachers, rooms)
