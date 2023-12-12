from ortools.sat.python import cp_model
import random

class Scheduler:
    def __init__(self, rooms, students, teachers):
        self.rooms = rooms
        self.students = students
        self.teachers = teachers
        self.days = range(0, 6)
        self.hours = range(7, 20)

        # Initialize the CP-SAT model
        self.model = cp_model.CpModel()
        # Create the solver instance
        self.solver = cp_model.CpSolver()

        # binary variables
        self.X = {} # X[p, c, d, h, r]
        self.Y = {} # Y[t, c, d, h, r]
        
        #populate
        self.binary_variable()
        self.program_schedule()
        self.teacher_schedule()
        self.program_rest_day()
        self.teacher_rest_day()
        self.maximum_continuous_learning()
        self.maximum_continuous_teaching()
        self.rest_hour_constraint()

    def binary_variable(self):
        for p in self.students:
            for c in p['courses']:
                for d in self.days:
                    for h in self.hours:
                        for r in self.rooms:
                            if r['type'] == c['type']:
                                self.X[p['program'], c['code'], d, h, r['name']] = \
                                    self.model.NewBoolVar(f'X_{p["program"]}_{c["code"]}_{d}_{h}_{r["name"]}')
                            
        for t in self.teachers:
            for s in t['specialized']:
                for d in self.days:
                    for h in self.hours:
                        for r in self.rooms:
                            if r['type'] == s['type']:
                                self.Y[t['name'], s['code'], d, h, r['name']] = \
                                    self.model.NewBoolVar(f'Y_{t["name"]}_{s["code"]}_{d}_{h}_{r["name"]}')
                            
    def program_schedule(self):
        for p in self.students:
            for c in p['courses']:
                
                units = int(c['units'])
                
                self.model.Add(sum(self.X[
                    p['program'], c['code'], d, h, r['name']
                    ] for d in self.days for h in self.hours for r in self.rooms if r['type'] == c['type']) == units)

    def teacher_schedule(self):
        for t in self.teachers:
            for s in t['specialized']:
                units = int(s['units'])
                
                self.model.Add(sum(self.Y[
                    t['name'], s['code'], d, h, r['name']
                    ] for d in self.days for h in self.hours for r in self.rooms if r['type'] == s['type']) == units)
                
    def program_rest_day(self):
        for p in self.students:
            # Choose a specific day as the rest day (adjust as needed)
            rest_day = random.choice(self.days)
            self.model.Add(sum(self.X[p['program'], c['code'], rest_day, h, r['name']]
                            for c in p['courses']
                            for h in self.hours
                            for r in self.rooms
                            if r['type'] == c['type']) == 0)

    def teacher_rest_day(self):
        for t in self.teachers:
            # Choose a specific day as the rest day (adjust as needed)
            rest_day = random.choice(self.days)
            self.model.Add(sum(self.Y[t['name'], s['code'], rest_day, h, r['name']]
                            for s in t['specialized']
                            for h in self.hours
                            for r in self.rooms
                            if r['type'] == s['type']) == 0)

    def maximum_continuous_learning(self):
        for student in self.students:
            for course in student['courses']:
                program_key = student['program']
                course_key = course['code']
                
                for day in self.days:
                    for room in self.rooms:
                        if room['type'] == course['type']:
                            for start_hour in self.hours:
                                X_vars = [
                                    self.X[program_key, course_key, day, hour, room['name']]
                                    for hour in range(start_hour, start_hour + 3)
                                    if hour in self.hours
                                    
                                ]

                            # Add constraint: at most max_continuous_hours continuous hours of learning
                            self.model.Add(sum(X_vars) <= 3)

    def maximum_continuous_teaching(self):
        for teacher in self.teachers:
            for course in teacher['specialized']:
                teacher_key = teacher['name']
                course_key = course['code']
                
                for day in self.days:
                    for room in self.rooms:
                        if room['type'] == course['type']:
                            for start_hour in self.hours:
                                Y_vars = [
                                    self.Y[teacher_key, course_key, day, hour, room['name']]
                                    for hour in range(start_hour, start_hour + 3)
                                    if hour in self.hours
                                ]

                                # Add constraint: at most max_continuous_hours continuous hours of teaching
                                self.model.Add(sum(Y_vars) <= 3)

    def rest_hour_constraint(self):
        for student in self.students:
            for course in student['courses']:
                program_key = student['program']
                course_key = course['code']

                for day in self.days:
                    for room in self.rooms:
                        if room['type'] == course['type']:
                            for start_hour in self.hours[:-1]:  # Exclude the last hour since there's no next hour
                                X_var_current = self.X[program_key, course_key, day, start_hour, room['name']]
                                X_var_next = self.X[program_key, course_key, day, start_hour + 1, room['name']]

                                # Add constraint: at least one hour of rest between two scheduled hours
                                self.model.Add(X_var_current + X_var_next <= 1)

        for teacher in self.teachers:
            for course in teacher['specialized']:
                teacher_key = teacher['name']
                course_key = course['code']

                for day in self.days:
                    for room in self.rooms:
                        if room['type'] == course['type']:
                            for start_hour in self.hours[:-1]:  # Exclude the last hour since there's no next hour
                                Y_var_current = self.Y[teacher_key, course_key, day, start_hour, room['name']]
                                Y_var_next = self.Y[teacher_key, course_key, day, start_hour + 1, room['name']]

                                # Add constraint: at least one hour of rest between two scheduled hours
                                self.model.Add(Y_var_current + Y_var_next <= 1)

class SolutionPrinter(cp_model.CpSolverSolutionCallback):
    def __init__(self, scheduler, limit):
        cp_model.CpSolverSolutionCallback.__init__(self)
        self.scheduler = scheduler
        self.solution_count = 0
        self.limit = limit
        self.seen_solutions = set()

    def on_solution_callback(self):
        # Convert the solution to a tuple for hashability
        current_solution = tuple(sorted((key, self.Value(value)) for key, value in self.scheduler.X.items()))

        # Check if the solution is unique
        if current_solution not in self.seen_solutions:
            print(f'Solution {self.solution_count}:')
            # Print here the schedule that contains program, course, teacher, room, day, hour
            # Modify this part based on how your schedule is represented
            for key, value in self.scheduler.X.items():
                if self.Value(value):
                    print(key)

            self.seen_solutions.add(current_solution)
            self.solution_count += 1

        # Check if the limit is reached and stop the search
        if self.solution_count >= self.limit:
            self.StopSearch()




if __name__ == "__main__":
    # Load data from data.py
    from data import rooms, teachers, students

    scheduler = Scheduler(rooms, students, teachers)

    # Create and set the solution callback with the desired limit
    limit = 10  # Set the desired limit
    solution_printer = SolutionPrinter(scheduler, limit)
    
    # Find solutions
    scheduler.solver.SearchForAllSolutions(scheduler.model, solution_printer)

    # Print the number of solutions found
    print(f'Number of solutions found: {solution_printer.solution_count}')
