# Given data format
data = [
    {
        'program': "BSIT",
        'courses': [
            {
                'code': "IT 3205",
                'description': "Web Development",
                'units': "3",
                'type': "lec",
            },
            {
                'code': "IT 3206",
                'description': "Database Management",
                'units': "3",
                'type': "lab",
            }
        ]
    },
    {
        
        'program': "BSCS",
        'courses': [
            {
                'code': "CS 2101",
                'description': "Introduction to Computer Science",
                'units': "3",
                'type': "lec",
            },
            {
                'code': "CS 2102",
                'description': "Programming Fundamentals",
                'units': "3",
                'type': "lab",
            }
        ]
    }
    # ... add more programs if needed
]

# Define sets for programs, courses, and units
programs = set()
courses = set()
units = set()

# Extract information from the data
for program_data in data:
    program = program_data['program']
    programs.add(program)
    
    for course_data in program_data['courses']:
        course_code = course_data['code']
        courses.add(course_code)
        
        # Assuming 'units' is a string, convert it to an integer for consistency
        units.add(int(course_data['units']))

# Print the sets
print("Programs:", programs)
print("Courses:", courses)
print("Units:", units)
