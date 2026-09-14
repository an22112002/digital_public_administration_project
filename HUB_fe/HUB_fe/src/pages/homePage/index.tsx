import { Outlet } from "react-router-dom";
import { useLocation, useNavigate } from "react-router-dom";

export default function Homepage() {
    const navigate = useNavigate();
    const location = useLocation();

    const navigationItems = [
        { label: "Thông tin", path: "/info" },
        { label: "Chế độ hoạt động", path: "/mode" },
        { label: "Dịch vụ", path: "/service" },
        { label: "LLM", path: "/llm" },
    ];

    return (
        <div className="min-h-screen bg-slate-100 text-slate-800 md:flex">
            {/* Navigator */}
            <nav className="w-full shrink-0 bg-slate-950 p-5 text-white md:w-64 md:p-6">
                <div className="mb-10 flex items-center gap-3">
                    <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-cyan-400 font-black text-slate-950">H</div>
                    <div>
                        <div className="text-lg font-bold tracking-tight">HUB</div>
                        <div className="text-xs text-slate-400">Thiết lập hệ thống</div>
                    </div>
                </div>
                <div className="mb-3 px-3 text-xs font-semibold uppercase tracking-[0.18em] text-slate-500">Cài đặt</div>
                <ul className="space-y-1">
                    {navigationItems.map((item) => (
                        <li key={item.path}>
                            <button
                                className={`w-full rounded-xl px-3 py-3 text-left text-sm font-medium transition ${location.pathname === item.path ? "bg-cyan-400 text-slate-950 shadow-lg shadow-cyan-950/30" : "text-slate-300 hover:bg-slate-800 hover:text-white"}`}
                                onClick={() => navigate(item.path)}
                            >
                                {item.label}
                            </button>
                        </li>
                    ))}
                </ul>
                <div className="mb-3 mt-10 px-3 text-xs font-semibold uppercase tracking-[0.18em] text-slate-500">Thiết bị ngoại vi</div>
                <ul>
                    <li>
                        <button
                            className={`w-full rounded-xl px-3 py-3 text-left text-sm font-medium transition ${location.pathname === "/scanner" ? "bg-cyan-400 text-slate-950 shadow-lg shadow-cyan-950/30" : "text-slate-300 hover:bg-slate-800 hover:text-white"}`}
                            onClick={() => navigate("/scanner")}
                        >
                            Máy scan
                        </button>
                    </li>
                </ul>
            </nav>

            {/* Frame */}
            <main className="w-full p-4 sm:p-8">
                <Outlet />
            </main>

        </div>
    );
}