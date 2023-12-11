from ortools.sat.python import cp_model

# Create the CP-SAT model
model = cp_model.CpModel()

# Define the variables and domains
teachers = {'teacher1': 'math', 'teacher2': 'science'}
rooms = {'room1': 'lab', 'room2': 'lec'}
programs = {
    'program1': {
        'courses': {
            'math': {'unit': 3, 'type': 'lab'},
            'science': {'unit': 4, 'type': 'lec'}
        }
    }
}

# Binary variables for program, teacher, room, day, hour, and duration
program_vars = {}
teacher_vars = {}
room_vars = {}
day_vars = {}
hour_vars = {}
duration_vars = {}

for program, program_data in programs.items():
    for course, course_data in program_data['courses'].items():
        for teacher, subject in teachers.items():
            program_vars[program, course, teacher] = model.NewBoolVar(
                f'{program}_{course}_{teacher}_scheduled'
            )

        for room, room_type in rooms.items():
            room_vars[program, course, room] = model.NewBoolVar(
                f'{program}_{course}_{room}_scheduled'
            )

        for day in range(1, 7 + 1):  # 6 days in a week
            day_vars[program, course, day] = model.NewBoolVar(
                f'{program}_{course}_{day}_scheduled'
            )

        for hour in range(1, 7 + 1):  # 7 hours in a day
            hour_vars[program, course, hour] = model.NewBoolVar(
                f'{program}_{course}_{hour}_scheduled'
            )

        for duration in range(1, 3 + 1):  # Maximum duration is 3 hours
            duration_vars[program, course, duration] = model.NewBoolVar(
                f'{program}_{course}_{duration}_scheduled'
            )

# Displaying a few variables to demonstrate
print("Program Variables:")
for var in program_vars:
    print(var, program_vars[var])

print("\nRoom Variables:")
for var in room_vars:
    print(var, room_vars[var])

# Continue similarly for teacher, day, hour, and duration variables
