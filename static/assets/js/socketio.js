document.addEventListener('DOMContentLoaded', () => {
    var socket = io.connect('http://' + document.domain + ':' + location.port);

    socket.on('connect', () => {
        socket.send("I am connected")
        //Automatically goes to message bucket
    });

    socket.on('message', data => {
        console.log('Message received: ' + data)
        const p = document.createElement('p');
        const span_username = document.createElement('span');
        const span_timestamp = document.createElement('span');
        const br = document.createElement('br');
        
        span_username.innerHTML = data.username;
        span_timestamp.innerHTML = data.time_stamp;

        p.innerHTML = span_username.outerHTML + br.outerHTML + data.msg + span_timestamp.outerHTML;
        document.querySelector('#chat-msg-list').append(p)

    });

    document.querySelector('#send_message').onclick = () => {
        socket.send({'msg': document.querySelector('#user_message').value, 'username':username, 'school': school, 'country':country});
    }

    //Room selection
    document.querySelectorAll('select-room').forEach(li => {
        li.onclick = () => {
            let newRoom = li.innerHTML;
            if (newRoom == room) {
                msg = `You are already in ${room} room.`
                print_system_message(msg)
            }
        }
    })

})