from ortools.sat.python import cp_model
from collections import namedtuple

# Constants
DAYS = 5
HOURS_PER_DAY = 12
HOUR_START = 7

TimeSlot = namedtuple('TimeSlot', ['day', 'hour'])

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
                        unit, student[7], time_slot.day, time_slot.hour
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
                            unit, student[7], time_slot.day, time_slot.hour
                        ), 0)for time_slot in self.time_slots) == 1)

        # Ensure that each time slot is occupied by at most one course unit.
        for time_slot in self.time_slots:
            self.model.Add(
                sum(self.student_and_time_slots_assignments.get(
                    (
                        student[0], student[1], student[2], 
                        student[3], student[4], student[5], 
                        unit, student[7], time_slot.day, time_slot.hour
                        ), 0)
                    for student in self.students_variable for unit in range(1, int(student[6]) + 1)) <= 1)

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

        # Each student is assigned to exactly one room
        for room in self.rooms_variable:
            self.model.Add(
                sum(self.room_and_student_assignments.get(
                    student + (room[0], room[1]), 0) for student in self.students_variable) <= 1
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

        # Each student is assigned to exactly one teacher
        for student in self.students_variable:
            self.model.Add(
                sum(self.teacher_and_student_assignments.get(
                        (student + (teacher[0], teacher[1])), 0)for teacher in self.teachers_variable) <= 1
            )

    def declare_room_and_time_slots_assignments(self):
        # Room and time slot assignment
        for room in self.rooms_variable:
            for time_slot in self.time_slots:
                var = (room + (time_slot.day, time_slot.hour))
                self.room_and_time_slots_assignments[var] = self.model.NewBoolVar(str(var))

        # Ensure room has time slot and no overlopping
        for room in self.rooms_variable: 
            self.model.Add(
                sum(self.room_and_time_slots_assignments.get(
                        ( room + (time_slot.day, time_slot.hour)), 0)for time_slot in self.time_slots) == 1
            )
        # Ensure room schedule once
        for time_slot in self.time_slots: 
            self.model.Add(
                sum(self.room_and_time_slots_assignments.get(
                        ( room + (time_slot.day, time_slot.hour)), 0)for room in self.rooms_variable) <= 1
            )

    def solve(self):
        # Objective: Minimize the total number of assigned variables (to improve schedule efficiency)
        self.model.Minimize(
            sum(
                self.student_and_time_slots_assignments[student_time_slot]
                for student_time_slot in self.student_and_time_slots_assignments
            )
        )

        # Solve the model
        self.solver.Solve(self.model)

        # Print the schedule
        print("Schedule:")
        for student_time_slot, variable in self.student_and_time_slots_assignments.items():
            if self.solver.Value(variable) == 1:
                student_info = (
                    student_time_slot[0],
                    student_time_slot[1],
                    student_time_slot[2],
                    student_time_slot[3],
                    student_time_slot[4],
                    student_time_slot[5],
                    student_time_slot[6],
                    student_time_slot[7],
                )
                time_slot_info = (
                    student_time_slot[8],
                    student_time_slot[9],
                )

                # Fetch room and teacher info from existing dictionaries
                room_info = None
                for room_student_key, room_var in self.room_and_student_assignments.items():
                    if self.solver.Value(room_var) == 1 and room_student_key[:-2] == student_info:
                        room_info = (room_student_key[-2], room_student_key[-1])
                        break

                teacher_info = None
                for teacher_student_key, teacher_var in self.teacher_and_student_assignments.items():
                    if self.solver.Value(teacher_var) == 1 and teacher_student_key[:-2] == student_info:
                        teacher_info = (teacher_student_key[-2], teacher_student_key[-1])
                        break

                print(
                    f"Program: {student_info[0]}, Year: {student_info[1]}, Semester: {student_info[2]}, "
                    f"Block: {student_info[3]}, Course Code: {student_info[4]}, "
                    f"Course Description: {student_info[5]}, Course Units: {student_info[6]}, "
                    f"Course Type: {student_info[7]}, "
                    f"Day {time_slot_info[0] + 1}, "
                    f"Hour {time_slot_info[1] + HOUR_START}:00 - {time_slot_info[1] + HOUR_START + 1}:00, "
                    f"Room: {room_info[0]}, Room Type: {room_info[1]}, "
                    f"Teacher: {teacher_info[0]}, Specialized: {teacher_info[1]}"
                )

if __name__ == "__main__":
    # Load data from data.py
    from data import rooms, teachers, students

    scheduler = Scheduler(rooms, students, teachers)