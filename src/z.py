from ortools.sat.python import cp_model

class RoomAssignmentModel:
    def __init__(self, num_rooms, num_days, num_hours):
        self.model = cp_model.CpModel()
        self.room_assignment = {}
        self.num_rooms = num_rooms
        self.num_days = num_days
        self.num_hours = num_hours

        for room in range(num_rooms):
            for day in range(num_days):
                for hour in range(num_hours):
                    var = self.model.NewBoolVar(f"Room_{room}_Day_{day + 1}_Hour_{hour + 1}")
                    self.room_assignment[(room, day, hour)] = var

    def ensure_unique_assignment(self):
        for room in range(self.num_rooms):
            for day in range(self.num_days):
                # Ensure that exactly one hour is assigned for each room and day
                self.model.Add(sum(self.room_assignment[(room, day, hour)] for hour in range(self.num_hours)) == 1)

        for day in range(self.num_days):
            for hour in range(self.num_hours):
                # Ensure that exactly one room is assigned for each hour of the day
                self.model.Add(sum(self.room_assignment[(room, day, hour)] for room in range(self.num_rooms)) == 1)

    def solve_model(self):
        solver = cp_model.CpSolver()
        status = solver.Solve(self.model)

        print("Solver status:", solver.StatusName(status))

        if status == cp_model.OPTIMAL:
            print('Solution:')
            for room, day, hour in self.room_assignment:
                var = self.room_assignment[(room, day, hour)]
                print(f'Room {room}, Day {day + 1}, Hour {hour + 1}: {solver.Value(var)}')
        else:
            print('No solution found.')

# Example usage
num_rooms = 3
num_days = 3
num_hours = 1

model_instance = RoomAssignmentModel(num_rooms, num_days, num_hours)
model_instance.ensure_unique_assignment()
model_instance.solve_model()
