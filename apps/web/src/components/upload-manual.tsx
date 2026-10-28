"use client";

import { useEffect, useState } from "react";
import { apiUrl } from "@/lib/api";
import { UPLOAD_LIMIT_BYTES, UPLOAD_LIMIT_NOTE } from "@/lib/image";
import { AskUploaded } from "@/components/ask-uploaded";

type Device = { id: string; manufacturer: string; model: string };

export function UploadManual() {
  const [devices, setDevices] = useState<Device[]>([]);
  const [deviceId, setDeviceId] = useState("");
  const [workspace, setWorkspace] = useState("demo");
  const [busy, setBusy] = useState(false);
  const [result, setResult] = useState<{ doc_id?: string; pages?: number; low_text_pages?: number; note?: string; error?: string; detail?: string } | null>(null);
  const [fileName, setFileName] = useState("");
  useEffect(() => { fetch(apiUrl("/v1/devices")).then((r) => r.json()).then(setDevices).catch(() => {}); }, []);
  async function upload(file: File) {
    if (file.size > UPLOAD_LIMIT_BYTES) { setResult({ error: UPLOAD_LIMIT_NOTE }); return; }
    setBusy(true); setResult(null); setFileName(file.name);
    const fd = new FormData(); fd.append("file", file);
    const q = new URLSearchParams({ workspace, ...(deviceId ? { device_id: deviceId } : {}) });
    try { const r = await fetch(apiUrl(`/v1/upload-manual?${q}`), { method: "POST", body: fd }); const j = await r.json(); setResult(r.ok ? j : { error: j.detail ?? `upload failed (${r.status})` }); }
    catch { setResult({ error: "upload failed" }); } finally { setBusy(false); }
  }
  return (
    <div className="space-y-3">
      <div className="grid gap-3 sm:grid-cols-2">
        <label className="block text-sm"><span className="mb-1 block text-fg-muted">Workspace</span><input className="inp" value={workspace} onChange={(e) => setWorkspace(e.target.value)} /></label>
        <label className="block text-sm"><span className="mb-1 block text-fg-muted">Tag to a device (optional)</span>
          <select className="inp" value={deviceId} onChange={(e) => setDeviceId(e.target.value)}><option value="">none</option>{devices.map((d) => <option key={d.id} value={d.id}>{d.manufacturer} {d.model}</option>)}</select></label>
      </div>
      <label className="btn-primary cursor-pointer">{busy ? "Indexing…" : "Upload a manual (PDF)"}<input type="file" accept="application/pdf" className="sr-only" onChange={(e) => e.target.files?.[0] && upload(e.target.files[0])} disabled={busy} /></label>
      {result && (result.error ? <p className="text-sm text-stop">{result.error}</p> : <p className="text-sm text-ok">Indexed {result.pages} pages of {fileName}{result.low_text_pages ? `; ${result.low_text_pages} pages have no extractable text and are skipped` : ""}.</p>)}
      {result?.doc_id && <AskUploaded docId={result.doc_id} title={fileName} />}
    </div>
  );
}
