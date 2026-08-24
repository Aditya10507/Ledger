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
      // Surfaces the specific, row-level error from the backend (FR-5) rather than a generic message.
      const detail = err?.response?.data?.detail;
      setError(typeof detail === "object" ? detail.message : detail || "Upload failed. Please check your files.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-2xl mx-auto p-8">
      <h1 className="text-xl font-semibold mb-6">New Reconciliation Run</h1>

      <div className="grid grid-cols-2 gap-4 mb-6">
        <FileDropZone label="Ledger CSV" file={ledgerFile} onSelect={setLedgerFile} />
        <FileDropZone label="Settlement CSV" file={settlementFile} onSelect={setSettlementFile} />
      </div>

      {error && <p className="text-critical text-sm mb-4">{error}</p>}

      <button
        disabled={!ledgerFile || !settlementFile || loading}
        onClick={handleSubmit}
        className="bg-primary text-white rounded-md px-4 py-2 text-sm font-medium disabled:opacity-40"
      >
        {loading ? "Running reconciliation…" : "Run Reconciliation"}
      </button>
    </div>
  );
}
