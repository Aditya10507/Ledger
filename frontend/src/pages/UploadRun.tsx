import { useState } from "react";
import { useNavigate } from "react-router-dom";
import client from "../api/client";
import FileDropZone from "../components/FileDropZone";

export default function UploadRun() {
  const [ledgerFile, setLedgerFile] = useState<File | null>(null);
  const [settlementFile, setSettlementFile] = useState<File | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleSubmit = async () => {
    if (!ledgerFile || !settlementFile) return;
    setLoading(true);
    setError(null);

    const formData = new FormData();
    formData.append("ledger_file", ledgerFile);
    formData.append("settlement_file", settlementFile);

    try {
      const { data } = await client.post("/reconciliation/runs", formData);
      navigate(`/runs/${data.run_id}`);
    } catch (err: any) {
      const detail = err?.response?.data?.detail;
      setError(typeof detail === "object" ? detail.message : detail || "Upload failed. Please check your files.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-2xl mx-auto p-8">
      <p className="text-xs uppercase tracking-widest text-ink-muted mb-1">New Reconciliation</p>
      <h1 className="font-display text-2xl font-semibold text-ink mb-8">Submit Documents</h1>

      <div className="grid grid-cols-2 gap-4 mb-6">
        <FileDropZone label="Ledger CSV" file={ledgerFile} onSelect={setLedgerFile} />
        <FileDropZone label="Settlement CSV" file={settlementFile} onSelect={setSettlementFile} />
      </div>

      {error && (
        <p role="alert" className="text-stamp-red text-sm mb-4">
          {error}
        </p>
      )}

      <button
        disabled={!ledgerFile || !settlementFile || loading}
        onClick={handleSubmit}
        className="bg-ledger text-white rounded-sm px-5 py-2.5 text-sm font-medium disabled:opacity-40 hover:bg-ledger-dark transition-colors"
      >
        {loading ? "Running reconciliation…" : "Run Reconciliation"}
      </button>

      <p className="text-xs text-ink-faint mt-4">
        Both files must be .csv with matching column headers. Maximum file size applies per your
        server configuration.
      </p>
    </div>
  );
}
