interface Txn {
  external_txn_id: string;
  amount: number | string;
  timestamp: string;
  source: string;
}

export default function TransactionCard({ txn }: { txn: Txn }) {
  return (
    <div className="bg-white rounded-md p-3 text-sm">
      <p className="font-mono text-xs text-ink/50 uppercase">{txn.source}</p>
      <p className="font-mono text-xs text-ink/50">{txn.external_txn_id}</p>
      <p className="font-mono font-medium">₹{txn.amount}</p>
      <p className="text-xs text-ink/60">{new Date(txn.timestamp).toLocaleString()}</p>
    </div>
  );
}
