from ortools.sat.python import cp_model

class Scheduler:
    def __init__(self, rooms, students, teachers, days, time_slots):
        self.rooms = rooms
        self.students = students
        self.teachers = teachers

        self.model = cp_model.CpModel()
        self.solver = cp_model.CpSolver()

        # set up variables
        self.rooms_variable = self.define_rooms_variable()
        self.teachers_variable = self.define_teachers_variable()
        self.students_variable = self.define_students_variable()

        # Dictionary to store values
        self.room_assignments = {}  
        self.teacher_assignments = {}  

        # Populate variables based on data
        self.declare_room_assignments()
        self.declare_teacher_assignments()

        # Define constraints and solve the model
        self.define_constraints()
        self.solve()

    def define_rooms_variable(self):
        room_variables = {}
        for room in self.rooms:
            room_name = room['name']
            room_type = room['type']
            room_variables[(room_name, room_type)] = self.model.NewBoolVar(f"{room_name}, {room_type}")
        return room_variables
    
    def define_teachers_variable(self):
        teachers_variable = {}
        for teacher in self.teachers:
            teacher_name = teacher['name']
            teacher_specialized = teacher['specialized']
            teachers_variable[(teacher_name, teacher_specialized)] = self.model.NewBoolVar(f"{teacher_name}, {teacher_specialized}")
        return teachers_variable
    
    def define_students_variable(self):
        students_variable = {}
        for student in self.students:
            student_program = student['program']
            student_year = student['year']
            student_semester = student['semester']
            student_block = student['block']
            student_courses = student['courses']
            for course in student_courses:
                course_code = course['code']
                course_description = course['description']
                course_units = course['units']
                course_type = course['type']
                assign = (student_program, student_year, student_semester, student_block, course_code, course_description, course_units, course_type)
                students_variable[assign] = self.model.NewBoolVar(str(assign))
        return students_variable

    def declare_room_assignments(self):
        for room_name, room_type in self.rooms_variable:
            for student_program, student_year, student_semester, student_block, course_code, course_description, course_units, course_type in self.students_variable:
                if room_type == course_type:
                    assign = (student_program, student_year, student_semester, student_block, course_code, course_description, course_units, course_type, room_name, room_type)
                    self.room_assignments[assign] = self.model.NewBoolVar(str(assign))

    def declare_teacher_assignments(self):
        for teacher_name, teacher_specialized in self.teachers_variable:
            for student_program, student_year, student_semester, student_block, course_code, course_description, course_units, course_type in self.students_variable:
                if teacher_specialized == course_code:
                    assign = (student_program, student_year, student_semester, student_block, course_code, course_description, course_units, course_type, teacher_name, teacher_specialized)
                    self.teacher_assignments[assign] = self.model.NewBoolVar(str(assign))

    def define_constraints(self):
        # Each student is assigned to exactly one room
        for student_program, student_year, student_semester, student_block, course_code, course_description, course_units, course_type in self.students_variable:
            self.model.Add(
                sum(
                    self.room_assignments.get(
                        (
                            student_program,
                            student_year,
                            student_semester,
                            student_block,
                            course_code,
                            course_description,
                            course_units,
                            course_type,
                            room_name,
                            room_type,
                        ),
                        0
                    )
                    for room_name, room_type in self.rooms_variable
                ) == 1
            )

        # Each teacher is assigned to exactly one student
        for teacher_name, teacher_specialized in self.teachers_variable:
            self.model.Add(
                sum(
                    self.teacher_assignments.get(
                        (
                            student_program,
                            student_year,
                            student_semester,
                            student_block,
                            course_code,
                            course_description,
                            course_units,
                            course_type,
                            teacher_name,
                            teacher_specialized,
                        ),
                        0
                    )
                    for student_program, student_year, student_semester, student_block, course_code, course_description, course_units, course_type in self.students_variable
                ) == 1
            )

    def solve(self):
        # Objective: Maximize the total number of student-teacher-room assignments
        objective = sum(self.room_assignments.values()) + sum(self.teacher_assignments.values())
        self.model.Maximize(objective)

        # Solve the model
        status = self.solver.Solve(self.model)

        if status == cp_model.OPTIMAL:
            print("Optimal solution found.")

            # Print assignments
            print("\nAssignments:")
            for student_program, student_year, student_semester, student_block, course_code, course_description, course_units, course_type, room_name, room_type in self.room_assignments:
                for t_student_program, t_student_year, t_student_semester, t_student_block, t_course_code, t_course_description, t_course_units, t_course_type, teacher_name, teacher_specialized in self.teacher_assignments:
                    if (student_program, student_year, student_semester, student_block, course_code, course_description, course_units, course_type) == (
                            t_student_program, t_student_year, t_student_semester, t_student_block, t_course_code, t_course_description, t_course_units, t_course_type
                        ):
                        if (
                            self.solver.Value(self.room_assignments[(student_program, student_year, student_semester, student_block, course_code, course_description, course_units, course_type, room_name, room_type)]) == 1 and
                            self.solver.Value(self.teacher_assignments[(t_student_program, t_student_year, t_student_semester, t_student_block, t_course_code, t_course_description, t_course_units, t_course_type, teacher_name, teacher_specialized)]) == 1
                        ):
                            print(
                                str(student_program),
                                str(student_year),
                                str(student_semester),
                                str(student_block),
                                str(course_code),
                                str(course_description),
                                str(course_units),
                                str(course_type),
                                str(room_name),
                                str(room_type),
                                str(teacher_name),
                                str(teacher_specialized),
                            )

        else:
            print("No optimal solution found.")

if __name__ == "__main__":
    # Load data from data.py
    from data import rooms, teachers, students
    days = ["Mon", "Tue", "Thu", "Fri", "Sat"]
    time_slots = range(7, 20)

    scheduler = Scheduler(rooms, students, teachers, days, time_slots)
