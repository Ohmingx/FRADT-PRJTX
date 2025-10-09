// static/js/main.js (Final Merged Version)
document.addEventListener('DOMContentLoaded', () => {
    const socket = io();

    const video = document.getElementById('video');
    const captureCanvas = document.getElementById('canvas'); // For capturing
    const overlayCanvas = document.getElementById('overlay-canvas'); // For drawing
    const overlayCtx = overlayCanvas.getContext('2d');

    const captureBtn = document.getElementById('capture-btn');
    const personNameInput = document.getElementById('person-name');
    const statusMessage = document.getElementById('status-message');
    const systemLogs = document.getElementById('system-logs');

    // 1. Access Webcam
    if (navigator.mediaDevices.getUserMedia) {
        navigator.mediaDevices.getUserMedia({ video: true })
            .then(function (stream) {
                video.srcObject = stream;
            })
            .catch(function (error) {
                console.log("Something went wrong!", error);
                statusMessage.textContent = "Error accessing webcam. Please grant permission.";
            });
    }

    // --- NEWLY ADDED SECTION START ---
    // This ensures the canvas is the same size as the video feed, making the boxes align correctly.
    video.addEventListener('loadedmetadata', () => {
        overlayCanvas.width = video.videoWidth;
        overlayCanvas.height = video.videoHeight;
        // Also resize the hidden capture canvas
        captureCanvas.width = video.videoWidth;
        captureCanvas.height = video.videoHeight;
    });
    // --- NEWLY ADDED SECTION END ---


    // 2. Send frames to the server for processing periodically
    setInterval(() => {
        if (video.readyState === video.HAVE_ENOUGH_DATA) {
            // Draw video to a temporary canvas to get the image data
            const tempCanvas = document.createElement('canvas');
            tempCanvas.width = video.videoWidth;
            tempCanvas.height = video.videoHeight;
            const tempCtx = tempCanvas.getContext('2d');
            tempCtx.drawImage(video, 0, 0, tempCanvas.width, tempCanvas.height);
            const imageData = tempCanvas.toDataURL('image/jpeg');
            
            // Send the frame to the server
            socket.emit('process_frame', { image: imageData });
        }
    }, 400); // Send a frame every 400 milliseconds

    // 3. Listen for recognition results and draw them
    socket.on('recognition_results', (data) => {
        // Clear the overlay canvas
        overlayCtx.clearRect(0, 0, overlayCanvas.width, overlayCanvas.height);

        // Draw boxes and names for each result
        data.results.forEach(person => {
            const [left, top, right, bottom] = person.box;
            const name = person.name;

            // Draw the box
            overlayCtx.strokeStyle = name === "Unknown" ? 'red' : 'lime';
            overlayCtx.lineWidth = 2;
            overlayCtx.strokeRect(left, top, right - left, bottom - top);

            // Draw the label background
            overlayCtx.fillStyle = name === "Unknown" ? 'red' : 'lime';
            overlayCtx.fillRect(left, bottom - 25, right - left, 25);
            
            // Draw the name text
            overlayCtx.fillStyle = 'black';
            overlayCtx.font = '18px Arial';
            overlayCtx.fillText(name, left + 6, bottom - 6);
        });
    });

    // Listen for the 'update_attendance' event from the server
    socket.on('update_attendance', function(data) {
        console.log('Received attendance update:', data);
        logMessage(`✅ Attendance marked for ${data.name} at ${data.time}`);
    });

    // 4. Handle Capture Button Click
    captureBtn.addEventListener('click', () => {
        const name = personNameInput.value.trim();
        if (!name) {
            statusMessage.textContent = "Please enter a name.";
            statusMessage.style.color = 'red';
            return;
        }
        statusMessage.textContent = `Capturing image for ${name}...`;
        statusMessage.style.color = 'blue';

        // Use the correctly sized hidden canvas for capture
        const context = captureCanvas.getContext('2d');
        context.drawImage(video, 0, 0, captureCanvas.width, captureCanvas.height);
        const imageData = captureCanvas.toDataURL('image/jpeg');
        socket.emit('add_new_person', { name: name, image: imageData });
        personNameInput.value = '';
    });

    // 5. Listen for server response for adding a person
    socket.on('add_person_response', (data) => {
        if (data.success) {
            statusMessage.textContent = data.message;
            statusMessage.style.color = 'green';
            logMessage(`SUCCESS: ${data.message}`);
        } else {
            statusMessage.textContent = data.message;
            statusMessage.style.color = 'red';
            logMessage(`ERROR: ${data.message}`);
        }
    });
    
    function logMessage(message) {
        const p = document.createElement('p');
        p.textContent = `[${new Date().toLocaleTimeString()}] ${message}`;
        systemLogs.insertBefore(p, systemLogs.firstChild);
    }
});