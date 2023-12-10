from ortools.sat.python import cp_model

# Constants
DAYS = 7
HOURS_PER_DAY = 1
HOUR_START = 7


class Scheduler:
    def __init__(self, rooms, students, teachers):
        # variables
        self.rooms = range(len(rooms))
        self.students = range(len(students))
        self.teachers = range(len(teachers))
        # CP-SAT
        self.model = cp_model.CpModel()
        self.solver = cp_model.CpSolver()

        self.room_availability = {}  # room availability
        self.student_time_slots = {}  # student schedule constraints

        self.define_room_availability()
        self.define_student_constraints()
        
        #self.print_schedule()

    def define_room_availability(self):
        for room in range(len(self.rooms)):
            for day in range(DAYS):
                for hour in range(HOURS_PER_DAY):
                    var = (room, day, hour)
                    self.room_availability[var] = self.model.NewBoolVar(str(var))

    def define_student_constraints(self):
        for student in self.students:
            program = student['program']
            for room_available in self.room_availability:
                var = (program, room_available[0], room_available[1], room_available[2])
                self.student_time_slots[var] = self.model.NewBoolVar(str(var))

        x = range(len(self.students))

        print(str(x))

    def print_schedule(self):
        status = self.solver.Solve(self.model)

        if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
            for student in self.student_time_slots.items():
                print(student)
        else:
            print('No solution found.')

if __name__ == "__main__":
    # Load data from data.py
    from data import rooms, teachers, students

    scheduler = Scheduler(rooms, students, teachers)