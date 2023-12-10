from ortools.sat.python import cp_model

# Constants
DAYS = 7
HOURS_PER_DAY = 1
HOUR_START = 7


class Scheduler:
    def __init__(self, rooms, students, teachers):
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
        self.define_student_constraints()
        
        #self.print_schedule()
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

    def define_student_constraints(self):
        for student in self.students:
            program = student['program']
            for room_available in self.room_availability:
                var = (program, room_available[0], room_available[1], room_available[2])
                self.student_time_slots[var] = self.model.NewBoolVar(str(var))

        for room_available in self.room_availability:
            overlapping_students = [
                self.student_time_slots[(student['program'], room_available[0], room_available[1], room_available[2])]
                for student in self.students
            ]
            self.model.Add(sum(overlapping_students) == 1)

        
        
    def print_schedule(self):
        status = self.solver.Solve(self.model)

        if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
            for student_program, time_slots in self.student_time_slots.items():
                for i, var in enumerate(time_slots):
                    if self.solver.Value(var):
                        day, hour = divmod(i, HOURS_PER_DAY)
                        room_index = i % len(self.rooms)
                        room_name = self.rooms[room_index]['name']
                        print(
                            f"Student Program: {student_program}, "
                            f"Room: {room_name}, "
                            f"Day: {day}, Hour: {hour + HOUR_START}"
                        )
        else:
            print('No solution found.')

if __name__ == "__main__":
    # Load data from data.py
    from data import rooms, teachers, students

    scheduler = Scheduler(rooms, students, teachers)