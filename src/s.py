from ortools.sat.python import cp_model

class Scheduler:
    def __init__(self, rooms, students, teachers):
        # Variables
        self.rooms = rooms
        self.students = students
        self.teachers = teachers
        self.days = range(1, 6)
        self.hours = range(7, 20)
        # Initialize the CP-SAT model
        self.model = cp_model.CpModel()
        # Create the solver instance
        self.solver = cp_model.CpSolver()

        # Initialize dictionaries to store variables
        self.teacher_day_assignment = {teacher['id']: [[] for _ in self.days] for teacher in self.teachers}
        self.room_day_assignment = {room['id']: [[] for _ in self.days] for room in self.rooms}
        self.student_day_assignment = {student['id']: [[] for _ in self.days] for student in self.students}

    def create_variables(self, role):
        # Handle specialized courses for teachers
        for teacher in self.teachers:
            for day in self.days:
                for specialized_course in teacher['specialized']:
                    course_code = specialized_course['code']
                    course_type = specialized_course['type']
                    matching_rooms = [room['id'] for room in self.rooms if room['type'] == course_type]

                    for room in matching_rooms:
                        teacher_var = self.teacher_day_assignment[teacher['id']][day - 1]
                        room_var = self.room_day_assignment[room][day - 1]
                        # Add constraint: If the teacher is assigned to a specialized course, they must be in a matching room
                        self.model.AddBoolAnd([self.model.Not(teacher_var[i]), self.model.Not(room_var[i])] for i in range(len(teacher_var)))

       # Update the total hours calculation for teachers with specialized courses
        for teacher in self.teachers:
            for day in self.days:
                assignment_vars = self.teacher_day_assignment[teacher['id']][day - 1]
                total_hours_var = self.model.NewIntVar(0, 6, f"Teacher_{teacher['id']}_TotalHours_{day}")
                self.model.Add(sum(assignment_vars) == total_hours_var)

         # Handle specialized courses for students
        for student in self.students:
            student_id = student['id']
            for day in self.days:
                for course in student['courses']:
                    course_code = course['code']
                    course_type = course['type']
                    matching_rooms = [room['id'] for room in self.rooms if room['type'] == course_type]
                    student_var = self.student_day_assignment[student_id][day - 1]

                    # Add constraint: If the student is assigned to a course, they must be in a matching room
                    for room in matching_rooms:
                        room_var = self.room_day_assignment[room][day - 1]
                        self.model.AddBoolAnd([~var for var in student_var] + [~var for var in room_var])


        # Update the total hours calculation for students with specialized courses
        for student in self.students:
            student_id = student['id']
            for day in self.days:
                assignment_vars = self.student_day_assignment[student_id][day - 1]
                total_hours_var = self.model.NewIntVar(0, 6, f"Student_{student_id}_TotalHours_{day}")
                self.model.Add(sum(assignment_vars) == total_hours_var)

        # Create boolean variables for room day assignments
        self.room_day_assignment = {room['id']: [] for room in self.rooms}
        for day in self.days:
            for room in self.rooms:
                var_name = f"Room_{room['id']}_Day_{day}"
                assignment_var = self.model.NewBoolVar(var_name)
                self.room_day_assignment[room['id']].append(assignment_var)

        # Create boolean variables for teacher day assignments
        self.teacher_day_assignment = {teacher['id']: [] for teacher in self.teachers}
        for day in self.days:
            for teacher in self.teachers:
                var_name = f"Teacher_{teacher['id']}_Day_{day}"
                assignment_var = self.model.NewBoolVar(var_name)
                self.teacher_day_assignment[teacher['id']].append(assignment_var)

        # Create boolean variables for student day assignments
        self.student_day_assignment = {student['id']: [] for student in self.students}
        for day in self.days:
            for student in self.students:
                var_name = f"Student_{student['id']}_Day_{day}"
                assignment_var = self.model.NewBoolVar(var_name)
                self.student_day_assignment[student['id']].append(assignment_var)

    def specialization_constraints(self, role):
        # Ensure each role (teacher or student) is assigned based on their specialization
        if role == "teacher":
            for role_member in self.teachers:
                for day in self.days:
                    for specialized_course in role_member['specialized']:
                        course_code = specialized_course['code']
                        course_type = specialized_course['type']
                        matching_rooms = [room['id'] for room in self.rooms if room['type'] == course_type]
                        role_var = self.teacher_day_assignment[role_member['id']][day - 1]

                        # Add constraint: If the role member is assigned to a specialized course, they must be in a matching room
                        for room_id in matching_rooms:
                            room_var = self.room_day_assignment[room_id][day - 1]
                            self.model.AddBoolAnd([role_var.Not(), room_var.Not()])

        elif role == "student":
            for role_member in self.students:
                student_id = role_member['id']
                for day in self.days:
                    for course in role_member['courses']:
                        course_type = course['type']
                        matching_rooms = [room['id'] for room in self.rooms if room['type'] == course_type]
                        role_var = self.student_day_assignment[student_id][day - 1]

                        # Add constraint: If the student is assigned to a course, they must be in a matching room
                        for room_id in matching_rooms:
                            room_var = self.room_day_assignment[room_id][day - 1]
                            self.model.AddBoolAnd([role_var.Not(), room_var.Not()])

    def teacher_room_assignment_constraints(self):
        # Ensure each teacher is assigned to rooms based on their specialization type
        for teacher in self.teachers:
            for day in self.days:
                for specialized_course in teacher['specialized']:
                    course_type = specialized_course['type']
                    matching_rooms = [room['id'] for room in self.rooms if room['type'] == course_type]
                    teacher_var = self.teacher_day_assignment[teacher['id']][day - 1]

                    # Add constraint: If the teacher is assigned to a specialized course, they must be in a matching room
                    for room_id in matching_rooms:
                        room_var = self.room_day_assignment[room_id][day - 1]
                        not_teacher_var = self.model.NewBoolVar(f"Not_Teacher_{teacher['id']}_Day_{day}")
                        not_room_var = self.model.NewBoolVar(f"Not_Room_{room_id}_Day_{day}")

                        self.model.AddBoolOr([teacher_var.Not(), not_teacher_var])
                        self.model.AddBoolOr([room_var.Not(), not_room_var])
                        self.model.AddBoolOr([not_teacher_var.Not(), not_room_var.Not()])

    def time_constraints(self, role):
        # Ensure each role (teacher or student) does not exceed the maximum daily hours
        max_daily_hours = 6

        if role == "teacher":
            role_assignment = self.teacher_day_assignment
        elif role == "student":
            role_assignment = self.student_day_assignment
        else:
            return

        for role_member_key, role_member_vars in role_assignment.items():
            for day in self.days:
                self.model.Add(role_member_vars[day - 1] == max_daily_hours)


    def classroom_availability_constraints(self):
        # Ensure each classroom is not double-booked on the same day and time
        for room in self.rooms:
            for day in self.days:
                for hour in self.hours:
                    room_var = self.room_day_assignment[room['id']][day - 1]
                    self.model.AddBoolOr([room_var.Not(), self.model.NewBoolVar(f"Hour_{hour}")])

    def solve(self):
        # Create variables and constraints for teachers
        self.create_variables("teacher")
        self.teacher_room_assignment_constraints()
        self.teacher_room_assignment_constraints()  # Move this line here
        self.specialization_constraints("teacher")
        self.classroom_availability_constraints()
        self.time_constraints("teacher")

        # Create variables and constraints for students
        self.create_variables("student")
        self.specialization_constraints("student")
        self.time_constraints("student")

        # Solve the problem
        status = self.solver.Solve(self.model)

        # Print the results
        print("Solving Status:", self.solver.StatusName(status))
        if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
            print("Optimal Schedule:")
            for day in self.days:
                print(f"Day {day}:")
                # Print teacher results
                for teacher in self.teachers:
                    teacher_id = teacher['id']
                    teacher_var = self.teacher_day_assignment[teacher_id][day - 1]
                    time_assignment_var = self.model.NewIntVar(0, 6, f"Teacher_{teacher_id}_Time_{day}")
                    self.model.Add(time_assignment_var == sum(self.teacher_day_assignment[teacher_id][0:self.hours[-1]]))
                    assignment_value = self.solver.Value(teacher_var)
                    total_hours_value = self.solver.Value(time_assignment_var)

                    print(f"{teacher_id}: Assignment - {assignment_value}, Total Hours - {total_hours_value}")

                # Print student results
                for student in self.students:
                    student_id = student['id']
                    for student_day in self.student_day_assignment[student_id]:
                        print(f"Student {student_id}: Assignment - {self.solver.Value(student_day)}")

                for room in self.rooms:
                    room_id = room['id']
                    room_var = self.room_day_assignment[room_id][day - 1]
                    print(f"{room_id} on Day {day}: {self.solver.Value(room_var)}")
        else:
            print("No solution found.")

if __name__ == "__main__":
    # Load data from data.py
    from data import rooms, teachers, students

    scheduler = Scheduler(rooms, students, teachers)
    scheduler.solve()
