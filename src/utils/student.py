from data.course import fetch_course_data
from data.student import fetch_student_data

def define_student_variable():
    courses = fetch_course_data()
    students = fetch_student_data()

    student_course_assignment = []
    # Create a binary decision variable for each student-course pair
    for student in students:
        student_id = student['_id']

        for student_curr in student['courses']:
            student_curr_code = student_curr['code']
            student_curr_des = student_curr['description']

            for course in courses:
                course_id = course['_id']
                course_code = course['code']
                course_des = course['description']

                
                # Check if the student prefers this course
                if student_curr_code == course_code and student_curr_des == course_des:
                    # Create a binary decision variable
                    student_course_assignment.append((student_id, course_id))
                    
    return student_course_assignment