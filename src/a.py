from ortools.sat.python import cp_model

class Scheduler:
    def __init__(self, rooms, students, teachers):
        # variables
        self.rooms = rooms
        self.students = students
        self.teachers = teachers
        self.hours = range(7, 20)
        self.days = range(0, 6)
        # CP-SAT
        self.model = cp_model.CpModel()
        self.solver = cp_model.CpSolver()
        # Binary variables for program, teacher, room, day, hour, and duration
        self.teacher_vars = {}
        self.room_vars = {}
        self.duration_vars = {} 
        self.day_vars = {}
        self.hour_vars = {}
        # populate
        self.assignments()
        self.constraints_1()
        self.constraints_2()

    def assignments(self):
        for student in self.students:
            program = student['program']
            for course in student['courses']:
                course_code = course['code']
                course_type = course['type']
                course_units = int(course['units'])
                # teachers------------------------------------
                for teacher in self.teachers:
                    if teacher['specialized'] == course_code:
                        teacher_name = teacher['name']
                        self.teacher_vars[program, course_code, teacher_name] = self.model.NewBoolVar(
                            f'{program}_{course_code}_{teacher_name}_scheduled'
                        )
                # rooms-------------------------------------
                for room in self.rooms:
                    if room['type'] == course_type:
                        room_name = room['name']
                        self.room_vars[program, course_code, room_name] = self.model.NewBoolVar(
                            f'{program}_{course_code}_{room_name}_scheduled'
                        )
                # units---------------------------------
                unit_vars = []
                for _ in range(course_units):
                    unit_vars.append(self.model.NewBoolVar(f'{program}_{course_code}_unit_scheduled'))
                self.duration_vars[program, course_code] = unit_vars
                # days-----------------------------------
                for day in self.days:
                    self.day_vars[program, course_code, day] = self.model.NewBoolVar(
                        f'{program}_{course_code}_{day}_scheduled'
                    )
                # hours--------------------------------
                for hour in self.hours: 
                    self.hour_vars[program, course_code, hour] = self.model.NewBoolVar(
                        f'{program}_{course_code}_{hour}_scheduled'
                    )

    def constraints_1(self):
        # Constraint 1: Each program must be scheduled for classes on less than or equal to 5 days a week
        for student in self.students:
            program = student['program']
            for course in student['courses']:
                course_code = course['code']
                # Each program is assigned only in less than or equal to 5 days of classes
                self.model.Add(sum(self.day_vars[
                    program, course_code, day
                    ] for day in self.days) <= 5)
                # All courses of the program must be assigned in less than or equal to 5 days
                self.model.Add(sum(self.day_vars[
                    program, other_course['code'], day
                    ] for other_course in student['courses']
                            for day in self.days) <= 5)
                # Each course is assigned at least once
                self.model.Add(sum(self.day_vars[
                    program, course_code, day
                    ] for day in self.days) >= 1)
        
    def constraints_2(self):   
        # Constraint 2: Program Unit Constraints
        for student in self.students:
            program = student['program']
            for course in student['courses']:
                course_code = course['code']
                course_units = int(course['units']) 
                # Ensure the total hours scheduled for the course per week is equal to the specified units
                self.model.Add(
                    sum(self.hour_vars[program, course_code, hour] for hour in self.hours) >= course_units
                )
                # Ensure at least 1 unit is assigned for the course
                self.model.Add(
                    sum(self.hour_vars[program, course_code, hour] for hour in self.hours) >= 1
                )
                # Ensure the course is scheduled only on the specified days
                for day in self.days:
                    day_var = self.day_vars[program, course_code, day]
                    duration_vars = [self.duration_vars[program, course_code][i] for i in range(course_units)]
                    # Create an OR constraint
                    or_constraint = self.model.NewBoolVar(f'{program}_{course_code}_{day}_or_constraint')
                    self.model.AddBoolOr([day_var] + duration_vars).OnlyEnforceIf(or_constraint)
                    # Connect the OR constraint with the equality constraint
                    self.model.Add(sum(duration_vars) == course_units).OnlyEnforceIf(or_constraint)
 

class SolutionPrinter(cp_model.CpSolverSolutionCallback):
    def __init__(self, scheduler, limit):
        cp_model.CpSolverSolutionCallback.__init__(self)
        self.scheduler = scheduler
        self.solution_count = 0
        self.limit = limit

    def on_solution_callback(self):
        print(f'Solution {self.solution_count}:')
        for _, var in self.scheduler.hour_vars.items():
            if self.Value(var):
                print(f'{var}')

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



