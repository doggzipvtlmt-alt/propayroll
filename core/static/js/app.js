const apiBase = "/api";

const loginForm = document.getElementById("login-form");
const signupForm = document.getElementById("signup-form");
const loginResult = document.getElementById("login-result");
const signupResult = document.getElementById("signup-result");
const tokenStatus = document.getElementById("token-status");
const apiBaseLabel = document.getElementById("api-base");
const logoutBtn = document.getElementById("logout-btn");
const clearTokenBtn = document.getElementById("clear-token-btn");

const updateTokenStatus = () => {
  const token = localStorage.getItem("accessToken");
  tokenStatus.textContent = token ? "Authenticated (token stored)" : "Not authenticated";
};

apiBaseLabel.textContent = apiBase;
updateTokenStatus();

const showResult = (element, message, isError = false) => {
  element.textContent = message;
  element.style.color = isError ? "#b42318" : "#1c7c54";
};

loginForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  loginResult.textContent = "Signing in...";
  const formData = new FormData(loginForm);
  const payload = {
    email: formData.get("email"),
    password: formData.get("password"),
  };

  try {
    const response = await fetch(`${apiBase}/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    const data = await response.json();
    if (!response.ok) {
      showResult(loginResult, data.error || "Login failed.", true);
      return;
    }
    localStorage.setItem("accessToken", data.access);
    localStorage.setItem("refreshToken", data.refresh);
    showResult(loginResult, `Welcome back, ${data.user.full_name || data.user.email}.`);
    updateTokenStatus();
  } catch (error) {
    showResult(loginResult, "Unable to reach the server. Please retry.", true);
  }
});

signupForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  signupResult.textContent = "Submitting request...";
  const formData = new FormData(signupForm);
  const payload = {
    full_name: formData.get("full_name"),
    email: formData.get("email"),
    phone_number: formData.get("phone_number"),
    role_requested: formData.get("role_requested"),
  };

  try {
    const response = await fetch(`${apiBase}/auth/signup`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    const data = await response.json();
    if (!response.ok) {
      showResult(signupResult, data.error || "Signup request failed.", true);
      return;
    }
    showResult(signupResult, data.message || "Signup request submitted.");
    signupForm.reset();
  } catch (error) {
    showResult(signupResult, "Unable to reach the server. Please retry.", true);
  }
});

logoutBtn.addEventListener("click", () => {
  localStorage.removeItem("accessToken");
  localStorage.removeItem("refreshToken");
  updateTokenStatus();
  showResult(loginResult, "Logged out.");
});

clearTokenBtn.addEventListener("click", () => {
  localStorage.clear();
  updateTokenStatus();
  showResult(loginResult, "Local tokens cleared.");
});
