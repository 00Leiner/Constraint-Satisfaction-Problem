# Import necessary libraries
from ortools.sat.python import cp_model
from utils.student import define_student_variable 
from data.course import fetch_course_data
from utils.teacher import define_teacher_variable
from data.room import fetch_room_data
from assignment.scheduling import define_scheduling

# Function to create the scheduling model
def create_scheduling_model():
    # Initialize the CP model
    model = cp_model.CpModel()
    
    # Define variables 
    students = define_student_variable() #{(student_id, course_id), }
    courses = fetch_course_data() #{ (_id, code, description, units, type) }
    teachers = define_teacher_variable() #{(teacher_id, course_id), }
    rooms = fetch_room_data() #{ (_id, name, type) }
    day = [
        'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'
        ]
    time = [
        (7, 8), (8, 9), (9, 10), (10, 11), (11, 12), (12, 13), (13, 14), (14, 15)
        ]

    scheduling = define_scheduling(model, students, courses, teachers, rooms, day, time) #{(student_id, course_id, teachers_id, room_id, day, time)}

    # Return the model
    return model

# Function to solve the scheduling model
def solve_scheduling_model(model):
    # Initialize the CP solver
    solver = cp_model.CpSolver()
    
    # Solve the model and obtain the solution
    status = solver.Solve(model)
    
    # Process and output the solution
    if status == cp_model.OPTIMAL:
        # Extract and process the solution
        extract_and_process_solution(solver)
    else:
        print("No optimal solution found.")

# Function to extract and process the scheduling solution
def extract_and_process_solution(solver):
    # TODO: Implement logic to extract and process the scheduling solution
    # Example: Extract assignments and output the solution
    print("Scheduling Solution:")
    # TODO: Implement output logic

# Main function to orchestrate the scheduling process
def main():
    print("Creating the scheduling model...")
    
    # Create the scheduling model
    model = create_scheduling_model()
    
    print("Solving the scheduling model...")
    
    # Solve the scheduling model
    solve_scheduling_model(model)
    
    print("Scheduling process completed.")

# Entry point for the script
if __name__ == "__main__":
    #main()
    create_scheduling_model()
