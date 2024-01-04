from data.course import fetch_course_data
from data.teacher import fetch_teacher_data

def define_teacher_course_assignments(model):
    courses = fetch_course_data()
    teachers = fetch_teacher_data()

    teacher_course_assignment = {}
    # Create a binary decision variable for each teacher-course pair
    for teacher in teachers:
        teacher_id = teacher['_id']

        for teacher_spec in teacher['specialized']:
            teacher_spec_code = teacher_spec['code']
            teacher_spec_des = teacher_spec['description']

            for course in courses:
                course_id = course['_id']
                course_code = course['code']
                course_des = course['description']

                
                # Check if the teacher prefers this course
                if teacher_spec_code == course_code and teacher_spec_des == course_des:
                    # Create a binary decision variable
                    teacher_course_assignment[(teacher_id, course_id)] = model.NewBoolVar(f'teacher:{teacher_id}_course:{course_id}')

    return teacher_course_assignment
