const signupSocket = new WebSocket("wss://www.example.com/socketserver");

//Send to signup information to the server
function sendData(event) {
  event.preventDefault();

  // Collect input values
  const email = document.getElementById("exampleEmailInput").value;
  const username = document.getElementById("exampleusername").value;
  const location = document.getElementById("examplelocation").value;
  
  const checkboxes = document.querySelectorAll("input[type='checkbox']");
  const notifications = [];
  checkboxes.forEach(checkbox => {
    if (checkbox.checked) {
      notifications.push(checkbox.nextElementSibling.textContent.trim());
    }
  });

  const msg = {
    type: "message",
    data: {
      email: email,
      username: username,
      location: location,
      notifications: notifications
    },
    id: clientID, // You need to define clientID somewhere in your code
    date: Date.now(),
  };
  
  
  signupSocket.send(JSON.stringify(msg));
}

document.querySelector('form').addEventListener('submit', sendData);