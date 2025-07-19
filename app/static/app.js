/* global EventSource */
let runId = null;
let eventSource = null;

const qInput  = document.getElementById("query");
const runBtn  = document.getElementById("runBtn");
const report  = document.getElementById("report");
const vList   = document.getElementById("versionList");

/* helper: create a rollback button for a version */
function addVersion(ts) {
  const btn = document.createElement("button");
  const stamp = new Date(ts * 1000).toLocaleString();
  btn.textContent = `Version ${vList.children.length} — ${stamp}`;
  btn.dataset.ts = ts;
  btn.onclick = async () => {
    if (!runId) return;
    const r = await fetch("/rollback", {
      method: "POST",
      headers: {"Content-Type":"application/json"},
      body: JSON.stringify({ run_id: runId, ts: Number(btn.dataset.ts) })
    });
    if (r.ok) {
      const data = await r.json();
      report.textContent = data.report;
    } else {
      alert("Rollback failed");
    }
  };
  vList.prepend(btn);               // newest on top
}

/* STEP 1 — kick off a run */
runBtn.addEventListener("click", async () => {
  const query = qInput.value.trim();
  if (!query) return alert("Enter a question first");

  // Close any previous stream
  if (eventSource) eventSource.close();
  vList.innerHTML = "";
  report.textContent = "Running…";

  const res = await fetch("/start", {
    method : "POST",
    headers: {"Content-Type":"application/json"},
    body   : JSON.stringify({ query })
  });

  if (!res.ok) {
    report.textContent = "Error starting run";
    return;
  }

  ({ run_id: runId } = await res.json());

  /* STEP 2 — listen for the webhook‑triggered report */
  eventSource = new EventSource(`/stream/${runId}`);
  eventSource.onmessage = (e) => {
    const payload = JSON.parse(e.data);          // {report, ts, done?}
    if (payload.report) {
      report.textContent = payload.report;
      if (payload.ts) addVersion(payload.ts);
    }
    if (payload.done) eventSource.close();
  };
  eventSource.onerror = () => {
    console.warn("SSE connection lost");
    eventSource.close();
  };
});

/* STEP 3 — highlight → prompt → edit */
report.addEventListener("mouseup", async () => {
  const sel = window.getSelection().toString();
  if (!sel.trim() || !runId) return;

  const instr = prompt("How should I edit the selection?");
  if (!instr) return;                       // cancelled

  const r = await fetch("/edit", {
    method : "POST",
    headers: {"Content-Type":"application/json"},
    body   : JSON.stringify({
      run_id    : runId,
      original  : sel,
      instruction: instr
    })
  });

  if (r.ok) {
    const data = await r.json();
    report.textContent = data.report;
    addVersion(Date.now() / 1000);
  } else {
    alert("Edit failed");
  }
});