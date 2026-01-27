const state = {
  token: localStorage.getItem("doggzi_token"),
  user: JSON.parse(localStorage.getItem("doggzi_user") || "null"),
};

const toast = document.getElementById("toast");
const sessionStatus = document.getElementById("session-status");
const sessionRole = document.getElementById("session-role");

const tabs = document.querySelectorAll(".tab");
const sections = document.querySelectorAll(".section");

const loginForm = document.getElementById("login-form");
const signupForm = document.getElementById("signup-form");
const logoutBtn = document.getElementById("logout-btn");

const dashboardSummary = document.getElementById("dashboard-summary");
const employeeTable = document.getElementById("employee-table");
const leaveTable = document.getElementById("leave-table");
const attendanceTable = document.getElementById("attendance-table");
const approvalTable = document.getElementById("approval-table");
const notificationsTable = document.getElementById("notifications-table");
const auditTable = document.getElementById("audit-table");

const employeeForm = document.getElementById("employee-form");
const leaveForm = document.getElementById("leave-form");
const attendanceForm = document.getElementById("attendance-form");

function showToast(message, isError = false) {
  toast.textContent = message;
  toast.style.background = isError ? "#b5242f" : "#0f3d6e";
  toast.classList.add("show");
  setTimeout(() => toast.classList.remove("show"), 2600);
}

function setSession(user) {
  state.user = user;
  sessionStatus.textContent = user ? user.email : "Signed out";
  sessionRole.textContent = user ? user.role_key : "-";
  logoutBtn.disabled = !user;
}

function setAuth(token, user) {
  state.token = token;
  state.user = user;
  if (token) {
    localStorage.setItem("doggzi_token", token);
  } else {
    localStorage.removeItem("doggzi_token");
  }
  if (user) {
    localStorage.setItem("doggzi_user", JSON.stringify(user));
  } else {
    localStorage.removeItem("doggzi_user");
  }
  setSession(user);
}

async function apiFetch(path, options = {}) {
  const headers = { "Content-Type": "application/json", ...(options.headers || {}) };
  if (state.token) {
    headers.Authorization = `Bearer ${state.token}`;
  }
  const response = await fetch(path, { ...options, headers });
  const payload = await response.json();
  if (!response.ok) {
    throw new Error(payload?.message || "Request failed");
  }
  return payload.data;
}

function setActiveSection(targetId) {
  sections.forEach((section) => {
    section.classList.toggle("active", section.id === targetId);
  });
  tabs.forEach((tab) => {
    tab.classList.toggle("active", tab.dataset.section === targetId);
  });
}

tabs.forEach((tab) => {
  tab.addEventListener("click", () => setActiveSection(tab.dataset.section));
});

loginForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const formData = new FormData(loginForm);
  const payload = Object.fromEntries(formData.entries());
  try {
    const data = await apiFetch("/api/auth/login", {
      method: "POST",
      body: JSON.stringify(payload),
    });
    setAuth(data.access_token, data.user);
    showToast("Login successful");
    await refreshAll();
  } catch (error) {
    showToast(error.message, true);
  }
});

signupForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const formData = new FormData(signupForm);
  const payload = Object.fromEntries(formData.entries());
  try {
    const data = await apiFetch("/api/auth/register", {
      method: "POST",
      body: JSON.stringify(payload),
    });
    showToast(`Signup submitted. Status: ${data.status}`);
    signupForm.reset();
  } catch (error) {
    showToast(error.message, true);
  }
});

logoutBtn.addEventListener("click", async () => {
  if (!state.token) return;
  try {
    await apiFetch("/api/auth/logout", { method: "POST" });
  } catch (error) {
    showToast(error.message, true);
  } finally {
    setAuth(null, null);
  }
});

employeeForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const formData = new FormData(employeeForm);
  const payload = Object.fromEntries(formData.entries());
  try {
    await apiFetch("/api/employees", {
      method: "POST",
      body: JSON.stringify(payload),
    });
    showToast("Employee created");
    employeeForm.reset();
    await loadEmployees();
  } catch (error) {
    showToast(error.message, true);
  }
});

leaveForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const formData = new FormData(leaveForm);
  const payload = Object.fromEntries(formData.entries());
  try {
    await apiFetch("/api/leaves", {
      method: "POST",
      body: JSON.stringify(payload),
    });
    showToast("Leave submitted");
    leaveForm.reset();
    await loadLeaves();
  } catch (error) {
    showToast(error.message, true);
  }
});

attendanceForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const formData = new FormData(attendanceForm);
  const payload = Object.fromEntries(formData.entries());
  try {
    await apiFetch("/api/attendance", {
      method: "POST",
      body: JSON.stringify(payload),
    });
    showToast("Attendance logged");
    attendanceForm.reset();
    await loadAttendance();
  } catch (error) {
    showToast(error.message, true);
  }
});

function renderRows(items, formatter) {
  if (!items || items.length === 0) {
    return "<div class=\"row\">No records found.</div>";
  }
  return items.map(formatter).join("");
}

function renderDashboard(summary) {
  if (!summary) {
    dashboardSummary.innerHTML = "<div class=\"kpi\">No data</div>";
    return;
  }
  const entries = Object.entries(summary);
  dashboardSummary.innerHTML = entries
    .map(([key, value]) => {
      return `
        <div class="kpi">
          <div class="label">${key.replace(/_/g, " ")}</div>
          <strong>${value}</strong>
        </div>
      `;
    })
    .join("");
}

async function loadDashboard() {
  if (!state.token) return;
  const data = await apiFetch("/api/dashboard/summary");
  renderDashboard(data);
}

async function loadEmployees() {
  if (!state.token) return;
  const data = await apiFetch("/api/employees?page=1&page_size=10");
  employeeTable.innerHTML = renderRows(data.items, (item) => {
    return `
      <div class="row">
        <strong>${item.full_name}</strong>
        <div>${item.employee_code} · ${item.department || ""} · ${item.designation || ""}</div>
        <span class="badge ${item.status}">${item.status}</span>
      </div>
    `;
  });
}

async function loadLeaves() {
  if (!state.token) return;
  const data = await apiFetch("/api/leaves?page=1&page_size=10");
  leaveTable.innerHTML = renderRows(data.items, (item) => {
    return `
      <div class="row">
        <strong>${item.employee_name || item.employee_id}</strong>
        <div>${item.leave_type} · ${item.start_date} → ${item.end_date}</div>
        <span class="badge ${item.status}">${item.status}</span>
      </div>
    `;
  });
}

async function loadAttendance() {
  if (!state.token) return;
  const data = await apiFetch("/api/attendance?page=1&page_size=10");
  attendanceTable.innerHTML = renderRows(data.items, (item) => {
    return `
      <div class="row">
        <strong>${item.employee_name || item.employee_id}</strong>
        <div>${item.date} · ${item.status}</div>
        <div>${item.check_in || "-"} → ${item.check_out || "-"}</div>
      </div>
    `;
  });
}

async function loadApprovals() {
  if (!state.token) return;
  const data = await apiFetch("/api/approvals?page=1&page_size=10");
  approvalTable.innerHTML = renderRows(data.items, (item) => {
    return `
      <div class="row">
        <strong>${item.entity_type}</strong>
        <div>Workflow: ${item.workflow_key}</div>
        <div>Entity: ${item.entity_id}</div>
        <span class="badge ${item.status}">${item.status}</span>
        <div class="inline-actions">
          <button class="ghost" data-approve="${item.id}">Approve</button>
          <button class="ghost" data-reject="${item.id}">Reject</button>
        </div>
      </div>
    `;
  });
}

approvalTable.addEventListener("click", async (event) => {
  const approveId = event.target.getAttribute("data-approve");
  const rejectId = event.target.getAttribute("data-reject");
  if (!approveId && !rejectId) return;
  const id = approveId || rejectId;
  const action = approveId ? "approve" : "reject";
  const comment = window.prompt(`Add comment for ${action}`, "");
  try {
    await apiFetch(`/api/approvals/${id}/${action}`, {
      method: "PUT",
      body: JSON.stringify({ comment }),
    });
    showToast(`Approval ${action}d`);
    await loadApprovals();
  } catch (error) {
    showToast(error.message, true);
  }
});

async function loadNotifications() {
  if (!state.token) return;
  const data = await apiFetch("/api/notifications?page=1&page_size=10");
  notificationsTable.innerHTML = renderRows(data.items, (item) => {
    return `
      <div class="row">
        <strong>${item.title}</strong>
        <div>${item.message}</div>
        <span class="badge ${item.read ? "approved" : "pending"}">${item.read ? "read" : "unread"}</span>
      </div>
    `;
  });
}

async function loadAudit() {
  if (!state.token) return;
  const data = await apiFetch("/api/audit?limit=10&page=1");
  auditTable.innerHTML = renderRows(data.items, (item) => {
    return `
      <div class="row">
        <strong>${item.action}</strong>
        <div>${item.entity_type} · ${item.entity_id}</div>
        <div>${item.created_at}</div>
      </div>
    `;
  });
}

async function refreshAll() {
  await Promise.all([
    loadDashboard(),
    loadEmployees(),
    loadLeaves(),
    loadAttendance(),
    loadApprovals(),
    loadNotifications(),
    loadAudit(),
  ]);
}

document.getElementById("refresh-dashboard").addEventListener("click", loadDashboard);
document.getElementById("refresh-employees").addEventListener("click", loadEmployees);
document.getElementById("refresh-leaves").addEventListener("click", loadLeaves);
document.getElementById("refresh-attendance").addEventListener("click", loadAttendance);
document.getElementById("refresh-approvals").addEventListener("click", loadApprovals);
document.getElementById("refresh-notifications").addEventListener("click", loadNotifications);
document.getElementById("refresh-audit").addEventListener("click", loadAudit);

document.getElementById("mark-all-read").addEventListener("click", async () => {
  try {
    await apiFetch("/api/notifications/read-all", { method: "PUT" });
    showToast("Notifications marked as read");
    await loadNotifications();
  } catch (error) {
    showToast(error.message, true);
  }
});

setSession(state.user);
if (state.token) {
  refreshAll();
}
