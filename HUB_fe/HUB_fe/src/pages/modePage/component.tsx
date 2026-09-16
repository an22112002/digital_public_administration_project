interface ModeButtonProps {
    onClick: () => void;
    label: string;
    info: string;
}

export default function ModeButton({ onClick, label, info}: ModeButtonProps) {

    const icon = label === "Cơ bản" ? "◌" : label === "Máy chủ" ? "▣" : "⇄";

    return (
        <button
            type="button"
            className="group flex min-h-48 flex-col items-start rounded-2xl border border-slate-200 bg-white p-5 text-left shadow-sm transition duration-200 hover:-translate-y-1 hover:border-cyan-300 hover:shadow-xl hover:shadow-slate-200/70 focus:outline-none focus:ring-2 focus:ring-cyan-400 focus:ring-offset-2"
            onClick={onClick}
        >
            <span className="mb-5 flex h-10 w-10 items-center justify-center rounded-xl bg-slate-100 text-lg font-bold text-cyan-600 transition group-hover:bg-cyan-100" aria-hidden="true">{icon}</span>
            <h2 className="text-base font-bold text-slate-900">{label}</h2>
            <p className="mt-2 text-sm leading-6 text-slate-500">{info}</p>
        </button>
    );
}