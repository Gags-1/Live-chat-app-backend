var client_id = Date.now();
document.querySelector("#ws-id").textContent = client_id;

var ws = new WebSocket(`ws://localhost:8000/ws/${client_id}`);
var statusElement = document.getElementById('status');

ws.onmessage = function(event) {
    var messages = document.getElementById('messages');
    var message = document.createElement('li');
    var content = document.createTextNode(event.data);
    message.appendChild(content);
    messages.appendChild(message);
    messages.scrollTop = messages.scrollHeight; // Auto-scroll to the bottom
};

function sendMessage(event) {
    var input = document.getElementById("messageText");
    if (input.value.trim() !== '') {
        ws.send(input.value);
        input.value = '';
    }
    event.preventDefault();
}

function disconnect() {
    if (ws) {
        ws.close();
        statusElement.textContent = "You have disconnected.";
        document.getElementById('disconnectBtn').disabled = true;
    }
}

ws.onclose = function() {
    statusElement.textContent = "Connection closed.";
    document.getElementById('disconnectBtn').disabled = true;
};
