const courseId = JSON.parse(
    document.getElementById('course_id').textContent
);
const url = 'ws://' + window.location.host + '/ws/chat/room/' + courseId + '/';
const chatSocket = new WebSocket(url);

chatSocket.onmessage = function(event) {
    const data = JSON.parse(event.data);
    const chat = document.getElementById('chat');
    chat.innerHTML += '<div class="message">' + data.message + '</div>';
    chat.scrollTop = chat.scrollHeight;
};

chatSocket.onclose = function(event) {
    console.error('Chat socket closed unexpectedly');
};


const input = document.getElementById('chat-message-input');
const submitButton = document.getElementById('chat-message-submit');

submitButton.addEventListener('click', function(event) {
    const message = input.value;
    if(message) {
        // отправить сообщение в формате json
        chatSocket.send(JSON.stringify({'message': message}));
        // очистить поле ввода
        input.value = '';
        input.focus();
    }
});


input.addEventListener('keypress', function(event) {
    if (event.key === 'Enter') {
        // отменить стандартное действие
        // если необходимо
        event.preventDefault();
        // запустить событие нажатие клавиши
        submitButton.click();
    }
});
input.focus();
