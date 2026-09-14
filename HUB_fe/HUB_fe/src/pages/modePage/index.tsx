import ModeButton from './component.tsx';
import { useState, useEffect } from "react";
import { saveMode, getMode } from "../../api/settingAPI";
import type { ModeResponse } from "../../api/settingAPI";


export default function Modepage() {
    const [changedMode, setChangedMode] = useState<"basic" | "server" | "client" | null>(null);

    const [mode, setMode] = useState<string>("");
    const [server_ip, setServer_ip] = useState<string>("");

    useEffect(() => {
        const fetchMode = async () => {
            const response: ModeResponse = await getMode();
            setMode(response.mode);
            setServer_ip(response.server_ip || "");
        }
        fetchMode();
    }, []);

    const handleModeChange = async (newMode: "basic" | "server" | "client" | null) => {
        if (newMode === null) {
            return;
        }
        if (newMode === "client" && !isValidateServerIP(server_ip)) {
            alert("Địa chỉ máy chủ không hợp lệ. Vui lòng nhập đúng địa chỉ IP.");
            return;
        }
        const response: ModeResponse = {
            mode: newMode,
            server_ip: newMode === "client" ? server_ip : null,
        };
        const result = await saveMode({ mode: newMode, server_ip: server_ip || null });
        if (result.success) {
            alert("Chế độ đã được cập nhật thành công. Vui lòng khởi động lại ứng dụng để áp dụng thay đổi.");
            setMode(newMode);
            setChangedMode(null);
        }
        setServer_ip(response.server_ip || "");
    };

    const isValidateServerIP = (ip: string) => {
        const ipRegex = /^(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$/;
        return ipRegex.test(ip);
    }

    return (
        <div className="mx-auto flex max-w-6xl flex-col gap-8">
            <header>
                <h1 className="text-3xl font-bold tracking-tight text-slate-950">Chế độ hoạt động</h1>
                <p className="mt-2 max-w-2xl text-sm leading-6 text-slate-500">Chọn cách HUB xử lý tài liệu phù hợp với cấu hình máy và mô hình sử dụng của bạn.</p>
            </header>

            <section>
                <div className="mb-4 flex items-center justify-between">
                    <h2 className="text-sm font-bold uppercase tracking-[0.12em] text-slate-500">Các chế độ khả dụng</h2>
                    <span className="rounded-full bg-white px-3 py-1 text-xs font-medium text-slate-500 shadow-sm">3 lựa chọn</span>
                </div>
                <div className="grid gap-4 lg:grid-cols-3">
                    <ModeButton 
                        label="Cơ bản" 
                        info="Hoạt động độc lập, chỉ scan và đẩy tài liệu, tắt các chức năng OCR, tắt tự điền form. Dùng được cho các máy yếu." 
                        onClick={() => {setChangedMode("basic");}} />
                    <ModeButton 
                        label="Máy chủ" 
                        info="Hoạt động độc lập, scan và đẩy tài liệu, OCR, tự điền form. Dùng cho các máy mạnh có GPU hoặc CPU mạnh. Có thể hỗ trợ cho nhiều máy khách cùng lúc. Máy phải có LM Studio cài đặt sẵn." 
                        onClick={() => {setChangedMode("server");}} />
                    <ModeButton 
                        label="Máy khách" 
                        info="Vẫn có thể chạy độc lập như máy Cơ bản, nhưng dùng được OCR, tự điền form. Tuy nhiên, chỉ dùng được khi có máy chủ hoạt động cùng LAN. Máy khách sẽ gửi dữ liệu scan lên máy chủ để xử lý OCR và tự điền form, sau đó nhận lại kết quả từ máy chủ. Dùng được cho các máy yếu." 
                        onClick={() => {setChangedMode("client");}} />
                </div>

            </section>

            <section className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm sm:p-6">
                <div className="mb-5">
                    <h2 className="text-lg font-bold text-slate-950">{changedMode !== null ? "Xác nhận thay đổi" : "Chế độ hiện tại"}</h2>
                    <p className="mt-1 text-sm text-slate-500">{changedMode !== null ? "Kiểm tra thông tin trước khi lưu cấu hình mới." : "Cấu hình đang được sử dụng trên thiết bị này."}</p>
                </div>
                
                <div className="rounded-xl bg-slate-50 p-4">
                    <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
                        <span className="text-sm font-semibold text-slate-500">Chế độ đã chọn</span>
                        <span className="text-lg font-bold text-cyan-700">
                            {changedMode !== null ? (
                                changedMode === "basic" ? "Cơ bản" : changedMode === "server" ? "Máy chủ" : "Máy khách"
                            ) : (
                                mode === "basic" ? "Cơ bản" : mode === "server" ? "Máy chủ" : "Máy khách"
                            )}
                            
                        </span>
                    </div>
                    <div className="mt-5">
                        {(mode === "client" || changedMode === "client") && (
                            <>
                                <label className="mb-2 block text-sm font-semibold text-slate-600" htmlFor="server-ip">Địa chỉ máy chủ</label>
                                <input
                                    id="server-ip"
                                    type="text"
                                    value={server_ip}
                                    onChange={(e) => setServer_ip(e.target.value)}
                                    className="w-full rounded-xl border border-slate-200 bg-white px-4 py-3 text-sm text-slate-800 outline-none transition placeholder:text-slate-400 focus:border-cyan-400 focus:ring-2 focus:ring-cyan-100 sm:max-w-md"
                                    placeholder="Nhập địa chỉ máy chủ"
                                />
                            </>
                        )}
                    </div>
                    {changedMode && (
                        <button type="button" className="mt-5 rounded-xl bg-cyan-500 px-5 py-3 text-sm font-bold text-slate-950 transition hover:bg-cyan-400"
                            onClick={async () => {
                                await handleModeChange(changedMode);
                            }}>
                            Lưu thay đổi
                        </button>
                    )}
                    
                </div>
            </section>
        </div>
    );
}