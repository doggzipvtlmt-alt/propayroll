const toast = document.getElementById("toast");
const candidateSummary = document.getElementById("candidateSummary");
const lockOverlay = document.getElementById("lockOverlay");
const onboardingStatus = document.getElementById("onboardingStatus");
const categoryForm = document.getElementById("categoryForm");
const formalOptions = document.getElementById("formalOptions");
const checklistContainer = document.getElementById("checklist");
const verificationCheck = document.getElementById("verificationCheck");
const finalSubmit = document.getElementById("finalSubmit");
const finalErrors = document.getElementById("finalErrors");
const selfDeclarationSection = document.getElementById("selfDeclarationSection");
const selfDeclarationForm = document.getElementById("selfDeclarationForm");

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

const getCandidateId = () => {
  const parts = window.location.pathname.split("/");
  return parts[parts.length - 1];
};

const renderSummary = (candidate) => {
  candidateSummary.innerHTML = "";
  const fields = {
    "Candidate ID": candidate.candidate_id,
    Name: candidate.candidate_name,
    Mobile: candidate.mobile,
    Email: candidate.email,
    Position: candidate.position,
    "Selection Status": candidate.selection_status,
    "Final Status": candidate.final_status,
  };
  Object.entries(fields).forEach(([label, value]) => {
    const div = document.createElement("div");
    div.innerHTML = `<strong>${label}:</strong> ${value || "-"}`;
    candidateSummary.appendChild(div);
  });
};

const renderChecklist = (checklist, category) => {
  checklistContainer.innerHTML = "";
  checklist.forEach((item) => {
    const row = document.createElement("div");
    row.className = "checklist-item";
    const statusClass = item.status === "Uploaded" || item.status === "Completed" ? "uploaded" : "missing";
    row.innerHTML = `
      <div>
        <div><strong>${item.label}</strong></div>
        <small>${item.detail || ""}</small>
      </div>
      <div>
        <div class="status ${statusClass}">${item.status}</div>
      </div>
    `;

    if (item.key !== "self_declaration_fields" && item.key !== "skill_proof" && item.key !== "bank_details") {
      const uploadForm = document.createElement("form");
      uploadForm.innerHTML = `
        <input type="file" name="file" />
        <button type="submit">Upload</button>
      `;
      uploadForm.addEventListener("submit", (event) => handleUpload(event, item.key, item.required, category));
      row.querySelector("div:last-child").appendChild(uploadForm);
    }

    if (item.key === "bank_details" && category === "Formally Educated") {
      const bankWrapper = document.createElement("div");
      [
        { key: "bank_cheque", label: "Cancelled Cheque" },
        { key: "bank_passbook", label: "Passbook First Page" },
      ].forEach((doc) => {
        const form = document.createElement("form");
        form.innerHTML = `
          <div>${doc.label}</div>
          <input type="file" name="file" />
          <button type="submit">Upload</button>
        `;
        form.addEventListener("submit", (event) => handleUpload(event, doc.key, true, category));
        bankWrapper.appendChild(form);
      });
      row.querySelector("div:last-child").appendChild(bankWrapper);
    }

    if (item.key === "skill_proof" && category === "Non-Formally Educated") {
      const skillWrapper = document.createElement("div");
      [
        { key: "ngo_letter", label: "NGO Letter" },
        { key: "employer_letter", label: "Employer Letter" },
        { key: "skill_assessment", label: "Skill Assessment Sheet" },
        { key: "trial_evaluation", label: "Internal Trial Evaluation" },
      ].forEach((doc) => {
        const form = document.createElement("form");
        form.innerHTML = `
          <div>${doc.label}</div>
          <input type="file" name="file" />
          <button type="submit">Upload</button>
        `;
        form.addEventListener("submit", (event) => handleUpload(event, doc.key, true, category));
        skillWrapper.appendChild(form);
      });
      row.querySelector("div:last-child").appendChild(skillWrapper);
    }

    checklistContainer.appendChild(row);
  });
};

const handleUpload = async (event, docKey, required, category) => {
  event.preventDefault();
  const form = event.target;
  const fileInput = form.querySelector("input[type=file]");
  if (!fileInput.files.length) {
    showToast("Please select a file.", true);
    return;
  }
  const data = new FormData();
  data.append("file", fileInput.files[0]);
  data.append("doc_key", docKey);
  data.append("category", category || "general");
  data.append("required", required ? "true" : "false");

  const response = await fetch(`/api/candidates/${getCandidateId()}/upload`, {
    method: "POST",
    body: data,
  });

  if (!response.ok) {
    const payload = await response.json();
    showToast(payload.error || "Upload failed.", true);
    return;
  }

  showToast("Document uploaded.");
  await loadCandidate();
};

const loadCandidate = async () => {
  const response = await fetch(`/api/candidates/${getCandidateId()}`);
  if (!response.ok) {
    showToast("Candidate not found.", true);
    return;
  }
  const data = await response.json();
  renderSummary(data.candidate);
  const isSelected = data.candidate.selection_status === "Selected";
  lockOverlay.classList.toggle("hidden", isSelected);
  onboardingStatus.textContent = data.onboarding.category ? data.onboarding.category : "Pending";
  categoryForm.category.value = data.onboarding.category || "";
  formalOptions.classList.toggle("hidden", data.onboarding.category !== "Formally Educated");
  categoryForm.has_pg.checked = Boolean(data.onboarding.flags?.hasPg);
  categoryForm.experienced.checked = Boolean(data.onboarding.flags?.experienced);
  selfDeclarationSection.classList.toggle("hidden", data.onboarding.category !== "Non-Formally Educated");
  if (data.onboarding.selfDeclaration) {
    Object.entries(data.onboarding.selfDeclaration).forEach(([key, value]) => {
      const field = selfDeclarationForm.querySelector(`[name="${key}"]`);
      if (field) {
        field.value = value;
      }
    });
  }
  renderChecklist(data.onboarding.checklist, data.onboarding.category);
  finalSubmit.disabled = data.onboarding.missing.length > 0;
  finalErrors.textContent = data.onboarding.missing.join(" ");
};

categoryForm.addEventListener("change", () => {
  formalOptions.classList.toggle("hidden", categoryForm.category.value !== "Formally Educated");
});

categoryForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  setError("category", "");
  if (!categoryForm.category.value) {
    setError("category", "Employee category is required.");
    return;
  }

  const payload = {
    category: categoryForm.category.value,
    has_pg: categoryForm.has_pg.checked,
    experienced: categoryForm.experienced.checked,
  };

  const response = await fetch(`/api/candidates/${getCandidateId()}/onboarding/category`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    const data = await response.json();
    setError("category", data.error || "Failed to save category.");
    return;
  }

  showToast("Category saved.");
  await loadCandidate();
});

selfDeclarationForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  setError("self_declaration", "");
  const payload = Object.fromEntries(new FormData(selfDeclarationForm));
  const response = await fetch(`/api/candidates/${getCandidateId()}/onboarding/self-declaration`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    const data = await response.json();
    setError("self_declaration", data.error || "Failed to save self-declaration.");
    return;
  }

  showToast("Self-declaration saved.");
  await loadCandidate();
});

finalSubmit.addEventListener("click", async () => {
  finalErrors.textContent = "";
  const response = await fetch(`/api/candidates/${getCandidateId()}/onboarding/submit`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ verified: verificationCheck.checked }),
  });

  if (!response.ok) {
    const data = await response.json();
    finalErrors.textContent = data.missing ? data.missing.join(" ") : data.error;
    showToast("Onboarding submission failed.", true);
    return;
  }

  showToast("Onboarding submitted.");
  verificationCheck.checked = false;
  await loadCandidate();
});

loadCandidate();
