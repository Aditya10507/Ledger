import { useRef, useState } from "react";

export default function FileDropZone({
  label,
  file,
  onSelect,
}: {
  label: string;
  file: File | null;
  onSelect: (file: File) => void;
}) {
  const inputRef = useRef<HTMLInputElement>(null);
  const [dragging, setDragging] = useState(false);

  const openPicker = () => {
    inputRef.current?.click();
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selected = e.target.files?.[0];
    if (selected) onSelect(selected);
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setDragging(true);
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    setDragging(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setDragging(false);
    const dropped = e.dataTransfer.files?.[0];
    if (dropped) onSelect(dropped);
  };

  return (
    <div
      onClick={openPicker}
      onKeyDown={(e) => {
        if (e.key === "Enter" || e.key === " ") {
          e.preventDefault();
          openPicker();
        }
      }}
      onDragOver={handleDragOver}
      onDragLeave={handleDragLeave}
      onDrop={handleDrop}
      role="button"
      tabIndex={0}
      aria-label={label}
      className={`block border-2 border-dashed rounded-sm p-8 text-center cursor-pointer transition-all ${
        dragging
          ? "border-ledger bg-ledger-light scale-[1.02]"
          : file
          ? "border-ledger bg-ledger-light"
          : "border-line hover:border-ledger/50 bg-panel"
      }`}
    >
      <input
        ref={inputRef}
        type="file"
        className="hidden"
        style={{ position: "absolute", left: "-9999px" }}
        onChange={handleChange}
      />
      <p className="text-xs uppercase tracking-wide text-ink-muted mb-2">{label}</p>
      {file ? (
        <p className="font-mono text-sm text-ledger-dark font-medium">{file.name}</p>
      ) : (
        <p className="text-sm text-ink-faint">
          {dragging ? "Drop file here" : "Click to select a file"}
        </p>
      )}
    </div>
  );
}
