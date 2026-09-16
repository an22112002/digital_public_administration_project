import { useEffect, useState } from "react";
import { getDevicesList, getNaps2Installed} from "../../api/scannerAPI";
import { saveNAPS2Path, getNAPS2Path } from "../../api/settingAPI";

interface DeviceDetail {
    name: string;
    status: "connected" | "disconnected";
    driver: string[];
}

export default function ScannerPage() {
    const [NAPS2Path, setNAPS2Path] = useState<string>("");
    const [changeNAPS2Path, setChangeNAPS2Path] = useState<boolean>(false);

    const [devices, setDevices] = useState<DeviceDetail[] | null>(null);
    const [installStatus, setInstallStatus] = useState<string>("");

    const fetchNAPS2Path = async () => {
        const response = await getNAPS2Path();
        setNAPS2Path(response.naps2_path);
    }

    const handleNAPS2PathChange = async () => {
        const response = await saveNAPS2Path(NAPS2Path);
        if (response.success) {
            alert("Đường dẫn NAPS2 đã được cập nhật thành công.");
            setChangeNAPS2Path(false);
            await fetchInstalledStatus(); // Refresh status path after saving
        }
    }

    const fetchInstalledStatus = async () => {
        const installedResponse = await getNaps2Installed();
        if (!installedResponse.installed) {
            setInstallStatus("NAPS2 chưa được cài đặt. Vui lòng cài đặt NAPS2 để sử dụng chức năng quét.");
        } else {
            setInstallStatus(`NAPS2 đã được cài đặt. ${installedResponse.message}`);
        }
    }
        
    const fetchDevices = async () => {
        const devicesData = await getDevicesList();
        const combinedDevices: DeviceDetail[] = [
            ...(devicesData.wia ?? []).map(device => ({ ...device, driver: ["WIA"] })),
            ...(devicesData.twain ?? []).map(device => ({ ...device, driver: ["TWAIN"] })),
            ...(devicesData.escl ?? []).map(device => ({ ...device, driver: ["ESCL"] })),
        ];
        setDevices(combinedDevices);
    }

    const handleRefresh = async () => {
        await fetchInstalledStatus();
        await fetchDevices();
    }

    useEffect(() => {

        const load = async () => {
            await fetchNAPS2Path();
            await fetchInstalledStatus();
            await fetchDevices();
        };

        load();
    }, []);

    return (
        <div className="mx-auto flex max-w-6xl flex-col gap-8">
            <header className="flex flex-col gap-5 sm:flex-row sm:items-end sm:justify-between">
                <div>
                    <p className="text-xs font-bold uppercase tracking-[0.2em] text-cyan-600">Thiết bị ngoại vi</p>
                    <h1 className="mt-2 text-3xl font-bold tracking-tight text-slate-950">Máy scan</h1>
                    <p className="mt-2 max-w-2xl text-sm leading-6 text-slate-500">Kiểm tra phần mềm NAPS2 và các thiết bị scan đang kết nối với HUB.</p>
                </div>
                <button className="inline-flex items-center justify-center gap-2 rounded-xl bg-cyan-500 px-5 py-3 text-sm font-bold text-slate-950 transition hover:bg-cyan-400" onClick={() => void handleRefresh}><span aria-hidden="true">↻</span>Cập nhật trạng thái</button>
            </header>
            <section className="overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm">
                <div className="border-b border-slate-100 px-5 py-5 sm:px-7">
                    <h2 className="text-lg font-bold text-slate-950">Cấu hình NAPS2</h2>
                    <p className="mt-1 text-sm text-slate-500">Đường dẫn được dùng để khởi chạy quy trình quét tài liệu.</p>
                </div>
                <div className="grid gap-5 p-5 sm:grid-cols-2 sm:p-7">
                    {/* Đường dẫn NAPS2 */}
                    <label>
                        <span className="mb-2 block text-sm font-semibold text-slate-600">Đường dẫn NAPS2</span>
                            <input 
                                type="text" 
                                className="w-full rounded-xl border border-slate-200 px-4 py-3 text-sm outline-none transition placeholder:text-slate-400 focus:border-cyan-400 focus:ring-2 focus:ring-cyan-100 disabled:bg-slate-50" 
                                placeholder="Nhập đường dẫn NAPS2" 
                                disabled={!changeNAPS2Path}
                                value={NAPS2Path}
                                onChange={(e) => setNAPS2Path(e.target.value)}
                            />
                    </label>
                    <div className="flex items-end"><button type="button" className="w-full rounded-xl border border-slate-300 bg-white px-5 py-3 text-sm font-bold text-slate-700 transition hover:border-cyan-400 hover:text-cyan-700" onClick={async () => { if (changeNAPS2Path) await handleNAPS2PathChange(); else setChangeNAPS2Path(true); }}>{changeNAPS2Path ? "Lưu đường dẫn" : "Sửa đường dẫn"}</button></div>

                    {/* Trạng thái cài đặt NAPS2 */}
                    <div className="sm:col-span-2"><span className="mb-2 block text-sm font-semibold text-slate-600">Trạng thái cài đặt NAPS2</span><div className={`rounded-xl border p-4 text-sm ${installStatus.includes("chưa") ? "border-amber-200 bg-amber-50 text-amber-800" : "border-emerald-200 bg-emerald-50 text-emerald-800"}`}><span className="mr-2" aria-hidden="true">●</span>{installStatus || "Đang kiểm tra..."}</div></div>
                </div>
            </section>
            <section className="overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm">
                <div className="border-b border-slate-100 px-5 py-5 sm:px-7"><h2 className="text-lg font-bold text-slate-950">Thiết bị scan tìm được</h2><p className="mt-1 text-sm text-slate-500">Các driver khả dụng trên thiết bị này.</p></div>
                <div className="overflow-x-auto p-5 sm:p-7"><table className="w-full min-w-[650px] text-left">
                    <thead className="bg-slate-950 text-xs uppercase tracking-wider text-slate-300">
                        <tr>
                            <th className="px-4 py-3 text-center" rowSpan={2}>Tên máy scan</th>
                            <th className="px-4 py-3 text-center" colSpan={3}>Driver</th>
                            <th className="px-4 py-3 text-center" rowSpan={2}>Trạng thái</th>
                        </tr>
                        <tr>
                            <th className="px-4 py-3 text-center">WIA</th>
                            <th className="px-4 py-3 text-center">TWAIN</th>
                            <th className="px-4 py-3 text-center">ESCL</th>
                        </tr>
                    </thead>
                    <tbody>
                        {devices && devices.length > 0 ? (
                            <>
                                {devices.map((device, index) => (
                                    <tr key={index} className="border-t border-slate-100 transition hover:bg-cyan-50/40">
                                        <td className="px-4 py-4 text-center text-sm font-semibold text-slate-800">{device.name}</td>
                                        <td className="px-4 py-4 text-center text-emerald-600">{device.driver.includes("WIA") ? "✓" : "-"}</td>
                                        <td className="px-4 py-4 text-center text-emerald-600">{device.driver.includes("TWAIN") ? "✓" : "-"}</td>
                                        <td className="px-4 py-4 text-center text-emerald-600">{device.driver.includes("ESCL") ? "✓" : "-"}</td>
                                        <td className="px-4 py-4 text-center"><span className={`rounded-full px-3 py-1 text-xs font-semibold ${device.status === "connected" ? "bg-emerald-50 text-emerald-700" : "bg-slate-100 text-slate-500"}`}>{device.status === "connected" ? "Kết nối" : "Ngắt kết nối"}</span></td>
                                    </tr>
                                ))}
                            </>
                        ) : (
                            <tr>
                                <td className="p-8 text-center text-sm text-slate-500" colSpan={5}>
                                    Không tìm thấy máy scan nào.
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
