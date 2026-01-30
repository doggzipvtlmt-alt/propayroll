const apiBase = "/api/hrms";

const candidateForm = document.getElementById("candidate-form");
const candidateResult = document.getElementById("candidate-result");
const candidateStatus = document.getElementById("candidate-status");
const onboardingForm = document.getElementById("onboarding-form");
const onboardingResult = document.getElementById("onboarding-result");
const onboardingStatus = document.getElementById("onboarding-status");
const onboardingCard = document.getElementById("onboarding-card");
const candidateIdInput = document.getElementById("candidate-id");
const candidateIdDisplay = document.getElementById("candidate-id-display");
const attendanceForm = document.getElementById("attendance-form");
const attendanceResult = document.getElementById("attendance-result");
const attendanceStatus = document.getElementById("attendance-status");
const attendanceCandidateId = document.getElementById("attendance-candidate-id");
const attendanceTable = document.getElementById("attendance-table");
const candidatesTable = document.getElementById("candidates-table");
const refreshTableBtn = document.getElementById("refresh-table");
const refreshAttendanceBtn = document.getElementById("refresh-attendance");

const interviewScheduledInputs = document.querySelectorAll("input[name='interview_scheduled']");
const interviewDateInput = document.querySelector("input[name='interview_date']");
const selectionStatusInput = document.querySelector("select[name='selection_status']");
const joiningDateInput = document.querySelector("input[name='joining_date']");
const categoryInputs = document.querySelectorAll("input[name='category']");
const formalSection = document.getElementById("formal-section");
const nonFormalSection = document.getElementById("non-formal-section");
const optionalSection = document.getElementById("optional-section");

const showResult = (element, message, isError = false) => {
  element.textContent = message;
  element.classList.remove("success", "error");
  element.classList.add(isError ? "error" : "success");
};

const setCandidateContext = (candidateId) => {
  candidateIdInput.value = candidateId;
  candidateIdDisplay.value = candidateId;
  attendanceCandidateId.value = candidateId;
};

const setLocked = (locked) => {
  onboardingForm.classList.toggle("locked", locked);
  onboardingStatus.textContent = locked ? "Locked" : "Ready";
  onboardingStatus.classList.toggle("locked", locked);
};

const updateInterviewDateState = () => {
  const scheduled = document.querySelector("input[name='interview_scheduled']:checked");
  const enabled = scheduled && scheduled.value === "Yes";
  interviewDateInput.disabled = !enabled;
  if (!enabled) {
    interviewDateInput.value = "";
  }
};

const updateJoiningDateState = () => {
  const enabled = selectionStatusInput.value === "Selected";
  joiningDateInput.disabled = !enabled;
  if (!enabled) {
    joiningDateInput.value = "";
  }
};

const updateCategorySections = () => {
  const selected = document.querySelector("input[name='category']:checked");
  const category = selected ? selected.value : "";
  formalSection.classList.toggle("hidden", category !== "formal");
  nonFormalSection.classList.toggle("hidden", category !== "non_formal");
  optionalSection.classList.toggle("hidden", !category);
};

const validateCandidateForm = () => {
  const requiredFields = candidateForm.querySelectorAll("[required]");
  for (const field of requiredFields) {
    if (field.disabled) {
      continue;
    }
    if (field.type === "radio") {
      const group = candidateForm.querySelectorAll(`input[name='${field.name}']`);
      const checked = Array.from(group).some((input) => input.checked);
      if (!checked) {
        return `Please select ${field.name.replace(/_/g, " ")}.`;
      }
      continue;
    }
    if (!field.value || !field.value.trim()) {
      return `Please fill ${field.name.replace(/_/g, " ")}.`;
    }
  }
  return "";
};

const validateOnboardingForm = () => {
  const requiredFields = onboardingForm.querySelectorAll("[required]");
  for (const field of requiredFields) {
    if (field.closest(".hidden")) {
      continue;
    }
    if (field.type === "radio") {
      const group = onboardingForm.querySelectorAll(`input[name='${field.name}']`);
      const checked = Array.from(group).some((input) => input.checked);
      if (!checked) {
        return `Please select ${field.name.replace(/_/g, " ")}.`;
      }
      continue;
    }
    if (field.type === "file") {
      if (!field.files || field.files.length === 0) {
        return `Upload required document: ${field.name.replace(/_/g, " ")}.`;
      }
      continue;
    }
    if (!field.value || !field.value.trim()) {
      return `Please fill ${field.name.replace(/_/g, " ")}.`;
    }
  }
  const experienced = onboardingForm.querySelector("input[name='formal_experienced']:checked");
  if (formalSection.classList.contains("hidden")) {
    return "";
  }
  if (experienced && experienced.value === "Yes") {
    const requiredExperience = [
      "formal_offer_letter",
      "formal_experience_letter",
      "formal_salary_slips",
    ];
    for (const name of requiredExperience) {
      const field = onboardingForm.querySelector(`input[name='${name}']`);
      if (field && (!field.files || field.files.length === 0)) {
        return `Upload required document: ${name.replace(/_/g, " ")}.`;
      }
    }
  }
  return "";
};

const renderCandidates = (rows) => {
  candidatesTable.innerHTML = "";
  if (!rows.length) {
    const emptyRow = document.createElement("tr");
    emptyRow.innerHTML = "<td colspan='9'>No candidates saved yet.</td>";
    candidatesTable.appendChild(emptyRow);
    return;
  }
  rows.forEach((row) => {
    const tr = document.createElement("tr");
    const canStart = row.selection_status === "Selected";
    tr.innerHTML = `
      <td>${row.candidate_id || ""}</td>
      <td>${row.candidate_name || ""}</td>
      <td>${row.position_applied_for || ""}</td>
      <td>${row.interview_status || ""}</td>
      <td>${row.selection_status || ""}</td>
      <td>${row.offer_released || ""}</td>
      <td>${row.joining_date || ""}</td>
      <td>${row.final_status || ""}</td>
      <td>
        ${
          canStart
            ? `<button class="action-btn" type="button" data-candidate="${row.candidate_id}">Start Onboarding</button>`
            : "-"
        }
      </td>
    `;
    candidatesTable.appendChild(tr);
  });
};

const renderAttendance = (rows) => {
  attendanceTable.innerHTML = "";
  if (!rows.length) {
    const emptyRow = document.createElement("tr");
    emptyRow.innerHTML = "<td colspan='8'>No attendance records yet.</td>";
    attendanceTable.appendChild(emptyRow);
    return;
  }
  rows.forEach((row) => {
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td>${row.attendance_id || ""}</td>
      <td>${row.candidate_id || ""}</td>
      <td>${row.attendance_date || ""}</td>
      <td>${row.status || ""}</td>
      <td>${row.check_in_time || ""}</td>
      <td>${row.check_out_time || ""}</td>
      <td>${row.shift || ""}</td>
      <td>${row.notes || ""}</td>
    `;
    attendanceTable.appendChild(tr);
  });
};

const loadCandidates = async () => {
  const response = await fetch(`${apiBase}/candidates`);
  const data = await response.json();
  renderCandidates(data.candidates || []);
};

const loadAttendance = async () => {
  const response = await fetch(`${apiBase}/attendance`);
  const data = await response.json();
  renderAttendance(data.attendance || []);
};

const validateAttendanceForm = () => {
  const requiredFields = attendanceForm.querySelectorAll("[required]");
  for (const field of requiredFields) {
    if (!field.value || !field.value.trim()) {
      return `Please fill ${field.name.replace(/_/g, " ")}.`;
    }
  }
  return "";
};

interviewScheduledInputs.forEach((input) => {
  input.addEventListener("change", updateInterviewDateState);
});

selectionStatusInput.addEventListener("change", () => {
  updateJoiningDateState();
  const enableOnboarding = selectionStatusInput.value === "Selected" && candidateIdInput.value;
  setLocked(!enableOnboarding);
});

categoryInputs.forEach((input) => {
  input.addEventListener("change", updateCategorySections);
});

candidateForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const validationMessage = validateCandidateForm();
  if (validationMessage) {
    showResult(candidateResult, validationMessage, true);
    return;
  }
  candidateStatus.textContent = "Saving...";
  const formData = new FormData(candidateForm);
  const payload = Object.fromEntries(formData.entries());
  try {
    const response = await fetch(`${apiBase}/candidates`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    const data = await response.json();
    if (!response.ok) {
      showResult(candidateResult, data.error || "Submission failed.", true);
      candidateStatus.textContent = "Submission failed";
      return;
    }
    showResult(candidateResult, `Candidate saved. ID: ${data.candidate_id}`);
    candidateStatus.textContent = "Saved";
    setCandidateContext(data.candidate_id);
    setLocked(payload.selection_status !== "Selected");
    await loadCandidates();
    candidateForm.reset();
    updateInterviewDateState();
    updateJoiningDateState();
  } catch (error) {
    showResult(candidateResult, "Server unavailable. Please retry.", true);
    candidateStatus.textContent = "Submission failed";
  }
});

onboardingForm.addEventListener("reset", () => {
  onboardingResult.textContent = "";
});

onboardingForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const validationMessage = validateOnboardingForm();
  if (validationMessage) {
    showResult(onboardingResult, validationMessage, true);
    return;
  }
  const formData = new FormData(onboardingForm);
  const response = await fetch(`${apiBase}/onboarding`, {
    method: "POST",
    body: formData,
  });
  const data = await response.json();
  if (!response.ok) {
    showResult(onboardingResult, data.error || "Onboarding failed.", true);
    return;
  }
  showResult(onboardingResult, "Onboarding submitted successfully.");
  onboardingForm.reset();
  updateCategorySections();
});

attendanceForm.addEventListener("reset", () => {
  attendanceResult.textContent = "";
});

attendanceForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const validationMessage = validateAttendanceForm();
  if (validationMessage) {
    showResult(attendanceResult, validationMessage, true);
    return;
  }
  attendanceStatus.textContent = "Saving...";
  const formData = new FormData(attendanceForm);
  const payload = Object.fromEntries(formData.entries());
  try {
    const response = await fetch(`${apiBase}/attendance`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    const data = await response.json();
    if (!response.ok) {
      showResult(attendanceResult, data.error || "Attendance submission failed.", true);
      attendanceStatus.textContent = "Submission failed";
      return;
    }
    showResult(attendanceResult, `Attendance saved. ID: ${data.attendance_id}`);
    attendanceStatus.textContent = "Saved";
    attendanceForm.reset();
    await loadAttendance();
  } catch (error) {
    showResult(attendanceResult, "Server unavailable. Please retry.", true);
    attendanceStatus.textContent = "Submission failed";
  }
});

candidatesTable.addEventListener("click", (event) => {
  const target = event.target;
  if (target.matches(".action-btn")) {
    const candidateId = target.getAttribute("data-candidate");
    setCandidateContext(candidateId);
    setLocked(false);
    onboardingCard.scrollIntoView({ behavior: "smooth" });
  }
});

refreshTableBtn.addEventListener("click", loadCandidates);
refreshAttendanceBtn.addEventListener("click", loadAttendance);

updateInterviewDateState();
updateJoiningDateState();
updateCategorySections();
setLocked(true);
loadCandidates();
loadAttendance();
