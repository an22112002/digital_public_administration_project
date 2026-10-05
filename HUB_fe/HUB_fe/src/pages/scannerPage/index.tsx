import { useEffect, useState } from "react";
import { getTwainDevices, getTwainInstalled, type ScannerDevice } from "../../api/scannerAPI";

export default function ScannerPage() {
    const [devices, setDevices] = useState<ScannerDevice[]>([]);
    const [installStatus, setInstallStatus] = useState("");
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");

    const handleRefresh = async () => {
        setLoading(true);
        setError("");
        try {
            const [installedResponse, devicesResponse] = await Promise.all([
                getTwainInstalled(),
                getTwainDevices(),
            ]);
            setInstallStatus(installedResponse.message || (installedResponse.installed ? "TWAIN driver sẵn sàng." : "Chưa tìm thấy thiết bị hoặc TWAIN driver."));
            setDevices(devicesResponse.twain ?? []);
        } catch {
            setError("Không thể kết nối tới dịch vụ TWAIN của HUB.");
            setDevices([]);
        } finally {
            setLoading(false);
        }
    }

    useEffect(() => {
        void handleRefresh();
    }, []);

    const unavailable = installStatus.toLowerCase().includes("không") || installStatus.toLowerCase().includes("chưa");

    return (
        <div className="mx-auto flex max-w-6xl flex-col gap-8">
            <header className="flex flex-col gap-5 sm:flex-row sm:items-end sm:justify-between">
                <div>
                    <p className="text-xs font-bold uppercase tracking-[0.2em] text-cyan-600">Thiết bị ngoại vi</p>
                    <h1 className="mt-2 text-3xl font-bold tracking-tight text-slate-950">Máy scan</h1>
                    <p className="mt-2 max-w-2xl text-sm leading-6 text-slate-500">Kiểm tra TWAIN driver và các thiết bị scan đang kết nối với HUB.</p>
                </div>
                <button className="inline-flex items-center justify-center gap-2 rounded-xl bg-cyan-500 px-5 py-3 text-sm font-bold text-slate-950 transition hover:bg-cyan-400 disabled:cursor-not-allowed disabled:bg-slate-200 disabled:text-slate-500" onClick={() => void handleRefresh()} disabled={loading}><span aria-hidden="true">↻</span>{loading ? "Đang kiểm tra..." : "Cập nhật trạng thái"}</button>
            </header>
            {error && <div className="rounded-xl border border-red-200 bg-red-50 p-4 text-sm font-medium text-red-700">{error}</div>}
            <section className="overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm">
                <div className="border-b border-slate-100 px-5 py-5 sm:px-7">
                    <h2 className="text-lg font-bold text-slate-950">Trạng thái TWAIN</h2>
                    <p className="mt-1 text-sm text-slate-500">HUB sử dụng trực tiếp TWAIN driver để kết nối và quét tài liệu.</p>
                </div>
                <div className="p-5 sm:p-7"><div className={`rounded-xl border p-4 text-sm ${unavailable ? "border-amber-200 bg-amber-50 text-amber-800" : "border-emerald-200 bg-emerald-50 text-emerald-800"}`}><span className="mr-2" aria-hidden="true">●</span>{installStatus || "Đang kiểm tra..."}</div></div>
            </section>
            <section className="overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm">
                <div className="border-b border-slate-100 px-5 py-5 sm:px-7"><h2 className="text-lg font-bold text-slate-950">Thiết bị TWAIN tìm được</h2><p className="mt-1 text-sm text-slate-500">Các nguồn TWAIN mà HUB có thể sử dụng để quét.</p></div>
                <div className="overflow-x-auto p-5 sm:p-7"><table className="w-full min-w-[650px] text-left">
                    <thead className="bg-slate-950 text-xs uppercase tracking-wider text-slate-300">
                        <tr>
                            <th className="px-4 py-3">Tên máy scan</th>
                            <th className="px-4 py-3 text-center">Driver</th>
                            <th className="px-4 py-3 text-center">Trạng thái</th>
                        </tr>
                    </thead>
                    <tbody>
                        {devices && devices.length > 0 ? (
                            <>
                                {devices.map((device) => (
                                    <tr key={device.name} className="border-t border-slate-100 transition hover:bg-cyan-50/40">
                                        <td className="px-4 py-4 text-sm font-semibold text-slate-800">{device.name}</td>
                                        <td className="px-4 py-4 text-center font-semibold text-cyan-700">TWAIN</td>
                                        <td className="px-4 py-4 text-center"><span className={`rounded-full px-3 py-1 text-xs font-semibold ${device.status === "connected" ? "bg-emerald-50 text-emerald-700" : "bg-slate-100 text-slate-500"}`}>{device.status === "connected" ? "Kết nối" : "Ngắt kết nối"}</span></td>
                                    </tr>
                                ))}
                            </>
                        ) : (
                            <tr>
                                <td className="p-8 text-center text-sm text-slate-500" colSpan={3}>
                                    Không tìm thấy máy scan TWAIN nào.
                                </td>
                            </tr>
                        )}
                    </tbody>
                </table></div>
            </section>
            <div>
            </div>
        </div>
    )
}
