teachers = [
    {
        'id': "1",
        'name': "Dr. Smith",
        'specialized': [{
                'code': "CS 2101",
                'description': "Introduction to Computer Science",
                'units': "3",
                'type': "lec",
            },]
    },
    {
        'id': "2",
        'name': "Prof. Johnson",
        'specialized': [{
                'code': "CS 2102",
                'description': "Programming Fundamentals",
                'units': "3",
                'type': "lab",
            }]
    },
    {
        'id': "3",
        'name': "Dr. Williams",
        'specialized': [{
                'code': "IT 3205",
                'description': "Web Development",
                'units': "3",
                'type': "lec",
            },]
    },
    {
        'id': "4",
        'name': "Prof. Davis",
        'specialized': [{
                'code': "IT 3206",
                'description': "Database Management",
                'units': "3",
                'type': "lab",
            },]
    }
]

students = [
    {
        'id': "1",
        'program': "BSCS",
        'year': "2",
        'semester': "1",
        'block': "D",
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
    },
    {
        'id': "2",
        'program': "BSIT",
        'year': "4",
        'semester': "1",
        'block': "D",
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
            },
            {
                'code': "CS 2102",
                'description': "Programming Fundamentals",
                'units': "3",
                'type': "lab",
            }
        ]
    }
]

rooms = [
    {
        'id': "1",
        'name': "Classroom 1",
        'type': "lab",
    },
    {
        'id': "2",
        'name': "Classroom A",
        'type': "lec",
    }
]
