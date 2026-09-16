
import { useEffect, useState } from "react";
import {
    getLLMModels,
    getLLMServerStatus,
    getLLMSetting,
    loadLLMModel,
    unloadLLMModel,
    updateLLMSetting,
} from "../../api/llmAPI";
import type { LLMSetting } from "../../api/llmAPI";
import { getMode } from "../../api/settingAPI";

export default function LLMPage() {
    const [isServerMode, setIsServerMode] = useState<boolean | null>(null);
    const [models, setModels] = useState<string[]>([]);
    const [setting, setSetting] = useState<LLMSetting>({
        LLM_model: "",
        LLM_gpu_use: 0,
        LLM_context_length: 8192,
    });
    const [serverRunning, setServerRunning] = useState<boolean | null>(null);
    const [loading, setLoading] = useState(true);
    const [saving, setSaving] = useState(false);
    const [modelAction, setModelAction] = useState<"load" | "unload" | null>(null);
    const [message, setMessage] = useState<{ type: "success" | "error"; text: string } | null>(null);

    const readServerStatus = async () => {
        try {
            const response = await getLLMServerStatus();
            setServerRunning(response.state);
        } catch {
            setServerRunning(false);
        }
    };

    const loadSettings = async () => {
        setLoading(true);
        setMessage(null);
        try {
            const [availableModels, currentSetting] = await Promise.all([getLLMModels(), getLLMSetting()]);
            setModels(availableModels);
            setSetting(currentSetting);
            await readServerStatus();
        } catch {
            setMessage({ type: "error", text: "Không thể tải cấu hình LLM. Hãy kiểm tra kết nối backend." });
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        const loadPage = async () => {
            try {
                const mode = await getMode();
                const serverMode = mode.mode === "server";
                setIsServerMode(serverMode);
                if (serverMode) {
                    await loadSettings();
                } else {
                    setLoading(false);
                }
            } catch {
                setIsServerMode(false);
                setLoading(false);
            }
        };

        void loadPage();
    }, []);

    const updateSetting = <K extends keyof LLMSetting>(key: K, value: LLMSetting[K]) => {
        setSetting((current) => ({ ...current, [key]: value }));
        setMessage(null);
    };

    const handleSave = async () => {
        setSaving(true);
        setMessage(null);
        try {
            const response = await updateLLMSetting(setting);
            setMessage({ type: response.success ? "success" : "error", text: response.message });
        } catch {
            setMessage({ type: "error", text: "Không thể lưu cấu hình LLM." });
        } finally {
            setSaving(false);
        }
    };

    const handleModelAction = async (action: "load" | "unload") => {
        setModelAction(action);
        setMessage(null);
        try {
            const response = action === "load" ? await loadLLMModel() : await unloadLLMModel();
            setMessage({ type: response.success ? "success" : "error", text: response.message });
            await readServerStatus();
        } catch {
            setMessage({ type: "error", text: `Không thể ${action === "load" ? "load" : "unload"} mô hình LLM.` });
        } finally {
            setModelAction(null);
        }
    };

    if (isServerMode === null || loading && isServerMode === null) {
        return <div className="mx-auto flex max-w-6xl items-center justify-center py-24 text-sm text-slate-500">Đang kiểm tra quyền truy cập...</div>;
    }

    if (!isServerMode) {
        return (
            <div className="mx-auto flex max-w-3xl flex-col gap-8">
                <header>
                    <p className="text-xs font-bold uppercase tracking-[0.2em] text-cyan-600">Trí tuệ nhân tạo</p>
                    <h1 className="mt-2 text-3xl font-bold tracking-tight text-slate-950">Mô hình ngôn ngữ</h1>
                </header>
                <section className="rounded-2xl border border-amber-200 bg-amber-50 p-8 text-center shadow-sm sm:p-12">
                    <div className="mx-auto flex h-16 w-16 items-center justify-center rounded-2xl bg-amber-400 text-2xl font-black text-amber-950" aria-hidden="true">!</div>
                    <h2 className="mt-5 text-xl font-bold text-amber-950">Tính năng chỉ dành cho mode server</h2>
                    <p className="mx-auto mt-2 max-w-lg text-sm leading-6 text-amber-800">Hãy chuyển sang chế độ Máy chủ để cấu hình và quản lý mô hình ngôn ngữ.</p>
                </section>
            </div>
        );
    }

    return (
        <div className="mx-auto flex max-w-6xl flex-col gap-8">
            <header>
                <p className="text-xs font-bold uppercase tracking-[0.2em] text-cyan-600">Trí tuệ nhân tạo</p>
                <h1 className="mt-2 text-3xl font-bold tracking-tight text-slate-950">Mô hình ngôn ngữ</h1>
                <p className="mt-2 max-w-2xl text-sm leading-6 text-slate-500">Quản lý cấu hình mô hình được HUB sử dụng cho OCR và tự động điền biểu mẫu.</p>
            </header>
            {message && <div className={`rounded-xl border p-4 text-sm font-medium ${message.type === "success" ? "border-emerald-200 bg-emerald-50 text-emerald-800" : "border-red-200 bg-red-50 text-red-700"}`}>{message.text}</div>}

            <section className="grid gap-5 lg:grid-cols-[1.4fr_0.8fr]">
                <div className="rounded-2xl border border-slate-200 bg-white shadow-sm">
                    <div className="border-b border-slate-100 px-5 py-5 sm:px-7">
                        <h2 className="text-lg font-bold text-slate-950">Cấu hình mô hình</h2>
                        <p className="mt-1 text-sm text-slate-500">Các giá trị này được lưu vào cấu hình backend của HUB.</p>
                    </div>
                    <div className="space-y-6 p-5 sm:p-7">
                        <label className="block">
                            <span className="mb-2 block text-sm font-semibold text-slate-600">Mô hình LLM</span>
                            <select value={setting.LLM_model} disabled={loading || saving} onChange={(event) => updateSetting("LLM_model", event.target.value)} className="w-full rounded-xl border border-slate-200 bg-white px-4 py-3 text-sm text-slate-800 outline-none transition focus:border-cyan-400 focus:ring-2 focus:ring-cyan-100 disabled:bg-slate-50">
                                <option value="" disabled>Chọn mô hình</option>
                                {models.map((model) => <option key={model} value={model}>{model}</option>)}
                            </select>
                        </label>
                        <label className="block">
                            <div className="mb-2 flex items-center justify-between gap-3"><span className="text-sm font-semibold text-slate-600">Mức sử dụng GPU</span><span className="rounded-full bg-cyan-50 px-3 py-1 text-xs font-bold text-cyan-700">{setting.LLM_gpu_use.toFixed(2)}</span></div>
                            <input type="range" min="0" max="1" step="0.05" value={setting.LLM_gpu_use} disabled={loading || saving} onChange={(event) => updateSetting("LLM_gpu_use", Number(event.target.value))} className="h-2 w-full cursor-pointer accent-cyan-500 disabled:cursor-not-allowed" />
                            <div className="mt-2 flex justify-between text-xs text-slate-400"><span>CPU</span><span>GPU tối đa</span></div>
                        </label>
                        <label className="block">
                            <span className="mb-2 block text-sm font-semibold text-slate-600">Độ dài context</span>
                            <input type="number" min="1" step="1" value={setting.LLM_context_length} disabled={loading || saving} onChange={(event) => updateSetting("LLM_context_length", Number(event.target.value))} className="w-full rounded-xl border border-slate-200 px-4 py-3 text-sm text-slate-800 outline-none transition focus:border-cyan-400 focus:ring-2 focus:ring-cyan-100 disabled:bg-slate-50" />
                        </label>
                        <button type="button" disabled={loading || saving || !setting.LLM_model} onClick={() => void handleSave()} className="w-full rounded-xl bg-cyan-500 px-5 py-3 text-sm font-bold text-slate-950 transition hover:bg-cyan-400 disabled:cursor-not-allowed disabled:bg-slate-200 disabled:text-slate-500">{saving ? "Đang lưu..." : "Lưu cấu hình"}</button>
                    </div>
                </div>

                <div className="rounded-2xl border border-slate-200 bg-white shadow-sm">
                    <div className="border-b border-slate-100 px-5 py-5 sm:px-7"><h2 className="text-lg font-bold text-slate-950">Trạng thái LM Studio</h2><p className="mt-1 text-sm text-slate-500">Quản lý model đang được nạp trên server.</p></div>
                    <div className="space-y-5 p-5 sm:p-7">
                        <div className={`rounded-xl border p-4 ${serverRunning ? "border-emerald-200 bg-emerald-50" : "border-amber-200 bg-amber-50"}`}><div className={`text-sm font-bold ${serverRunning ? "text-emerald-800" : "text-amber-800"}`}><span className="mr-2" aria-hidden="true">●</span>{serverRunning === null ? "Đang kiểm tra..." : serverRunning ? "Server đang hoạt động" : "Server chưa sẵn sàng"}</div></div>
                        <div className="rounded-xl bg-slate-50 p-4"><p className="text-xs font-semibold uppercase tracking-wider text-slate-400">Model đã chọn</p><p className="mt-2 break-words text-sm font-bold text-slate-800">{setting.LLM_model || "Chưa chọn model"}</p></div>
                        <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-1 xl:grid-cols-2"><button type="button" disabled={modelAction !== null || !serverRunning} onClick={() => void handleModelAction("load")} className="rounded-xl bg-emerald-500 px-4 py-3 text-sm font-bold text-white transition hover:bg-emerald-600 disabled:cursor-not-allowed disabled:bg-slate-200 disabled:text-slate-500">{modelAction === "load" ? "Đang load..." : "Load model"}</button><button type="button" disabled={modelAction !== null || !serverRunning} onClick={() => void handleModelAction("unload")} className="rounded-xl border border-slate-300 bg-white px-4 py-3 text-sm font-bold text-slate-700 transition hover:border-red-300 hover:text-red-700 disabled:cursor-not-allowed disabled:bg-slate-50 disabled:text-slate-400">{modelAction === "unload" ? "Đang unload..." : "Unload model"}</button></div>
                        <button type="button" onClick={() => void readServerStatus()} className="w-full rounded-xl border border-slate-200 px-4 py-3 text-sm font-semibold text-slate-600 transition hover:border-cyan-400 hover:text-cyan-700">↻ Kiểm tra lại trạng thái</button>
                    </div>
                </div>
            </section>
        </div>
    )
}