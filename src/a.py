from ortools.sat.python import cp_model

def main():
    # Create CP model
    cp_model_ = cp_model.CpModel()

    # Define courses and their units
    courses_units = {'Course A': 3, 'Course B': 2, 'Course C': 1}
    time_slots = [(7, 10), (10, 13), (13, 16), (16, 19), (19, 22), (22, 25)]

    course_time_slots = {}
    for course in courses_units:
        for unit in range(courses_units[course]):
            course_time_slots[(course, unit)] = cp_model_.NewIntVar(0, len(time_slots) - 1, f'{course}_unit_{unit}')

    for course in courses_units:
        for unit in range(courses_units[course] - 1):
            cp_model_.Add(course_time_slots[(course, unit + 1)] == course_time_slots[(course, unit)] + 1)

    # Add non-overlapping constraints
    for course1 in courses_units:
        for course2 in courses_units:
            if course1 != course2:
                for unit1 in range(courses_units[course1]):
                    for unit2 in range(courses_units[course2]):
                        cp_model_.Add(course_time_slots[(course1, unit1)] != course_time_slots[(course2, unit2)])

    # Find multiple feasible solutions
    cp_solver = cp_model.CpSolver()
    cp_status = cp_solver.Solve(cp_model_)

    while cp_status == cp_model.OPTIMAL:
        # Group assignments by courses
        course_assignments = {}
        for (course, unit), var in course_time_slots.items():
            time_slot_index = cp_solver.Value(var)
            if course not in course_assignments:
                course_assignments[course] = []
            course_assignments[course].append(time_slot_index)

        # Process and print assignments
        for course, assignments in course_assignments.items():
            start_time = time_slots[assignments[0]][0]
            end_time = time_slots[assignments[-1]][1]
            print(f'{course} assigned to Time Slot {tuple(assignments)} ({start_time}:00 - {end_time}:00)')

        # Exclude current solution
        for (course, unit), var in course_time_slots.items():
            cp_model_.Add(var != cp_solver.Value(var))

        # Search for the next feasible solution
        cp_status = cp_solver.Solve(cp_model_)

if __name__ == '__main__':
    main()
