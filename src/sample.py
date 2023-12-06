from ortools.sat.python import cp_model
from collections import namedtuple

# Constants
DAYS = 5
HOURS_PER_DAY = 12
HOUR_START = 7

TimeSlot = namedtuple('TimeSlot', ['day', 'hour'])

def schedule_courses(course_and_unit):
    # Create the CP-SAT model.
    model = cp_model.CpModel()
    # Create a solver and solve the model.
    solver = cp_model.CpSolver()
    status = solver.Solve(model)

    # Extract courses and units from the dictionary.
    courses = list(course_and_unit.keys())

    # Constants for time slots and days.
    time_slots = [TimeSlot(day, hour) for day in range(DAYS) for hour in range(HOURS_PER_DAY)]
    
    # Define variables representing the schedule for each course unit.
    course_schedule = {}
    for course in courses:
        for unit in range(1, int(course_and_unit[course]) + 1):
            for time_slot in time_slots:
                course_schedule[(course, unit, time_slot)] = model.NewBoolVar(f'schedule_{course}_{unit}_{time_slot.day}_{time_slot.hour}')

    # Ensure that each course unit is scheduled exactly once.
    for course in courses:
        for unit in range(1, int(course_and_unit[course]) + 1):
            model.Add(sum(course_schedule[(
                course, unit, time_slot)
                ] for time_slot in time_slots) == 1)

    # Ensure that each time slot is occupied by at most one course unit.
    for time_slot in time_slots:
        model.Add(sum(course_schedule[(course, unit, time_slot)] for course in courses for unit in range(1, int(course_and_unit[course]) + 1)) <= 1)


    # Print the solution.
    if status == cp_model.OPTIMAL:
        for course in courses:
            print(f"\n{course} Schedule:")
            for unit in range(1, int(course_and_unit[course]) + 1):
                print(f"\nSchedule for Unit {unit}:")
                for time_slot in time_slots:
                    if solver.Value(course_schedule[(course, unit, time_slot)]) == 1:
                        print(f"Day {time_slot.day + 1}, Hour {time_slot.hour + HOUR_START}:00 - {time_slot.hour + HOUR_START + 1}:00")
    else:
        print(f"No solution found. Solver status: {solver.StatusName(status)}")

# Example: Schedule courses with different units and durations.
course_and_unit = {
    'course1': '3',
    'course2': '3',
    'course3': '2',
    'course4': '2',
    'course5': '3',
    'course6': '1',
    'course7': '3',
    'course8': '3',
    'course9': '2',
    'course10': '2',
    'course11': '3',
    'course12': '1'
}

schedule_courses(course_and_unit)
