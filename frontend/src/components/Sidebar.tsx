import { Link, useLocation, useNavigate } from "react-router-dom";

const NAV_ITEMS = [
  { label: "Dashboard", path: "/dashboard" },
  { label: "New Run", path: "/runs/new" },
];

export default function Sidebar() {
  const location = useLocation();
  const navigate = useNavigate();
  const role = localStorage.getItem("ledger_role");

  const handleLogout = () => {
    localStorage.removeItem("ledger_token");
    localStorage.removeItem("ledger_role");
    navigate("/login");
  };

  return (
    <nav
      aria-label="Main navigation"
      className="w-60 shrink-0 bg-ledger-dark min-h-screen p-5 flex flex-col text-paper"
    >
      <div className="mb-10 px-2">
        <p className="font-display font-semibold text-xl tracking-tight">Ledger</p>
        <p className="font-mono text-[10px] uppercase tracking-widest text-paper/50 mt-1">
          AI Finance Controller
        </p>
      </div>

      <ul className="flex-1 space-y-1">
        {NAV_ITEMS.map((item) => {
          const active = location.pathname.startsWith(item.path);
          return (
            <li key={item.path}>
              <Link
                to={item.path}
                aria-current={active ? "page" : undefined}
                className={`flex items-center gap-3 px-3 py-2 text-sm font-medium transition-colors border-l-2 ${
                  active
                    ? "border-paper text-paper bg-white/5"
                    : "border-transparent text-paper/60 hover:text-paper hover:bg-white/5"
                }`}
              >
                {item.label}
              </Link>
            </li>
          );
        })}

        {/* Admin-only nav item — role is actually read here, not just stored. */}
        {role === "admin" && (
          <li>
            <Link
              to="/audit-log"
              aria-current={location.pathname.startsWith("/audit-log") ? "page" : undefined}
              className={`flex items-center gap-3 px-3 py-2 text-sm font-medium transition-colors border-l-2 ${
                location.pathname.startsWith("/audit-log")
                  ? "border-paper text-paper bg-white/5"
                  : "border-transparent text-paper/60 hover:text-paper hover:bg-white/5"
              }`}
            >
              Audit Log
            </Link>
          </li>
        )}
      </ul>

      <div className="border-t border-white/10 pt-4">
        <p className="font-mono text-[10px] uppercase tracking-widest text-paper/40 mb-2 px-3">
          {role ?? "guest"}
        </p>
        <button
          onClick={handleLogout}
          className="w-full text-left px-3 py-2 text-sm font-medium text-paper/60 hover:text-paper hover:bg-white/5 transition-colors"
        >
          Log out
        </button>
      </div>
    </nav>
  );
}
