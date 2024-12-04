document.getElementById("loginForm").addEventListener("submit", async function(event) {
  event.preventDefault();

  const username = document.getElementById("username").value;
  const password = document.getElementById("password").value;

  // ส่งข้อมูลไปยัง API
  const response = await fetch("https://your-api-endpoint.com/login", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ username, password })
  });

  const result = await response.json();
  if (result.success) {
    alert("Login successful!");
  } else {
    alert("Invalid username or password!");
  }
});
