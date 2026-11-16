// Small helper for calling the backend
async function api(path, method = "GET", body = null) {
  const options = { method, headers: { "Content-Type": "application/json" } };
  if (body) options.body = JSON.stringify(body);
  const res = await fetch(path, options);
  const data = await res.json();
  if (!res.ok) throw new Error(data.detail || "Something went wrong");
  return data;
}

// The logged-in user is kept in the browser
function getUser() {
  return JSON.parse(localStorage.getItem("user"));
}

function requireLogin() {
  const user = getUser();
  if (!user) window.location.href = "index.html";
  return user;
}

function logout() {
  localStorage.removeItem("user");
  window.location.href = "index.html";
}

function showMessage(id, text, isError = false) {
  const el = document.getElementById(id);
  el.textContent = text;
  el.className = isError ? "message error" : "message";
}
