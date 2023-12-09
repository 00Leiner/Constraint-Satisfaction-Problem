from ortools.sat.python import cp_model
from collections import namedtuple

# Constants
DAYS = 5
HOURS_PER_DAY = 12
HOUR_START = 7

TimeSlot = namedtuple('TimeSlot', ['day', 'hour'])

class ScheduleSolutionPrinter(cp_model.CpSolverSolutionCallback):
    def __init__(self, solver, students_variable, room_and_student_assignments, teacher_and_student_assignments, room_and_time_slots_assignments):
        cp_model.CpSolverSolutionCallback.__init__(self)
        self.solver = solver
        self.students_variable = students_variable
        self.room_and_student_assignments = room_and_student_assignments
        self.teacher_and_student_assignments = teacher_and_student_assignments
        self.room_and_time_slots_assignments = room_and_time_slots_assignments
        self.solutions = []

    def on_solution_callback(self):
        current_solution = []
        for student in self.students_variable:
            for room in self.room_and_student_assignments:
                for teacher in self.teacher_and_student_assignments:
                    if room[:6] == teacher[:6] == student[:6]:
                        if (
                            self.solver.Value(self.room_and_student_assignments[room]) == 1 and
                            self.solver.Value(self.teacher_and_student_assignments[teacher]) == 1
                        ):
                            current_solution.append({
                                'program': student[0],
                                'year': student[1],
                                'semester': student[2],
                                'block': student[3],
                                'course_code': student[4],
                                'course_description': student[5],
                                'course_unit': student[6],
                                'course_type': student[7],
                                'day': student[8],
                                'time_in': student[9],
                                'time_out': student[10],
                                'room_name': room[-2],
                                'teacher_name': teacher[-2],
                            })
        self.solutions.append(current_solution)

    def get_solutions(self):
        return self.solutions

class Scheduler:
    def __init__(self, rooms, students, teachers):
        #variable
        self.rooms = rooms
        self.students = students
        self.teachers = teachers

        # Constants for time slots and days.
        self.time_slots = [TimeSlot(day, hour) for day in range(DAYS) for hour in range(HOURS_PER_DAY)]

        self.model = cp_model.CpModel()
        self.solver = cp_model.CpSolver()

        # set up variables
        self.rooms_variable = self.define_rooms_variable()
        self.teachers_variable = self.define_teachers_variable()
        self.students_variable = self.define_students_variable()

        # Dictionary to store values
        self.student_and_time_slots_assignments = {}
        self.room_and_student_assignments = {}  
        self.teacher_and_student_assignments = {}  
        self.room_and_time_slots_assignments = {}


        # Populate variables based on data
        self.declare_student_and_time_slots_assignments()
        self.declare_room_and_student_assignments()
        self.declare_teacher_and_student_assignments()
        self.declare_room_and_time_slots_assignments()

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
                assign = (student['program'], student['year'], 
                          student['semester'], student['block'],
                          course['code'], course['description'], 
                          course['units'], course['type'])
                students_variable[assign] = self.model.NewBoolVar(str(assign))
        return students_variable

    def declare_student_and_time_slots_assignments(self):
        #Student and time slot assignment
        for student in self.students_variable:
            for unit in range(1, int(student[6]) + 1):
                for time_slot in self.time_slots:
                    var =(
                        student[0], student[1], student[2],
                        student[3], student[4], student[5], 
                        unit, student[7], time_slot.day + 1, 
                        time_slot.hour + HOUR_START, time_slot.hour + HOUR_START + 1
                        )
                    self.student_and_time_slots_assignments[
                        var] = self.model.NewBoolVar(str(var))
                    
        # Ensure student course unit is scheduled exactly once
        for student in self.students_variable:
            for unit in range(1, int(student[6]) + 1):
                self.model.Add(
                    sum(self.student_and_time_slots_assignments.get(
                        (
                            student[0], student[1], student[2],
                            student[3], student[4], student[5], 
                            unit, student[7], time_slot.day + 1, 
                            time_slot.hour + HOUR_START, time_slot.hour + HOUR_START + 1
                        ), 0)for time_slot in self.time_slots) == 1)

    def declare_room_and_student_assignments(self):
        # Room and student assignment
        for room in self.rooms_variable:
            for student in self.students_variable:
                if room[1] == student[7]:
                    var = (student + (room[0], room[1]))
                    self.room_and_student_assignments[var] = self.model.NewBoolVar(str(var))

        # Each student is assigned to exactly one room
        for student in self.students_variable:
            self.model.Add(
                sum(self.room_and_student_assignments.get(
                    student + (room[0], room[1]), 0) for room in self.rooms_variable) == 1
            )

    def declare_teacher_and_student_assignments(self):
        # Teacher and Student assignment
        for teacher in self.teachers_variable:
            for student in self.students_variable:
                if teacher[1] == student[4]:  
                    self.teacher_and_student_assignments[(
                        student + (teacher[0], teacher[1]))] = self.model.NewBoolVar(str(student))
                    
         # Each teacher is assigned to exactly one student
        for teacher in self.teachers_variable:
            self.model.Add(
                sum(self.teacher_and_student_assignments.get(
                        (student + (teacher[0], teacher[1])), 0)for student in self.students_variable) == 1
            )

    def declare_room_and_time_slots_assignments(self):
        # Room and time slot assignment
        for room in self.rooms_variable:
            for time_slot in self.time_slots:
                var = (room + (time_slot.day, time_slot.hour))
                self.room_and_time_slots_assignments[var] = self.model.NewBoolVar(str(var))

    def solve(self):
        # Solve the model
        status = self.solver.Solve(self.model)
        print("Status: ", status)

        if status == cp_model.OPTIMAL:
            # Print assignments
            print("\nAssignments:")
            for student in self.student_and_time_slots_assignments:
                for room in self.room_and_student_assignments:
                        for teacher in self.teacher_and_student_assignments:
                            if room[:6] == teacher[:6] == student[:6]:
                                if (
                                    self.solver.Value(self.student_and_time_slots_assignments[student]) == 1 and
                                    self.solver.Value(self.room_and_student_assignments[room]) == 1 and
                                    self.solver.Value(self.teacher_and_student_assignments[teacher]) == 1
                                ):
                                    program = student[0]
                                    year = student[1]
                                    semester = student[2]
                                    block = student[3]
                                    course_code = student[4]
                                    course_description = student[5]
                                    course_unit = student[6]
                                    course_type = student[7]
                                    day = student[8]
                                    time_in = student[9]
                                    time_out = student[10]
                                    room_name = room[-2]
                                    teacher_name = teacher[-2]

                                    print(
                                        str(program),
                                        str(year),
                                        str(semester),
                                        str(block),
                                        str(course_code),
                                        str(course_description),
                                        str(course_unit),
                                        str(course_type),
                                        str(day),
                                        str(time_in),
                                        str(time_out),
                                        str(room_name),
                                        str(teacher_name),
                                    )


        
        else:
            print("No optimal solution found.")                             



if __name__ == "__main__":
    # Load data from data.py
    from data import rooms, teachers, students

    scheduler = Scheduler(rooms, students, teachers)