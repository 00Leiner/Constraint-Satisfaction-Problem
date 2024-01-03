from ortools.sat.python import cp_model
import random
from teacher import fetch_teacher_data
from student import fetch_student_data
from room import fetch_room_data


class Scheduler:
    def __init__(self, rooms, students, teachers):
        #variable
        self.rooms = rooms
        self.students = students
        self.teachers = teachers
        self.days = range(1, 4)
        self.hours = range(7, 12)
        # Initialize the CP-SAT model
        self.model = cp_model.CpModel()
        # Create the solver instance
        self.solver = cp_model.CpSolver()
        # binary variables
        self.X = {} # X[s, c, d, h, r, t]
        #populate
        self.binary_variable()  
        self.unit_constraints()
        self.no_double_booking_rooms_availability()
        self.one_day_rest_constraints()
        self.teacher_o_student_assignment()

    def binary_variable(self):
        for s in self.students:
            program = s['program']
            year = s['year']
            semester = s['semester']
            block = s['block']
            for c in s['courses']:
                courseCode = c['code']
                courseDescription = c['description']
                courseUnits = c['units']
                courseType = c['type']
                for d in self.days:
                    for h in self.hours:
                        for r in self.rooms:
                            room = r['name']
                            for t in self.teachers:
                                instructor = t['name']
                                self.X[program, year, block, semester, courseCode, courseDescription, courseUnits, d, h, room, instructor] = \
                                    self.model.NewBoolVar(f'X_{program}_{year}_{block}_{semester}_{courseCode}_{courseDescription}_{courseUnits}_{d}_{h}_{room}_{instructor}')
                             
    def unit_constraints(self):
        for s in self.students:
            program = s['program']
            year = s['year']
            semester = s['semester']
            block = s['block']
            
            for c in s['courses']:
                courseCode = c['code']
                courseDescription = c['description']
                courseUnits = c['units']
                
                if c['type'] == 'laboratory':
                    
                    # Consecutive time slots for laboratory courses with 3 units
                    for d in self.days:
                        for h in range(len(self.hours)):  # Ensure 3 consecutive hours
                            self.model.Add(sum(self.X[program, year, block, semester, courseCode, courseDescription, courseUnits, d, self.hours[h + i], r['name'], t['name']] 
                                            for i in range(3) 
                                            for r in self.rooms 
                                            if r['type'] == 'laboratory'
                                            for t in self.teachers))
                    
                    # Consecutive time slots for laboratory courses with 3 units
                    for d in self.days:
                        for h in range(len(self.hours) - 1):  # Ensure 3 consecutive hours
                            self.model.Add(sum(self.X[program, year, block, semester, courseCode, courseDescription, courseUnits, d, self.hours[h + i], r['name'], t['name']] 
                                            for i in range(2) 
                                            for r in self.rooms 
                                            if r['type'] == 'lecture'
                                            for t in self.teachers))
                else:
                    # Consecutive time slots for laboratory courses with 3 units
                    for d in self.days:
                        for h in range(len(self.hours)):  # Ensure 3 consecutive hours
                            self.model.Add(sum(self.X[program, year, block, semester, courseCode, courseDescription, courseUnits, d, self.hours[h + i], r['name'], t['name']] 
                                            for i in range(3) 
                                            for r in self.rooms 
                                            if r['type'] == 'lecture'
                                            for t in self.teachers))
                            
    
    def no_double_booking_rooms_availability(self):
        for d in self.days:
            for h in self.hours:
                for r in self.rooms:
                    room_constraints = [self.X[s['program'], s['year'], s['block'], s['semester'], c['code'], c['description'], c['units'], d, h, r['name'], t['name']] 
                                        for s in self.students 
                                        for c in s['courses'] 
                                        for t in self.teachers 
                                        ]
                    self.model.Add(sum(room_constraints) <= 1)
        

    def one_day_rest_constraints(self):
        # 1 day rest of learning schedule
        for s in self.students:
            rest_day = random.choice(self.days)
            self.model.Add(sum(self.X[s['program'], s['year'], s['block'], s['semester'], c['code'], c['description'], c['units'], rest_day, h, r['name'], t['name']] 
                               for c in s['courses']
                               for h in self.hours
                               for r in self.rooms
                               for t in self.teachers) == 0)
            
        # 1 day rest of teaching schedule
        for t in self.teachers:
            rest_day = random.choice(self.days)
            self.model.Add(sum(self.X[s['program'], s['year'], s['block'], s['semester'], c['code'], c['description'], c['units'], rest_day, h, r['name'], t['name']] 
                               for s in self.students
                               for c in s['courses']
                               for h in self.hours
                               for r in self.rooms) == 0)   

    def teacher_o_student_assignment(self):
         for s in self.students:
            program = s['program']
            year = s['year']
            semester = s['semester']
            block = s['block']
            for c in s['courses']:
                courseCode = c['code']
                courseDescription = c['description']
                courseUnits = c['units']
                courseType = c['type']
                for d in self.days:
                    for h in self.hours:
                        for r in self.rooms:
                            room = r['name']
                            room_constraints = [self.X[program, year, block, semester, courseCode, courseDescription, courseUnits, d, h, room, t['name']] 
                                        for t in self.teachers
                                        for specialized in t['specialized']
                                        if courseCode == specialized['code'] and courseDescription == specialized['description']
                                        ]
                            self.model.Add(sum(room_constraints) <= 1)
     

if __name__ == "__main__":

    rooms = fetch_room_data()
    students = fetch_student_data()
    teachers = fetch_teacher_data()
    scheduler = Scheduler(rooms, students, teachers)
