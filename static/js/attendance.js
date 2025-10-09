// static/js/attendance.js
document.addEventListener('DOMContentLoaded', () => {
    const socket = io();
    const tableBody = document.getElementById('attendance-table-body');

    socket.on('update_attendance', function(data) {
        console.log('Received attendance update:', data);

        // Create a new row
        const newRow = document.createElement('tr');

        // Create cells
        const nameCell = document.createElement('td');
        nameCell.textContent = data.name;
        const dateCell = document.createElement('td');
        const today = new Date();
        dateCell.textContent = today.getFullYear() + '-' + String(today.getMonth() + 1).padStart(2, '0') + '-' + String(today.getDate()).padStart(2, '0');
        const timeCell = document.createElement('td');
        timeCell.textContent = data.time;

        // Append cells to the row
        newRow.appendChild(nameCell);
        newRow.appendChild(dateCell);
        newRow.appendChild(timeCell);

        // Add the new row to the top of the table
        tableBody.insertBefore(newRow, tableBody.firstChild);
    });
});