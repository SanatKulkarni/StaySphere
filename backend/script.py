class Room:
    def __init__(self, room_number):
        self.room_number = room_number
        self.occupied = False
        self.student = None

class Floor:
    def __init__(self, floor_number, num_rooms):
        self.floor_number = floor_number
        self.rooms = [Room(f"{floor_number}-{i+1}") for i in range(num_rooms)]

class HostelBuilding:
    def __init__(self, building_name, num_floors, rooms_per_floor):
        self.building_name = building_name
        self.floors = [Floor(i+1, rooms_per_floor) for i in range(num_floors)]

class Student:
    def __init__(self, name, institute, room=None):
        self.name = name
        self.institute = institute
        self.room = room

class HostelManager:
    def __init__(self):
        self.buildings = []
        self.students = []

    def add_building(self, building):
        self.buildings.append(building)

    def allocate_room(self, student):
        for building in self.buildings:
            for floor in building.floors:
                for room in floor.rooms:
                    if not room.occupied:
                        room.occupied = True
                        student.room = room
                        self.students.append(student)
                        return

    def reallocate_room(self, student, new_room):
        if student.room:
            student.room.occupied = False
            student.room = new_room
            new_room.occupied = True

    def get_empty_rooms(self):
        empty_rooms = 0
        for building in self.buildings:
            for floor in building.floors:
                empty_rooms += sum(1 for room in floor.rooms if not room.occupied)
        return empty_rooms

    def get_students_by_institute(self, institute):
        return [student for student in self.students if student.institute == institute]

    def generate_report(self, report_type):
        if report_type == "student":
            for student in self.students:
                print(f"Name: {student.name}, Institute: {student.institute}, Room: {student.room.room_number if student.room else 'Not allocated'}")
        elif report_type == "building":
            for building in self.buildings:
                print(f"Building: {building.building_name}")
                for floor in building.floors:
                    print(f"  Floor: {floor.floor_number}")
                    for room in floor.rooms:
                        print(f"    Room: {room.room_number}, Occupied: {'Yes' if room.occupied else 'No'}")
        elif report_type == "room_occupancy":
            total_rooms = sum(len(building.floors) * len(building.floors[0].rooms) for building in self.buildings)
            occupied_rooms = total_rooms - self.get_empty_rooms()
            print(f"Total Rooms: {total_rooms}, Occupied Rooms: {occupied_rooms}, Empty Rooms: {self.get_empty_rooms()}")

# Example usage
manager = HostelManager()

building1 = HostelBuilding("Building A", 3, 10)
building2 = HostelBuilding("Building B", 2, 8)

manager.add_building(building1)
manager.add_building(building2)

student1 = Student("John", "Institute A")
student2 = Student("Alice", "Institute B")
student3 = Student("Bob", "Institute A")

manager.allocate_room(student1)
manager.allocate_room(student2)
manager.allocate_room(student3)

manager.generate_report("student")
manager.generate_report("building")
manager.generate_report("room_occupancy")

print("Students from Institute A:")
for student in manager.get_students_by_institute("Institute A"):
    print(student.name)