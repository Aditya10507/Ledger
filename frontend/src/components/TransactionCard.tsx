interface Txn {
  external_txn_id: string;
  amount: number | string;
  timestamp: string;
  source: string;
}

export default function TransactionCard({ txn }: { txn: Txn }) {
  return (
    <div className="bg-panel border border-line rounded-sm p-3">
      <p className="font-mono text-[10px] text-ink-faint uppercase">{txn.source}</p>
      <p className="font-mono text-xs text-ink-muted">{txn.external_txn_id}</p>
      <p className="font-mono font-medium text-ink mt-1">₹{txn.amount}</p>
      <p className="text-xs text-ink-faint mt-1">
        {new Date(txn.timestamp).toLocaleString()}
      </p>
    </div>
  );
}
