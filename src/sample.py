from ortools.sat.python import cp_model

def create_string_assignment_model():
    model = cp_model.CpModel()

    # Constants
    courses = ["Math", "Physics", "English", "History"]
    rooms = ["Room A", "Room B", "Room C"]
    teachers = ["Teacher X", "Teacher Y", "Teacher Z"]
    days = ["Monday", "Tuesday", "Wednesday"]
    
    # Variables
    course_to_room = [model.NewIntVar(0, len(rooms) - 1, f'{course}_to_{room}') for course in courses for room in rooms]
    course_to_teacher = [model.NewIntVar(0, len(teachers) - 1, f'{course}_to_{teacher}') for course in courses for teacher in teachers]
    course_to_day = [model.NewIntVar(0, len(days) - 1, f'{course}_to_{day}') for course in courses for day in days]

    # Constraints: Each course is assigned to exactly one room, teacher, and day
    for i, course in enumerate(courses):
        model.Add(sum(course_to_room[i * len(rooms) + j] for j in range(len(rooms))) == 1)
        model.Add(sum(course_to_teacher[i * len(teachers) + j] for j in range(len(teachers))) == 1)
        model.Add(sum(course_to_day[i * len(days) + j] for j in range(len(days))) == 1)

    # Additional constraints can be added based on your specific requirements

    return model, course_to_room, course_to_teacher, course_to_day, courses, rooms, teachers, days

def solve_string_assignment_problem():
    model, course_to_room, course_to_teacher, course_to_day, courses, rooms, teachers, days = create_string_assignment_model()
    solver = cp_model.CpSolver()

    status = solver.Solve(model)

    if status == cp_model.OPTIMAL:
        for i, course in enumerate(courses):
            assigned_room = rooms[solver.Value(course_to_room[i * len(rooms)])]
            assigned_teacher = teachers[solver.Value(course_to_teacher[i * len(teachers)])]
            assigned_day = days[solver.Value(course_to_day[i * len(days)])]
            print(f'{course} is assigned to {assigned_room}, taught by {assigned_teacher}, on {assigned_day}')
    else:
        print('No solution found.')

if __name__ == "__main__":
    solve_string_assignment_problem()
