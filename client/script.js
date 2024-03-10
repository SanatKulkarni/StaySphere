const BASE_URL = 'http://localhost:8000';

// Add building form submission
const addBuildingForm = document.getElementById('add-building-form');
addBuildingForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const buildingName = document.getElementById('building-name').value;
    const floorData = document.getElementById('floors').value;
    const floors = JSON.parse(floorData);

    const formData = new FormData();
    formData.append('building_name', buildingName);
    formData.append('floors', JSON.stringify(floors));

    try {
        const response = await fetch(`${BASE_URL}/buildings`, {
            method: 'POST',
            body: formData,
        });
        const data = await response.json();
        console.log(data.message);
        addBuildingForm.reset();
        fetchAndDisplayData(); // Fetch and display updated data
    } catch (error) {
        console.error('Error adding building:', error);
    }
});

// Add student form submission
const addStudentForm = document.getElementById('add-student-form');
addStudentForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const studentName = document.getElementById('student-name').value;
    const institute = document.getElementById('institute').value;

    const formData = new FormData();
    formData.append('name', studentName);
    formData.append('institute', institute);

    try {
        const response = await fetch(`${BASE_URL}/students`, {
            method: 'POST',
            body: formData,
        });
        const data = await response.json();
        console.log(data.message);
        addStudentForm.reset();
        fetchAndDisplayData(); // Fetch and display updated data
    } catch (error) {
        console.error('Error adding student:', error);
    }
});

// Function to fetch and display data
function fetchAndDisplayData() {
    // Fetch buildings
    fetch(`${BASE_URL}/report/building`)
        .then(response => response.json())
        .then(data => {
            const buildingsTable = document.getElementById('buildings-table');
            buildingsTable.innerHTML = `
                <tr>
                    <th>Building Name</th>
                    <th>Floor</th>
                    <th>Room</th>
                    <th>Occupied</th>
                    <th>Student</th>
                </tr>
            `;

            data.forEach(building => {
                building.floors.forEach(floor => {
                    floor.rooms.forEach(room => {
                        const row = buildingsTable.insertRow(-1);
                        row.insertCell(0).textContent = building.building_name;
                        row.insertCell(1).textContent = floor.floor_number;
                        row.insertCell(2).textContent = room.room_number;
                        row.insertCell(3).textContent = room.occupied ? 'Yes' : 'No';
                        row.insertCell(4).textContent = room.student || '';
                    });
                });
            });
        })
        .catch(error => console.error('Error fetching buildings:', error));

    // Fetch students
    fetch(`${BASE_URL}/report/student`)
        .then(response => response.json())
        .then(data => {
            const studentsTable = document.getElementById('students-table');
            studentsTable.innerHTML = `
                <tr>
                    <th>Name</th>
                    <th>Institute</th>
                    <th>Room</th>
                </tr>
            `;

            data.forEach(student => {
                const row = studentsTable.insertRow(-1);
                row.insertCell(0).textContent = student.name;
                row.insertCell(1).textContent = student.institute;
                row.insertCell(2).textContent = student.room || 'Not allocated';
            });
        })
        .catch(error => console.error('Error fetching students:', error));
}

// Fetch room occupancy report
fetch(`${BASE_URL}/report/room_occupancy`)
.then(response => response.json())
.then(data => {
    const reportsTable = document.getElementById('reports-table');
    reportsTable.innerHTML = `
        <tr>
            <th>Total Rooms</th>
            <th>Occupied Rooms</th>
            <th>Empty Rooms</th>
        </tr>
        <tr>
            <td>${data.total_rooms}</td>
            <td>${data.occupied_rooms}</td>
            <td>${data.empty_rooms}</td>
        </tr>
    `;
})
.catch(error => console.error('Error fetching room occupancy report:', error));



// Submit student feedback
const feedbackForm = document.getElementById('feedback-form');
feedbackForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const studentName = document.getElementById('student-name-feedback').value;
    const rating = parseInt(document.getElementById('rating').value);
    const feedbackText = document.getElementById('feedback-text').value;

    const formData = new FormData();
    formData.append('student_name', studentName);
    formData.append('rating', rating);
    formData.append('feedback', feedbackText);

    try {
        const response = await fetch(`${BASE_URL}/student_feedback`, {
            method: 'POST',
            body: formData,
        });
        const data = await response.json();
        console.log(data.message);
        feedbackForm.reset();
        fetchAndDisplayData(); // Fetch and display updated data
    } catch (error) {
        console.error('Error submitting feedback:', error);
    }
});


// Fetch student ratings
fetch(`${BASE_URL}/student_ratings`)
.then(response => response.json())
.then(data => {
    const ratingsTable = document.getElementById('ratings-table');
    // Clear the table before adding new rows
    while (ratingsTable.firstChild) {
        ratingsTable.removeChild(ratingsTable.firstChild);
    }

    const headerRow = ratingsTable.insertRow(-1);
    headerRow.innerHTML = `
        <tr>
            <th>Name</th>
            <th>Rating</th>
            <th>Feedback</th>
        </tr>
    `;

    data.forEach(rating => {
        const row = ratingsTable.insertRow(-1);
        const nameCell = row.insertCell(0);
        const ratingCell = row.insertCell(1);
        const feedbackCell = row.insertCell(2);

        nameCell.textContent = rating.name;
        ratingCell.textContent = rating.rating;
        feedbackCell.textContent = rating.feedback;
    });
})
.catch(error => console.error('Error fetching student ratings:', error));




// Fetch available rooms
async function fetchAvailableRooms() {
try {
const response = await fetch(`${BASE_URL}/available_rooms`);
const data = await response.json();
return data;
} catch (error) {
console.error('Error fetching available rooms:', error);
return [];
}
}

// Populate room select options
async function populateRoomOptions(selectElement) {
const availableRooms = await fetchAvailableRooms();
selectElement.innerHTML = '';
availableRooms.forEach(room => {
    const option = document.createElement('option');
    option.value = room.room_number;
    option.text = room.room_number;
    selectElement.add(option);
    });
}

// Add event listener for room allocation form submission
const allocateRoomForm = document.getElementById('allocate-room-form');
allocateRoomForm.addEventListener('submit', async (e) => {
e.preventDefault();
const studentName = document.getElementById('student-name-allocate').value;
const roomNumber = document.getElementById('room-select').value;

const formData = new FormData();
formData.append('student_name', studentName);
formData.append('room_number', roomNumber);

try {
const response = await fetch(`${BASE_URL}/allocate_room`, {
    method: 'POST',
    body: formData,
});
const data = await response.json();
console.log(data.message);
allocateRoomForm.reset();
fetchAndDisplayData(); // Fetch and display updated data
} catch (error) {
console.error('Error allocating room:', error);
}
});

const reallocateRoomForm = document.getElementById('reallocate-room-form');
reallocateRoomForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const studentName = document.getElementById('student-name-reallocate').value;
    const newRoomNumber = document.getElementById('new-room-select').value;

    const formData = new FormData();
    formData.append('student_name', studentName);
    formData.append('new_room_number', newRoomNumber);

    try {
        const response = await fetch(`${BASE_URL}/reallocate_room`, {
            method: 'POST',
            body: formData,
        });
        const data = await response.json();
        console.log(data.message);
        reallocateRoomForm.reset();
        fetchAndDisplayData(); // Fetch and display updated data
    } catch (error) {
        console.error('Error reallocating room:', error);
    }
});

// Initialize room select options
const roomSelect = document.getElementById('room-select');
const newRoomSelect = document.getElementById('new-room-select');
populateRoomOptions(roomSelect);
populateRoomOptions(newRoomSelect);

// Initial data fetch
fetchAndDisplayData();
