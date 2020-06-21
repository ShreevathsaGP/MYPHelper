const chatForm = document.getElementById('chat-form');
const chatMessages = document.querySelector('.chat-messages');
const roomNameHolder = document.getElementById('room-name');
const roomName = roomNameHolder.innerHTML
const userList = document.getElementById('users');

// For outputtins messages
function outputMessage(data) {
    const div = document.createElement('div');
    div.classList.add('message');
    div.innerHTML = `<p class="meta">${data.username} <span>${new Date().getHours() + ":" + new Date().getMinutes()}</span></p>
    <p class="text">
      ${data.msg}
    </p>`;
    document.querySelector('.chat-messages').appendChild(div);
  }

function updateUsers(clients) {
    console.log(clients);
    userList.innerHTML = '';
    for (let i = 0; i < clients[roomName].length; i++) {
        li = document.createElement('li');
        li.innerHTML = `<li>${clients[roomName][i]}</li>`
        
        document.querySelector('#users').appendChild(li)
    }
}

document.addEventListener('DOMContentLoaded', () => {
    // DO NOT CHANGE
    var socket = io.connect('http://' + document.domain + ':' + location.port);
    
    // Join room
    socket.on('connect', () => {
        socket.emit('join', {'username': username, 'room':roomName});
        console.log(`${username} has joined the ${roomName} room!`)
    });
    
    // Leave room
    socket.on('disconnect', () => {
        socket.emit('leave', {'username':username, 'room':roomName})
        console.log(`${username} has left the ${roomName} room!`)
    });

    socket.on("disconnecting", () => {
        socket.emit('leave', {'username':username, 'room':roomName})
        console.log(`${username} has left the ${roomName} room!`)
    });

    // Update clients
    socket.on('user-update', data => {
        console.log(`Updating clients list for ${roomName}`)
        updateUsers(data);
    });

    document.querySelector('#leave_button').onclick = () => {
        socket.emit('leave', {'username':username, 'room':roomName})
        console.log(`${username} has left the ${roomName} room!`)
    }

    // DO NOT CHANGE

    // MESSAGE
    socket.on('message', data => {
        console.log(`Message receieved: ${data}`)
        outputMessage(data);

        // Scroll down
        chatMessages.scrollTop = chatMessages.scrollHeight;
    })
    /* Old studd with button
    document.querySelector('#send_message').onclick = () => {
        socket.send({'msg':document.querySelector('#msg').value, 'username':username, 'room':roomName});
    }
    */

    chatForm.addEventListener('submit', e => {
        e.preventDefault();
        socket.send({'msg':document.querySelector('#msg').value, 'username':username, 'room':roomName});
        document.getElementById("msg").value = ''
    });
    

    // MESSAGE        

})

var input = document.getElementById("msg");
/*
input.addEventListener('keyup', function(event) {
    if (event.keyCode === 13) {
        event.preventDefault();

        // If enter is pressed, then clidk the send button
        document.getElementById("send_message").click();

        // If enter is pressed, then clear the input field
        document.getElementById("msg").value = '';
    }
})

window.addEventListener('beforeunload', function (e) { 
    document.getElementById("leave_button").click();
    e.returnValue = ''; 
}); 
*/
