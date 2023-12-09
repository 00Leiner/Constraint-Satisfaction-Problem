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

        self.room_availability = {}  # room availability
        self.student_time_slots = {}  # student schedule constraints

        self.define_room_availability()
        self.define_student_time_slots()

        self.print_schedule()

    def define_room_availability(self):
        for room in self.rooms:
            for day in range(DAYS):
                for hour in range(HOURS_PER_DAY):
                    var = (room['name'], day, hour)
                    self.room_availability[var] = self.model.NewBoolVar(str(var))
        
        # Ensure no overlap for room availability
        for room in self.rooms:
            self.model.Add(
                sum(self.room_availability[(
                    room['name'], day, hour
                )] for day in range(DAYS) for hour in range(HOURS_PER_DAY)) == 1)

    def define_student_time_slots(self):
        continues_learning = 3
        break_after_continuous_learning = 1  # You can adjust this based on your break duration

        for student in self.students:
            self.student_time_slots[student['program']] = [
                self.model.NewBoolVar(f"Student_{student['program']}_Room{room[-2]}_Hour{room[-1]}")
                for room in self.room_availability
            ]

            for i, room in enumerate(self.room_availability):
                if i % (continues_learning + break_after_continuous_learning) < continues_learning:
                    self.model.Add(self.student_time_slots[student['program']][i] == 1)
                else:
                    self.model.Add(self.student_time_slots[student['program']][i] == 0)

    def print_schedule(self):
        status = self.solver.Solve(self.model)

        if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
            for student_program, time_slots in self.student_time_slots.items():
                for i, room in enumerate(self.room_availability.items()):
                    if self.solver.Value(time_slots[i]):
                        print(
                            f"Student Program: {student_program}, "
                            f"Room: {room[-2]}, Hour: {room[-1]}"
                        )
        else:
            print('No solution found.')

if __name__ == "__main__":
    # Load data from data.py
    from data import rooms, teachers, students

    scheduler = Scheduler(rooms, students, teachers)
