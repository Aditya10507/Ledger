export default function FileDropZone({
  label,
  file,
  onSelect,
}: {
  label: string;
  file: File | null;
  onSelect: (file: File) => void;
}) {
  return (
    <label className="block border-2 border-dashed border-ink/20 rounded-lg p-6 text-center cursor-pointer hover:border-primary transition-colors">
      <input
        type="file"
        accept=".csv"
        className="hidden"
        onChange={(e) => e.target.files?.[0] && onSelect(e.target.files[0])}
      />
      <p className="text-sm font-medium">{label}</p>
      <p className="text-xs text-ink/50 mt-1">{file ? file.name : "Click or drag a .csv file"}</p>
    </label>
  );
}
