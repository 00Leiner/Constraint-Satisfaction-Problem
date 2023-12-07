from ortools.sat.python import cp_model
from collections import namedtuple

# Constants
DAYS = 1
HOURS_PER_DAY = 12
HOUR_START = 7

TimeSlot = namedtuple('TimeSlot', ['day', 'hour'])

class Scheduler:
    def __init__(self, rooms, students, teachers):
        # Constants for time slots and days.
        self.time_slots = [TimeSlot(day, hour) for day in range(DAYS) for hour in range(HOURS_PER_DAY)]
        # variables
        self.rooms = rooms
        self.students = students
        self.teachers = teachers
        # CP-SAT
        self.model = cp_model.CpModel()
        self.solver = cp_model.CpSolver()
        # Dictionaries to store values
        self.room_availability = {} 
        self.student_and_room_assignment = {}
        self.teacher_and_room_assignment = {}
        self.teacher_and_student_assignment = {}
        # Populate variables based on data
        self.define_room_availability()
        self.define_student_and_room_assignment()
        self.define_teacher_and_room_assignment()
        self.define_teacher_and_student_assignment()

        self.add_constraints()

        self.solve()

    def define_room_availability(self):
        for room in self.rooms:
            for time_slot in self.time_slots:
                var = (room['name'], room['type'], time_slot.day, time_slot.hour)
                self.room_availability[var] = self.model.NewBoolVar(str(var))

    def define_student_and_room_assignment(self):
        for student in self.students:
            for course in student['courses']:
                for unit in range(1, int(course['units']) + 1):
                    for room_availability in self.room_availability:
                        if course['type'] == room_availability[1]:
                            var = (student['program'], student['year'], student['semester'],
                                   student['block'], course['code'], unit, room_availability[0], 
                                   room_availability[2] + 1, room_availability[3] + HOUR_START, 
                                   room_availability[3] + HOUR_START + 1)
                            self.student_and_room_assignment[var] = self.model.NewBoolVar(str(var))

    def define_teacher_and_room_assignment(self):
        for teacher in self.teachers:
            specialized_list = teacher.get('specialized', [])
            if isinstance(specialized_list, dict):
                specialized_list = [specialized_list]
            for specialized in specialized_list:
                for unit in range(1, int(specialized['units']) + 1):    
                    for room_availability in self.room_availability:
                        if specialized['type'] == room_availability[1]:
                            var = (teacher['name'], specialized['code'], unit, room_availability[0], 
                                    room_availability[2] + 1, room_availability[3] + HOUR_START, 
                                    room_availability[3] + HOUR_START + 1)
                            self.teacher_and_room_assignment[var] = self.model.NewBoolVar(str(var))
                            
    def define_teacher_and_student_assignment(self):
        for student in self.students:
            for course in student['courses']:
                for teacher in self.teachers:
                    specialized_list = teacher.get('specialized', [])
                    if isinstance(specialized_list, dict):
                        specialized_list = [specialized_list]
                    for specialized in specialized_list:
                        if course['code'] == specialized['code']:
                            var = (student['program'], student['year'], student['semester'],
                                   student['block'], course['code'], teacher['name'])
                            self.teacher_and_student_assignment[var] = self.model.NewBoolVar(str(var))

    def add_constraints(self):
        # Ensure that each room is not assigned to multiple classes at the same time
        for room in self.rooms:
            for time_slot in self.time_slots:
                overlapping_assignments = [
                    self.student_and_room_assignment[(
                        student['program'], student['year'], student['semester'],
                        student['block'], course['code'], unit, room['name'],
                        time_slot.day, time_slot.hour, time_slot.hour + 1)
                    ] for student in self.students for course in student['courses'] for unit in range(1, int(course['units']) + 1) if course['type'] == room['type']
                ] + [
                    self.teacher_and_room_assignment[(
                        teacher['name'], specialized['code'], unit, room['name'],
                        time_slot.day, time_slot.hour, time_slot.hour + 1)
                    ] for teacher in self.teachers for specialized_list in [teacher.get('specialized', [])] if isinstance(specialized_list, list) for specialized in specialized_list for unit in range(1, int(specialized['units']) + 1) if specialized['type'] == room['type']
                ]
                self.model.Add(sum(overlapping_assignments) <= 1)

        # Ensure that each student is not assigned to multiple classes at the same time
        for student in self.students:
            for time_slot in self.time_slots:
                overlapping_assignments = [
                    self.student_and_room_assignment[(
                        student['program'], student['year'], student['semester'],
                        student['block'], course['code'], unit, room['name'],
                        time_slot.day, time_slot.hour, time_slot.hour + 1)
                    ] for course in student['courses'] for unit in range(1, int(course['units']) + 1) for room in self.rooms if course['type'] == room['type']
                ] + [
                    self.teacher_and_student_assignment[(
                        student['program'], student['year'], student['semester'],
                        student['block'], course['code'], teacher['name'])
                    ] for course in student['courses'] for teacher in self.teachers for specialized_list in [teacher.get('specialized', [])] if isinstance(specialized_list, list) for specialized in specialized_list if course['code'] == specialized['code']
                ]
                self.model.Add(sum(overlapping_assignments) <= 1)

        # Ensure that each teacher is not assigned to multiple classes at the same time
        for teacher in self.teachers:
            for time_slot in self.time_slots:
                overlapping_assignments = [
                    self.teacher_and_room_assignment[(
                        teacher['name'], specialized['code'], unit, room['name'],
                        time_slot.day, time_slot.hour, time_slot.hour + 1)
                    ] for specialized_list in [teacher.get('specialized', [])] if isinstance(specialized_list, list) for specialized in specialized_list for unit in range(1, int(specialized['units']) + 1) for room in self.rooms if specialized['type'] == room['type']
                ] + [
                    self.teacher_and_student_assignment[(
                        student['program'], student['year'], student['semester'],
                        student['block'], course['code'], teacher['name'])
                    ] for student in self.students for course in student['courses'] for specialized_list in [teacher.get('specialized', [])] if isinstance(specialized_list, list) for specialized in specialized_list if course['code'] == specialized['code']
                ]
                self.model.Add(sum(overlapping_assignments) <= 1)
    
    def solve(self):
        # Solve the model
        status = self.solver.Solve(self.model)
        print("Status: ", status)

        if status == cp_model.OPTIMAL:
            # Print assignments
            print("\nAssignments:")
            for student in self.student_and_room_assignment:
                for room in self.teacher_and_room_assignment:
                        for teacher in self.teacher_and_student_assignment:
                            if teacher[:4] == student[:4]:
                                if student[4] == room[1] == teacher[4]:
                                    if student[:-5] == room[:-5]:
                                        if (
                                            self.solver.Value(self.student_and_room_assignment[student]) == 1 and
                                            self.solver.Value(self.teacher_and_room_assignment[room]) == 1 and
                                            self.solver.Value(self.teacher_and_student_assignment[teacher]) == 1
                                        ):
                                            program = student[0]
                                            year = student[1]
                                            semester = student[2]
                                            block = student[3]
                                            course_code = student[4]
                                            course_unit = student[5]
                                            day = student[7]
                                            time_in = student[8]
                                            time_out = student[9]
                                            room_name = student[6]
                                            teacher_name = teacher[-1]

                                            print(
                                                str(program),
                                                str(year),
                                                str(semester),
                                                str(block),
                                                str(course_code),
                                                str(course_unit),
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
