const form = document.getElementById("candidateForm");
const tableBody = document.getElementById("candidateTable");
const toast = document.getElementById("toast");
const demoButton = document.getElementById("demoButton");

const showToast = (message, isError = false) => {
  toast.textContent = message;
  toast.style.background = isError ? "#c53030" : "#1a365d";
  toast.classList.add("show");
  setTimeout(() => toast.classList.remove("show"), 3000);
};

const setError = (field, message) => {
  const errorEl = document.querySelector(`[data-error-for="${field}"]`);
  if (errorEl) {
    errorEl.textContent = message || "";
  }
};

const clearErrors = () => {
  document.querySelectorAll(".error").forEach((el) => {
    el.textContent = "";
  });
};

const updateInterviewDateState = () => {
  const interviewScheduled = form.interview_scheduled.value;
  if (interviewScheduled === "Yes") {
    form.interview_date.disabled = false;
  } else {
    form.interview_date.value = "";
    form.interview_date.disabled = true;
  }
};

const updateJoiningDateState = () => {
  const selectionStatus = form.selection_status.value;
  if (selectionStatus === "Selected") {
    form.joining_date.disabled = false;
  } else {
    form.joining_date.value = "";
    form.joining_date.disabled = true;
  }
};

const fetchCandidates = async () => {
  const response = await fetch("/api/candidates");
  const data = await response.json();
  tableBody.innerHTML = "";
  data.data.forEach((candidate) => {
    const row = document.createElement("tr");
    row.innerHTML = `
      <td>${candidate.candidate_id}</td>
      <td>${candidate.candidate_name}</td>
      <td>${candidate.mobile}</td>
      <td>${candidate.position}</td>
      <td>${candidate.selection_status}</td>
      <td><a href="/candidate/${candidate.candidate_id}">View</a></td>
    `;
    tableBody.appendChild(row);
  });
};

const validateForm = () => {
  let valid = true;
  clearErrors();

  if (form.candidate_name.value.trim().length < 3) {
    setError("candidate_name", "Candidate name must be at least 3 characters.");
    valid = false;
  }

  if (!/^\d{10}$/.test(form.mobile.value.trim())) {
    setError("mobile", "Mobile number must be 10 digits.");
    valid = false;
  }

  if (!/^\S+@\S+\.\S+$/.test(form.email.value.trim())) {
    setError("email", "Email must be valid.");
    valid = false;
  }

  if (!form.position.value) {
    setError("position", "Position Applied For is required.");
    valid = false;
  }

  if (!form.source.value) {
    setError("source", "Source is required.");
    valid = false;
  }

  if (!form.interview_scheduled.value) {
    setError("interview_scheduled", "Interview Scheduled is required.");
    valid = false;
  }

  if (form.interview_scheduled.value === "Yes" && !form.interview_date.value) {
    setError("interview_date", "Interview Date is required when scheduled.");
    valid = false;
  }

  if (!form.interview_status.value) {
    setError("interview_status", "Interview Status is required.");
    valid = false;
  }

  if (!form.selection_status.value) {
    setError("selection_status", "Selection Status is required.");
    valid = false;
  }

  if (!form.offer_released.value) {
    setError("offer_released", "Offer Released is required.");
    valid = false;
  }

  if (form.selection_status.value === "Selected" && !form.joining_date.value) {
    setError("joining_date", "Joining Date is required when selected.");
    valid = false;
  }

  if (!form.final_status.value) {
    setError("final_status", "Final Status is required.");
    valid = false;
  }

  if (form.remarks.value.length > 500) {
    setError("remarks", "Remarks cannot exceed 500 characters.");
    valid = false;
  }

  return valid;
};

form.addEventListener("change", (event) => {
  if (event.target.name === "interview_scheduled") {
    updateInterviewDateState();
  }
  if (event.target.name === "selection_status") {
    updateJoiningDateState();
  }
});

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  if (!validateForm()) {
    showToast("Please fix validation errors.", true);
    return;
  }

  const payload = Object.fromEntries(new FormData(form));

  const response = await fetch("/api/candidates", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    const data = await response.json();
    if (data.errors) {
      Object.entries(data.errors).forEach(([field, message]) => {
        setError(field, message);
      });
    } else {
      showToast(data.error || "Failed to save candidate.", true);
    }
    return;
  }

  form.reset();
  updateInterviewDateState();
  updateJoiningDateState();
  showToast("Candidate saved successfully.");
  await fetchCandidates();
});

const demoData = () => {
  const today = new Date().toISOString().split("T")[0];
  form.candidate_name.value = "Ravi Kumar";
  form.mobile.value = "9876543210";
  form.email.value = "ravi.kumar@example.com";
  form.position.value = "Helper";
  form.source.value = "Referral";
  form.interview_scheduled.value = "Yes";
  form.interview_date.value = today;
  form.interview_status.value = "Attended";
  form.selection_status.value = "Selected";
  form.offer_released.value = "Yes";
  form.joining_date.value = today;
  form.final_status.value = "Joined";
  form.remarks.value = "Demo entry";
  updateInterviewDateState();
  updateJoiningDateState();
};

demoButton.addEventListener("click", (event) => {
  event.preventDefault();
  demoData();
});

updateInterviewDateState();
updateJoiningDateState();
fetchCandidates();
