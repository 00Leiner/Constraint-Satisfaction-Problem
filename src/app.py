from ortools.sat.python import cp_model

class Scheduler:
    def __init__(self, rooms, students, teachers, days, time_slots):
        self.rooms = rooms
        self.students = students
        self.teachers = teachers
        self.days = days
        self.time_slots = time_slots

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

        #solve
        self.solve()

    def define_rooms_variable(self):
        return {(room['name'], room['type']): self.model.NewBoolVar(f"{room['name']}, {room['type']}") for room in self.rooms}

    def define_teachers_variable(self):
        return {(teacher['name'], teacher['specialized']): self.model.NewBoolVar(f"{teacher['name']}, {teacher['specialized']}") for teacher in self.teachers}

    def define_students_variable(self):
        students_variable = {}
        for student in self.students:
            for course in student['courses']:
                assign = (student['program'], student['year'], student['semester'], student['block'],
                          course['code'], course['description'], course['units'], course['type'])
                students_variable[assign] = self.model.NewBoolVar(str(assign))
        return students_variable

    def declare_room_assignments(self):
        for room in self.rooms_variable:
            for assign in self.students_variable:
                if room[1] == assign[7]:
                    self.room_assignments[(assign + (room[0], room[1]))] = self.model.NewBoolVar(str(assign))

    def declare_teacher_assignments(self):
        for teacher in self.teachers_variable:
            for assign in self.students_variable:
                if teacher[1] == assign[4]:  
                    self.teacher_assignments[(
                        assign + (teacher[0], teacher[1]))] = self.model.NewBoolVar(str(assign))

    def define_constraints(self):
        # Each student is assigned to exactly one room
        for student in self.students_variable:
            self.model.Add(
                sum(self.room_assignments.get(
                    student + (room[0], room[1]), 0) for room in self.rooms_variable) == 1
            )

        # Each teacher is assigned to exactly one student
        for teacher in self.teachers_variable:
            self.model.Add(
                sum(self.teacher_assignments.get(
                        (student + (teacher[0], teacher[1])), 0)for student in self.students_variable) == 1
            )

    def solve(self):
        # Objective: Maximize the total number of student-teacher-room assignments
        objective = sum(self.room_assignments.values()) + sum(self.teacher_assignments.values())
        self.model.Maximize(objective)

        # Solve the model
        status = self.solver.Solve(self.model)
        print("Status: ", status)

        if status == cp_model.OPTIMAL:

            # Print assignments
            print("\nAssignments:")
            for room in self.room_assignments:
                for teacher in self.teacher_assignments:
                        if room[:8] == teacher[:8]:
                            if (
                                self.solver.Value(self.room_assignments[room]) == 1 and
                                self.solver.Value(self.teacher_assignments[teacher]) == 1
                            ):
                                print(
                                str(room[0]),
                                str(room[1]),
                                str(room[2]),
                                str(room[3]),
                                str(room[4]),
                                str(room[5]),
                                str(room[6]),
                                str(room[7]),
                                str(room[8]),
                                str(room[9]),
                                str(teacher[-2]),
                                str(teacher[-1])
                            )

        else:
            print("No optimal solution found.")

if __name__ == "__main__":
    # Load data from data.py
    from data import rooms, teachers, students
    days = ["Mon", "Tue", "Thu", "Fri", "Sat"]
    time_slots = range(7, 20)

    scheduler = Scheduler(rooms, students, teachers, days, time_slots)