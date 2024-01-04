from data.room import fetch_room_data

def define_room_availability(model):
    rooms = fetch_room_data()
    time_slot = [(7, 8), (8, 9), (9, 10), (10, 11), (11, 12), (12, 13)]

    room_availability = {}
    # Create a binary decision variable for each room-course pair
    for room in rooms:
        room_id = room['_id']

        for day in range(1, 3): #2 days
            
            for time in list(time_slot):

                room_availability[(room_id, day, time)] = model.NewBoolVar(f'room:{room_id}_day:{day}_time{time}')
                
    return room_availability
