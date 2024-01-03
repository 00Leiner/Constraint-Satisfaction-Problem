import requests

class Fetching:
    def __init__(self, url):
        self.url = url
    
    def perform_get_request(self):
        response = requests.get(self.url)

        if response.status_code == 200:
            # Assuming the response content is JSON
            data = response.json()
            return data
        else:
            print(f"Error in GET request. Status code: {response.status_code}")
            print(response.text)
            return None

def format_data(fetched_data):
    formatted_data = []

    for teacher in fetched_data.get('teachers', []):
        teacher_info = {
            'name': teacher.get('name', ''),
            'specialized': []
        }

        for course in teacher.get('specialized', []):
            course_info = {
                'code': course.get('code', ''),
                'description': course.get('description', ''),
                'units': course.get('units', ''),
                'type': course.get('type', '')
            }

            teacher_info['specialized'].append(course_info)

        formatted_data.append(teacher_info)

    return formatted_data

def fetch_teacher_data():
    fetch_url = 'http://localhost:3000/Teachers/get'
    fetching_instance = Fetching(fetch_url)
    fetched_data = fetching_instance.perform_get_request()

    if fetched_data is not None:
        formatted_data = format_data(fetched_data)
        return formatted_data
    else:
        print('Failed to fetch data.')
        return None
    