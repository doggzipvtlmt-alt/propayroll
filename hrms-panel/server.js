const path = require("path");
const fs = require("fs");
const express = require("express");
const multer = require("multer");
const ExcelJS = require("exceljs");

const app = express();
const PORT = process.env.PORT || 3000;

const STORAGE_ROOT = path.join(__dirname, process.env.HRMS_STORAGE_DIR || "storage");
const EXCEL_DIR = path.join(STORAGE_ROOT, "excel");
const CANDIDATE_DOCS_DIR = path.join(STORAGE_ROOT, "candidates");
const CANDIDATES_FILE = path.join(EXCEL_DIR, "candidates.xlsx");
const ONBOARDING_FILE = path.join(EXCEL_DIR, "onboarding.xlsx");

const candidateHeaders = [
  "candidate_id",
  "event_type",
  "created_at",
  "candidate_name",
  "mobile",
  "email",
  "position",
  "source",
  "interview_scheduled",
  "interview_date",
  "interview_status",
  "selection_status",
  "offer_released",
  "joining_date",
  "final_status",
  "remarks",
];

const onboardingHeaders = [
  "candidate_id",
  "event_type",
  "category",
  "doc_key",
  "original_filename",
  "stored_path",
  "uploaded_at",
  "uploaded_by",
  "required",
  "verified",
  "metadata",
  "timestamp",
];

const allowedPositions = ["Kitchen Staff", "Helper", "Delivery Boy", "Other"];
const allowedSources = ["Referral", "Walk-in", "Portal", "Recruiter"];
const interviewStatuses = ["Attended", "Not Attended", "Rescheduled"];
const selectionStatuses = ["Selected", "Rejected", "On Hold"];
const finalStatuses = ["Joined", "Dropped", "Not Responding"];

const allowedMimeTypes = ["application/pdf", "image/jpeg", "image/png"];

const ensureDir = (dirPath) => {
  if (!fs.existsSync(dirPath)) {
    fs.mkdirSync(dirPath, { recursive: true });
  }
};

const safePathJoin = (baseDir, targetPath) => {
  const normalized = path.normalize(targetPath).replace(/^\.+/, "");
  const resolved = path.resolve(baseDir, normalized);
  if (!resolved.startsWith(path.resolve(baseDir))) {
    throw new Error("Invalid path");
  }
  return resolved;
};

const formatDate = (date = new Date()) => {
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, "0");
  const day = String(date.getDate()).padStart(2, "0");
  return `${year}-${month}-${day}`;
};

const formatDateId = (date = new Date()) => {
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, "0");
  const day = String(date.getDate()).padStart(2, "0");
  return `${year}${month}${day}`;
};

const ensureWorkbook = async (filePath, sheetName, headers) => {
  ensureDir(path.dirname(filePath));
  if (!fs.existsSync(filePath)) {
    const workbook = new ExcelJS.Workbook();
    const worksheet = workbook.addWorksheet(sheetName);
    worksheet.addRow(headers);
    await workbook.xlsx.writeFile(filePath);
  }
};

const readRows = async (filePath, sheetName) => {
  await ensureWorkbook(filePath, sheetName, sheetName === "Candidates" ? candidateHeaders : onboardingHeaders);
  const workbook = new ExcelJS.Workbook();
  await workbook.xlsx.readFile(filePath);
  const worksheet = workbook.getWorksheet(sheetName);
  if (!worksheet) {
    return [];
  }
  const headers = [];
  worksheet.getRow(1).eachCell((cell, colNumber) => {
    headers[colNumber - 1] = String(cell.value).trim();
  });
  const rows = [];
  worksheet.eachRow((row, rowNumber) => {
    if (rowNumber === 1) return;
    const rowData = {};
    headers.forEach((header, index) => {
      rowData[header] = row.getCell(index + 1).value ?? "";
    });
    rows.push(rowData);
  });
  return rows;
};

const appendRow = async (filePath, sheetName, headers, data) => {
  await ensureWorkbook(filePath, sheetName, headers);
  const workbook = new ExcelJS.Workbook();
  await workbook.xlsx.readFile(filePath);
  const worksheet = workbook.getWorksheet(sheetName);
  const row = headers.map((header) => (data[header] !== undefined ? data[header] : ""));
  worksheet.addRow(row);
  await workbook.xlsx.writeFile(filePath);
};

const getCandidateIdSequence = async (dateId) => {
  const rows = await readRows(CANDIDATES_FILE, "Candidates");
  const sequences = rows
    .filter((row) => row.candidate_id && String(row.candidate_id).includes(dateId))
    .map((row) => {
      const parts = String(row.candidate_id).split("-");
      return Number(parts[2]) || 0;
    });
  const maxSeq = sequences.length ? Math.max(...sequences) : 0;
  return maxSeq + 1;
};

const validateCandidatePayload = (payload) => {
  const errors = {};
  const name = String(payload.candidate_name || "").trim();
  const mobile = String(payload.mobile || "").trim();
  const email = String(payload.email || "").trim();
  const position = payload.position;
  const source = payload.source;
  const interviewScheduled = payload.interview_scheduled;
  const interviewDate = payload.interview_date;
  const interviewStatus = payload.interview_status;
  const selectionStatus = payload.selection_status;
  const offerReleased = payload.offer_released;
  const joiningDate = payload.joining_date;
  const finalStatus = payload.final_status;
  const remarks = payload.remarks || "";

  if (name.length < 3) {
    errors.candidate_name = "Candidate name must be at least 3 characters.";
  }

  if (!/^\d{10}$/.test(mobile)) {
    errors.mobile = "Mobile number must be 10 digits.";
  }

  if (!/^\S+@\S+\.\S+$/.test(email)) {
    errors.email = "Email must be valid.";
  }

  if (!allowedPositions.includes(position)) {
    errors.position = "Position Applied For is required.";
  }

  if (!allowedSources.includes(source)) {
    errors.source = "Source is required.";
  }

  if (!["Yes", "No"].includes(interviewScheduled)) {
    errors.interview_scheduled = "Interview Scheduled is required.";
  }

  if (interviewScheduled === "Yes" && !interviewDate) {
    errors.interview_date = "Interview Date is required when interview is scheduled.";
  }

  if (!interviewStatuses.includes(interviewStatus)) {
    errors.interview_status = "Interview Status is required.";
  }

  if (!selectionStatuses.includes(selectionStatus)) {
    errors.selection_status = "Selection Status is required.";
  }

  if (!["Yes", "No"].includes(offerReleased)) {
    errors.offer_released = "Offer Released is required.";
  }

  if (selectionStatus === "Selected" && !joiningDate) {
    errors.joining_date = "Joining Date is required when selection status is Selected.";
  }

  if (!finalStatuses.includes(finalStatus)) {
    errors.final_status = "Final Status is required.";
  }

  if (remarks && remarks.length > 500) {
    errors.remarks = "Remarks cannot exceed 500 characters.";
  }

  return {
    errors,
    clean: {
      candidate_name: name,
      mobile,
      email,
      position,
      source,
      interview_scheduled: interviewScheduled,
      interview_date: interviewScheduled === "Yes" ? interviewDate : "",
      interview_status: interviewStatus,
      selection_status: selectionStatus,
      offer_released: offerReleased,
      joining_date: selectionStatus === "Selected" ? joiningDate : "",
      final_status: finalStatus,
      remarks: remarks || "",
    },
  };
};

const getCandidateSummary = (rows) => {
  const summary = new Map();
  rows.forEach((row) => {
    if (!row.candidate_id) return;
    summary.set(row.candidate_id, row);
  });
  return Array.from(summary.values());
};

const getCandidateById = async (candidateId) => {
  const rows = await readRows(CANDIDATES_FILE, "Candidates");
  const summary = getCandidateSummary(rows);
  return summary.find((row) => row.candidate_id === candidateId);
};

const getOnboardingState = (rows) => {
  let category = "";
  let flags = { hasPg: false, experienced: false };
  let selfDeclaration = null;
  const uploads = [];

  rows.forEach((row) => {
    if (row.event_type === "CATEGORY_SELECTED") {
      category = row.category || "";
      try {
        flags = JSON.parse(row.metadata || "{}") || flags;
      } catch (error) {
        flags = { hasPg: false, experienced: false };
      }
    }
    if (row.event_type === "SELF_DECLARATION") {
      try {
        selfDeclaration = JSON.parse(row.metadata || "{}");
      } catch (error) {
        selfDeclaration = null;
      }
    }
    if (row.event_type === "DOC_UPLOADED") {
      uploads.push(row);
    }
  });

  return { category, flags, selfDeclaration, uploads };
};

const summarizeUploads = (uploads) => {
  const map = {};
  uploads.forEach((upload) => {
    const key = upload.doc_key;
    if (!key) return;
    if (!map[key]) {
      map[key] = [];
    }
    map[key].push(upload);
  });
  return map;
};

const requiredChecklist = ({ category, flags, uploads, selfDeclaration }) => {
  const uploadMap = summarizeUploads(uploads);
  const checklist = [];
  const addItem = (key, label, required = true, statusOverride = null, detail = "") => {
    const uploadedCount = (uploadMap[key] || []).length;
    const isUploaded = uploadedCount > 0;
    const status = statusOverride || (isUploaded ? "Uploaded" : "Missing");
    checklist.push({ key, label, required, status, uploadedCount, detail });
  };

  if (!category) {
    return { checklist, missing: ["Employee category is not selected."] };
  }

  const missing = [];

  if (category === "Formally Educated") {
    addItem("aadhaar_card", "Aadhaar Card", true);
    addItem("pan_card", "PAN Card", true);
    addItem("address_proof", "Address Proof", true);
    addItem("edu_10th", "10th Marksheet", true);
    addItem("edu_12th", "12th Marksheet", true);
    addItem("edu_grad", "Graduation/Diploma", true);
    if (flags.hasPg) {
      addItem("edu_pg", "Post-Graduation", true);
    } else {
      addItem("edu_pg", "Post-Graduation", false, uploadMap.edu_pg ? "Uploaded" : "Optional");
    }
    addItem("resume", "Resume/CV", true);
    addItem("passport_photo", "Passport Photo", true);

    const chequeCount = (uploadMap.bank_cheque || []).length;
    const passbookCount = (uploadMap.bank_passbook || []).length;
    const bankStatus = chequeCount + passbookCount > 0 ? "Uploaded" : "Missing";
    checklist.push({
      key: "bank_details",
      label: "Bank Details (Cancelled Cheque or Passbook)",
      required: true,
      status: bankStatus,
      uploadedCount: chequeCount + passbookCount,
      detail: "Upload at least one of: Cancelled Cheque or Passbook.",
    });

    addItem("medical_fitness", "Medical Fitness Certificate", true);

    if (flags.experienced) {
      addItem("offer_letter", "Offer Letter", true);
      addItem("relieving_letter", "Relieving/Experience Letter", true);
      const salaryCount = (uploadMap.salary_slip || []).length;
      const status = salaryCount >= 3 ? "Uploaded" : "Missing";
      checklist.push({
        key: "salary_slip",
        label: "Last 3 Salary Slips",
        required: true,
        status,
        uploadedCount: salaryCount,
        detail: "Upload at least 3 salary slips.",
      });
    }
  }

  if (category === "Non-Formally Educated") {
    addItem("aadhaar_card", "Aadhaar Card", true);
    addItem("address_proof", "Address Proof", true);
    addItem("passport_photo", "Passport Photo", true);
    addItem("bank_statement", "Bank Details (Passbook/Account Statement)", true);
    addItem("self_declaration_form", "Self-Declaration Form", true);

    const hasSelfFields =
      selfDeclaration &&
      selfDeclaration.name &&
      selfDeclaration.age &&
      selfDeclaration.address &&
      selfDeclaration.skill &&
      selfDeclaration.willingness &&
      selfDeclaration.signature;

    checklist.push({
      key: "self_declaration_fields",
      label: "Self-Declaration Fields",
      required: true,
      status: hasSelfFields ? "Completed" : "Missing",
      uploadedCount: 0,
      detail: "Complete the self-declaration form fields.",
    });

    const skillProofOptions = [
      "ngo_letter",
      "employer_letter",
      "skill_assessment",
      "trial_evaluation",
    ];
    const skillProofCount = skillProofOptions.reduce((total, key) => total + (uploadMap[key] || []).length, 0);
    checklist.push({
      key: "skill_proof",
      label: "Skill/Experience Proof (any one)",
      required: true,
      status: skillProofCount > 0 ? "Uploaded" : "Missing",
      uploadedCount: skillProofCount,
      detail: "Upload at least one proof: NGO Letter, Employer Letter, Skill Assessment Sheet, or Internal Trial Evaluation.",
    });

    addItem("medical_fitness", "Medical Fitness Certificate (Optional)", false, uploadMap.medical_fitness ? "Uploaded" : "Optional");
  }

  checklist.forEach((item) => {
    if (!item.required) {
      return;
    }
    if (["Missing", "Optional"].includes(item.status)) {
      missing.push(`${item.label} is missing.`);
    }
  });

  if (category === "Formally Educated") {
    if ((uploadMap.bank_cheque || []).length + (uploadMap.bank_passbook || []).length === 0) {
      missing.push("Bank Details (Cancelled Cheque or Passbook) are missing.");
    }
    if (flags.experienced && (uploadMap.salary_slip || []).length < 3) {
      missing.push("At least 3 salary slips are required.");
    }
  }

  if (category === "Non-Formally Educated") {
    const skillProofOptions = [
      "ngo_letter",
      "employer_letter",
      "skill_assessment",
      "trial_evaluation",
    ];
    const skillProofCount = skillProofOptions.reduce((total, key) => total + (uploadMap[key] || []).length, 0);
    if (skillProofCount === 0) {
      missing.push("At least one skill/experience proof document is required.");
    }
    const hasSelfFields =
      selfDeclaration &&
      selfDeclaration.name &&
      selfDeclaration.age &&
      selfDeclaration.address &&
      selfDeclaration.skill &&
      selfDeclaration.willingness &&
      selfDeclaration.signature;
    if (!hasSelfFields) {
      missing.push("Self-declaration fields are incomplete.");
    }
  }

  return { checklist, missing };
};

ensureDir(STORAGE_ROOT);
ensureDir(EXCEL_DIR);
ensureDir(CANDIDATE_DOCS_DIR);

app.use(express.json());
app.use(express.urlencoded({ extended: true }));
const publicDir = path.join(__dirname, "public");
app.use(express.static(publicDir));

app.get("/candidate/:id", (req, res) => {
  res.sendFile(path.join(publicDir, "candidate.html"));
});

const upload = multer({
  limits: { fileSize: 5 * 1024 * 1024 },
  fileFilter: (req, file, cb) => {
    if (!allowedMimeTypes.includes(file.mimetype)) {
      return cb(new Error("Only PDF, JPG, or PNG files are allowed."));
    }
    return cb(null, true);
  },
  storage: multer.diskStorage({
    destination: (req, file, cb) => {
      const candidateId = req.params.id;
      const category = String(req.body.category || "general");
      const safeCategory = category.replace(/[^a-zA-Z0-9_-]/g, "_");
      const dest = safePathJoin(CANDIDATE_DOCS_DIR, path.join(candidateId, "documents", safeCategory));
      ensureDir(dest);
      cb(null, dest);
    },
    filename: (req, file, cb) => {
      const safeName = path.basename(file.originalname).replace(/\s+/g, "_");
      cb(null, `${Date.now()}_${safeName}`);
    },
  }),
});

app.get("/api/candidates", async (req, res) => {
  const rows = await readRows(CANDIDATES_FILE, "Candidates");
  const summary = getCandidateSummary(rows);
  res.json({ data: summary });
});

app.get("/api/candidates/:id", async (req, res) => {
  const candidateId = req.params.id;
  const candidate = await getCandidateById(candidateId);
  if (!candidate) {
    return res.status(404).json({ error: "Candidate not found." });
  }
  const onboardingRows = await readRows(ONBOARDING_FILE, "Onboarding");
  const candidateOnboardingRows = onboardingRows.filter((row) => row.candidate_id === candidateId);
  const onboardingState = getOnboardingState(candidateOnboardingRows);
  const { checklist, missing } = requiredChecklist(onboardingState);

  return res.json({
    candidate,
    onboarding: {
      category: onboardingState.category,
      flags: onboardingState.flags,
      selfDeclaration: onboardingState.selfDeclaration,
      checklist,
      missing,
    },
  });
});

app.post("/api/candidates", async (req, res) => {
  const { errors, clean } = validateCandidatePayload(req.body);
  if (Object.keys(errors).length > 0) {
    return res.status(400).json({ errors });
  }

  const today = formatDate();
  const candidateRows = await readRows(CANDIDATES_FILE, "Candidates");
  const duplicate = candidateRows.find(
    (row) =>
      row.event_type === "CANDIDATE_CREATED" &&
      row.mobile === clean.mobile &&
      row.position === clean.position &&
      String(row.created_at).startsWith(today)
  );

  if (duplicate) {
    return res.status(409).json({ error: "Duplicate candidate for the same position and date." });
  }

  const dateId = formatDateId();
  const sequence = await getCandidateIdSequence(dateId);
  const candidateId = `CAND-${dateId}-${String(sequence).padStart(4, "0")}`;

  const record = {
    candidate_id: candidateId,
    event_type: "CANDIDATE_CREATED",
    created_at: new Date().toISOString(),
    ...clean,
  };

  await appendRow(CANDIDATES_FILE, "Candidates", candidateHeaders, record);
  res.status(201).json({ candidate_id: candidateId });
});

app.post("/api/candidates/:id/onboarding/category", async (req, res) => {
  const candidateId = req.params.id;
  const candidate = await getCandidateById(candidateId);
  if (!candidate) {
    return res.status(404).json({ error: "Candidate not found." });
  }
  if (candidate.selection_status !== "Selected") {
    return res.status(403).json({ error: "Onboarding is only allowed for Selected candidates." });
  }
  const category = req.body.category;
  const flags = {
    hasPg: Boolean(req.body.has_pg),
    experienced: Boolean(req.body.experienced),
  };

  if (!["Formally Educated", "Non-Formally Educated"].includes(category)) {
    return res.status(400).json({ error: "Employee category is required." });
  }

  await appendRow(ONBOARDING_FILE, "Onboarding", onboardingHeaders, {
    candidate_id: candidateId,
    event_type: "CATEGORY_SELECTED",
    category,
    metadata: JSON.stringify(flags),
    timestamp: new Date().toISOString(),
  });

  res.json({ status: "ok" });
});

app.post("/api/candidates/:id/onboarding/self-declaration", async (req, res) => {
  const candidateId = req.params.id;
  const candidate = await getCandidateById(candidateId);
  if (!candidate) {
    return res.status(404).json({ error: "Candidate not found." });
  }
  if (candidate.selection_status !== "Selected") {
    return res.status(403).json({ error: "Onboarding is only allowed for Selected candidates." });
  }
  const fields = {
    name: String(req.body.name || "").trim(),
    age: String(req.body.age || "").trim(),
    address: String(req.body.address || "").trim(),
    skill: String(req.body.skill || "").trim(),
    willingness: String(req.body.willingness || "").trim(),
    signature: String(req.body.signature || "").trim(),
  };

  const missing = Object.entries(fields)
    .filter(([, value]) => !value)
    .map(([key]) => key);

  if (missing.length > 0) {
    return res.status(400).json({ error: `Missing fields: ${missing.join(", ")}` });
  }

  await appendRow(ONBOARDING_FILE, "Onboarding", onboardingHeaders, {
    candidate_id: candidateId,
    event_type: "SELF_DECLARATION",
    metadata: JSON.stringify(fields),
    timestamp: new Date().toISOString(),
  });

  res.json({ status: "ok" });
});

app.post("/api/candidates/:id/upload", upload.single("file"), async (req, res) => {
  const candidateId = req.params.id;
  const candidate = await getCandidateById(candidateId);
  if (!candidate) {
    return res.status(404).json({ error: "Candidate not found." });
  }
  if (candidate.selection_status !== "Selected") {
    return res.status(403).json({ error: "Onboarding is only allowed for Selected candidates." });
  }
  const docKey = String(req.body.doc_key || "").trim();
  const category = String(req.body.category || "general");
  const required = String(req.body.required || "false") === "true";

  if (!docKey) {
    return res.status(400).json({ error: "doc_key is required." });
  }

  if (!req.file) {
    return res.status(400).json({ error: "File is required." });
  }

  const storedPath = path.relative(STORAGE_ROOT, req.file.path);

  await appendRow(ONBOARDING_FILE, "Onboarding", onboardingHeaders, {
    candidate_id: candidateId,
    event_type: "DOC_UPLOADED",
    category,
    doc_key: docKey,
    original_filename: req.file.originalname,
    stored_path: storedPath,
    uploaded_at: new Date().toISOString(),
    uploaded_by: "HR",
    required,
    verified: false,
    timestamp: new Date().toISOString(),
  });

  res.json({ status: "uploaded" });
});

app.post("/api/candidates/:id/onboarding/submit", async (req, res) => {
  const candidateId = req.params.id;
  const candidate = await getCandidateById(candidateId);
  if (!candidate) {
    return res.status(404).json({ error: "Candidate not found." });
  }
  if (candidate.selection_status !== "Selected") {
    return res.status(403).json({ error: "Onboarding is only allowed for Selected candidates." });
  }
  const verified = Boolean(req.body.verified);

  const onboardingRows = await readRows(ONBOARDING_FILE, "Onboarding");
  const candidateOnboardingRows = onboardingRows.filter((row) => row.candidate_id === candidateId);
  const onboardingState = getOnboardingState(candidateOnboardingRows);
  const { missing } = requiredChecklist(onboardingState);

  if (!verified) {
    missing.push("Verification checkbox must be checked.");
  }

  if (missing.length > 0) {
    return res.status(400).json({ error: "Onboarding incomplete.", missing });
  }

  await appendRow(ONBOARDING_FILE, "Onboarding", onboardingHeaders, {
    candidate_id: candidateId,
    event_type: "ONBOARDING_SUBMITTED",
    verified: true,
    metadata: JSON.stringify({ final_status: "COMPLETED" }),
    timestamp: new Date().toISOString(),
  });

  res.json({ status: "submitted" });
});

app.get("/api/candidates/:id/documents", async (req, res) => {
  const candidateId = req.params.id;
  const onboardingRows = await readRows(ONBOARDING_FILE, "Onboarding");
  const docs = onboardingRows.filter((row) => row.candidate_id === candidateId && row.event_type === "DOC_UPLOADED");
  res.json({ documents: docs });
});

app.use((err, req, res, next) => {
  if (err) {
    return res.status(400).json({ error: err.message || "Upload failed." });
  }
  return next();
});

app.listen(PORT, () => {
  console.log(`HRMS panel running on port ${PORT}`);
});
