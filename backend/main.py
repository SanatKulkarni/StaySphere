from typing import List
from fastapi import FastAPI, HTTPException, Form, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

app = FastAPI()
templates = Jinja2Templates(directory="templates")

# Configure CORS
origins = [
    "http://localhost:5500",
    "http://127.0.0.1:5500",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

class Room(BaseModel):
    room_number: str
    occupied: bool = False
    student: str = None

class Floor(BaseModel):
    floor_number: int
    rooms: List[Room]

class BuildingRequest(BaseModel):
    building_name: str
    num_floors: int
    rooms: List[List[str]]

class HostelBuilding(BaseModel):
    building_name: str
    floors: List[Floor]

class Student(BaseModel):
    name: str
    institute: str
    room: Room = None
    rating: int = 0
    feedback: str = ""

buildings = []
students = []

@app.post("/buildings")
async def add_building(request: Request, building_request: BuildingRequest):
    building_name = building_request.building_name
    num_floors = building_request.num_floors
    rooms = building_request.rooms
    room_number = building_request.room_number  # Added this line
    student_name = building_request.student_name  # Added this line

    floors = []
    for floor_number, floor_rooms in enumerate(rooms, start=1):
        floor = Floor(floor_number=floor_number, rooms=[Room(room_number=room) for room in floor_rooms])
        floors.append(floor)

    building = HostelBuilding(building_name=building_name, floors=floors)
    buildings.append(building)

    # Find the room object that matches the room number
    room = None
    for floor in building.floors:
        for r in floor.rooms:
            if r.room_number == room_number:
                room = r
                break
        if room:
            break

    # Update the room data
    if room:
        room.occupied = True
        room.student = student_name

    return {"message": "Building added successfully"}

@app.post("/students")
def add_student(name: str = Form(...), institute: str = Form(...)):
    student = Student(name=name, institute=institute)
    students.append(student)
    return {"message": "Student added successfully"}

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("student_index.html", {"request": request})

@app.get("/available_rooms", response_model=List[Room])
async def available_rooms():
    available_rooms = [room for building in buildings for floor in building.floors for room in floor.rooms if not room.occupied]
    return available_rooms

@app.post("/allocate_room")
async def allocate_room(student_name: str = Form(...), room_number: str = Form(...)):
    student = next((s for s in students if s.name == student_name), None)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    if student.room:
        raise HTTPException(status_code=400, detail="Student already has a room allocated")

    room = None
    for building in buildings:
        for floor in building.floors:
            for r in floor.rooms:
                if r.room_number == room_number:
                    room = r
                    break
            if room:
                break
        if room:
            break

    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    if room.occupied:
        raise HTTPException(status_code=400, detail="Room is already occupied")

    room.occupied = True
    room.student = student.name
    student.room = room

    return {"message": f"Room {room.room_number} allocated to {student.name}"}

@app.post("/reallocate_room")
async def reallocate_room(student_name: str = Form(...), new_room_number: str = Form(...)):
    student = next((s for s in students if s.name == student_name), None)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    if not student.room:
        raise HTTPException(status_code=400, detail="Student does not have a room allocated")

    new_room = None
    for building in buildings:
        for floor in building.floors:
            for r in floor.rooms:
                if r.room_number == new_room_number:
                    new_room = r
                    break
            if new_room:
                break
        if new_room:
            break

    if not new_room:
        raise HTTPException(status_code=404, detail="New room not found")
    if new_room.occupied:
        raise HTTPException(status_code=400, detail="New room is already occupied")

    old_room = student.room
    old_room.occupied = False
    old_room.student = None

    new_room.occupied = True
    new_room.student = student.name
    student.room = new_room

    return {"message": f"Room reallocated for {student.name} from {old_room.room_number} to {new_room.room_number}"}

@app.post("/student_feedback")
def submit_feedback(student_name: str = Form(...), rating: int = Form(...), feedback: str = Form(...)):
    student = next((s for s in students if s.name == student_name), None)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    student.rating = rating
    student.feedback = feedback

    return {"message": f"Feedback submitted for {student_name}"}

@app.get("/student_ratings")
def get_student_ratings():
    ratings = []
    for student in students:
        if student.rating > 0:
            ratings.append({
                "name": student.name,
                "rating": student.rating,
                "feedback": student.feedback
            })
    return ratings

@app.get("/empty_rooms")
def get_empty_rooms():
    empty_rooms = sum(1 for building in buildings for floor in building.floors for room in floor.rooms if not room.occupied)
    return {"empty_rooms": empty_rooms}

@app.get("/students_by_institute/{institute}")
def get_students_by_institute(institute: str):
    institute_students = [student for student in students if student.institute == institute]
    return institute_students

@app.get("/report/{report_type}")
def generate_report(report_type: str):
    if report_type == "student":
        return [{"name": student.name, "institute": student.institute, "room": student.room.room_number if student.room else "Not allocated"} for student in students]
    elif report_type == "building":
        building_reports = []
        for building in buildings:
            floor_reports = []
            for floor in building.floors:
                room_reports = [{"room_number": room.room_number, "occupied": room.occupied, "student": room.student} for room in floor.rooms]
                floor_reports.append({"floor_number": floor.floor_number, "rooms": room_reports})
            building_reports.append({"building_name": building.building_name, "floors": floor_reports})
        return building_reports
    elif report_type == "room_occupancy":
        total_rooms = sum(len(building.floors) * len(building.floors[0].rooms) for building in buildings)
        occupied_rooms = total_rooms - get_empty_rooms()["empty_rooms"]
        return {"total_rooms": total_rooms, "occupied_rooms": occupied_rooms, "empty_rooms": get_empty_rooms()["empty_rooms"]}
    else:
        raise HTTPException(status_code=400, detail="Invalid report type")
    
# Dummy data
building1 = HostelBuilding(
    building_name="Vedavathi",
    floors=[
        Floor(
            floor_number=1,
            rooms=[
                Room(room_number="A101", occupied=False),
                Room(room_number="A102", occupied=True, student="Amit"),
                Room(room_number="A103", occupied=False),
                Room(room_number="A104", occupied=False),
                Room(room_number="A105", occupied=True, student="Ajay"),
                Room(room_number="A106", occupied=False),
                Room(room_number="A107", occupied=True, student="Anamika"),
                Room(room_number="A108", occupied=False),
            ],
        ),
        Floor(
            floor_number=2,
            rooms=[
                Room(room_number="A201", occupied=False),
                Room(room_number="A202", occupied=True, student="Chaitanya"),
                Room(room_number="A203", occupied=False),
                Room(room_number="A204", occupied=False),
                Room(room_number="A205", occupied=True, student="Chitra Devi"),
                Room(room_number="A206", occupied=False),
                Room(room_number="A207", occupied=True, student="Devendra Kumar"),
                Room(room_number="A208", occupied=False),
                Room(room_number="A209", occupied=True, student="Gagan Jain"),
                Room(room_number="A210", occupied=False),
            ],
        ),
    ],
)

building2 = HostelBuilding(
    building_name="Ganga",
    floors=[
        Floor(
            floor_number=1,
            rooms=[
                Room(room_number="B101", occupied=True, student="Shruti Bhardwaj"),
                Room(room_number="B102", occupied=False),
                Room(room_number="B103", occupied=True, student="Akshay Jain"),
                Room(room_number="B104", occupied=False),
                Room(room_number="B105", occupied=True, student="Priyanka Goel"),
                Room(room_number="B106", occupied=False),
                Room(room_number="B107", occupied=True, student="Rahul Sharma"),
                Room(room_number="B108", occupied=False),
                Room(room_number="B109", occupied=True, student="Sakshi Jain"),
                Room(room_number="B110", occupied=False),
            ],
        ),
    ],
)

buildings = [building1, building2]

student1 = Student(name="Amit", institute="Institute A", room=building1.floors[0].rooms[1])
student2 = Student(name="Ajay", institute="Institute B", room=building1.floors[0].rooms[4])
student3 = Student(name="Anamika", institute="Institute A", room=building1.floors[0].rooms[6])
student4 = Student(name="Chaitanya", institute="Institute C", room=building1.floors[1].rooms[1])
student5 = Student(name="Chitra Devi", institute="Institute B", room=building1.floors[1].rooms[4])
student6 = Student(name="Devendra Kumar", institute="Institute A", room=building1.floors[1].rooms[6])
student7 = Student(name="Gagan Jain", institute="Institute B", room=building1.floors[1].rooms[8])
student8 = Student(name="Shruti Bharadwaj", institute="Institute C", room=building2.floors[0].rooms[0])
student9 = Student(name="Akshay Jain", institute="Institute A", room=building2.floors[0].rooms[2])
student10 = Student(name="Priyanka Goel", institute="Institute B", room=building2.floors[0].rooms[4])
student11 = Student(name="Rahul Sharma", institute="Institute C", room=building2.floors[0].rooms[6])
student12 = Student(name="Sakshi Jain", institute="Institute A", room=building2.floors[0].rooms[8])

students = [student1, student2, student3, student4, student5, student6, student7, student8, student9, student10, student11, student12]