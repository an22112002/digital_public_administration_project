import { useState, useEffect } from "react";
import { getTitle, saveTitle, getProvince, getCommune, listProvince, listCommune, getSelfIP, saveNewPosition, getUI, saveUI } from "../../api/settingAPI";
import type { ProvinceListResponse, CommuneListResponse, UIResponse } from "../../api/settingAPI";

export default function InfoPage() {
    const [machineIp, setMachineIp] = useState("");
    const [title, setTitle] = useState("");
    const [changedTitle, setChangedTitle] = useState(false);
    const [province, setProvince] = useState("");
    const [commune, setCommune] = useState("");
    const [selectProvinceID, setSelectProvinceID] = useState<string | null>(null);
    const [selectCommuneID, setSelectCommuneID] = useState<string | null>(null);
    const [provinceArr, setProvinceArr] = useState<ProvinceListResponse>({ province_list: [] });
    const [communeArr, setCommuneArr] = useState<CommuneListResponse>({ commune_list: [] });
    const [changedPosition, setChangedPosition] = useState(false);
    const [provinceError, setProvinceError] = useState("");
    const [communeError, setCommuneError] = useState("");
    const [isLoadingCommunes, setIsLoadingCommunes] = useState(false);
    const [ui, setUI] = useState<UIResponse["ui"]>("desktop");
    const [isSavingUI, setIsSavingUI] = useState(false);

    const fetchTitle = async () => {
        const response = await getTitle();
        setTitle(response.title);
    }

    const fetchSelfIP = async () => {
        const response = await getSelfIP();
        setMachineIp(response.self_ip);
    }

    const load = async () => {
        const saveProvince = await getProvince();
        const saveCommune = await getCommune();

        const provinceListResponse: ProvinceListResponse = await listProvince();
        setProvinceArr(provinceListResponse);
        for (const provinceOption of provinceListResponse.province_list) {
            if (provinceOption.name === saveProvince.province) {
                setProvince(provinceOption.name);
                setSelectProvinceID(provinceOption.id);


                const communeListResponse: CommuneListResponse = await listCommune(provinceOption.id);
                setCommuneArr(communeListResponse);
                for (const communeOption of communeListResponse.commune_list) {
                    if (communeOption.name === saveCommune.commune) {
                        setCommune(communeOption.name);
                        setSelectCommuneID(communeOption.id);
                        break;
                    }
                }
                break;
            }
        }
    }

    useEffect(() => {
        fetchTitle();
        fetchSelfIP();
        load();
        getUI().then((response) => setUI(response.ui)).catch(() => undefined);
    }, []);

    const handleUIChange = async (nextUI: UIResponse["ui"]) => {
        if (nextUI === ui) return;

        setIsSavingUI(true);
        try {
            const response = await saveUI(nextUI);
            if (response.success) {
                setUI(nextUI);
            }
        } finally {
            setIsSavingUI(false);
        }
    };

    const handleTitleChange = async () => {
        const response = await saveTitle(title);
        if (response.success) {
            alert("Tiêu đề đã được cập nhật thành công.");
            setChangedTitle(false);
        }
    }

    const handleProvinceChange = async (value: string) => {
        const normalizedValue = value.trim();
        setProvince(normalizedValue);
        setCommune("");
        setSelectCommuneID(null);
        setCommuneArr({ commune_list: [] });

        const selectedProvince = provinceArr.province_list.find(
            (option) => option.name.trim().toLocaleLowerCase() === normalizedValue.toLocaleLowerCase(),
        );

        if (!selectedProvince) {
            setSelectProvinceID(null);
            setProvinceError(normalizedValue ? "Tên tỉnh/thành phố không có trong danh sách." : "");
            return;
        }

        setProvinceError("");
        setSelectProvinceID(selectedProvince.id);
        setIsLoadingCommunes(true);
        try {
            const communeListResponse = await listCommune(selectedProvince.id);
            setCommuneArr(communeListResponse);
        } finally {
            setIsLoadingCommunes(false);
        }
    };

    const handleCommuneChange = (value: string) => {
        const normalizedValue = value.trim();
        setCommune(normalizedValue);
        const selectedCommune = communeArr.commune_list.find(
            (option) => option.name.trim().toLocaleLowerCase() === normalizedValue.toLocaleLowerCase(),
        );

        setSelectCommuneID(selectedCommune?.id || null);
        setCommuneError(selectedCommune || !normalizedValue ? "" : "Tên xã/phường không có trong danh sách.");
    };

    const handlePositionChange = async () => {
        const provinceIsValid = provinceArr.province_list.some(
            (option) => option.name.trim().toLocaleLowerCase() === province.trim().toLocaleLowerCase(),
        );
        const communeIsValid = communeArr.commune_list.some(
            (option) => option.name.trim().toLocaleLowerCase() === commune.trim().toLocaleLowerCase(),
        );

        if (!provinceIsValid || !selectProvinceID) {
            setProvinceError("Vui lòng chọn tỉnh/thành phố có trong danh sách.");
        }
        if (!communeIsValid || !selectCommuneID) {
            setCommuneError("Vui lòng chọn xã/phường có trong danh sách.");
        }
        if (!provinceIsValid || !communeIsValid || !selectProvinceID || !selectCommuneID) return;

        const response = await saveNewPosition(selectProvinceID, selectCommuneID);
        if (response.success) {
            alert("Vị trí đã được cập nhật thành công.");
            setProvince(province.trim());
            setCommune(commune.trim());
            setChangedPosition(false);
        }
    };

    return (
        <div className="mx-auto flex max-w-5xl flex-col gap-8">
            <header>
                <p className="text-xs font-bold uppercase tracking-[0.2em] text-cyan-600">Thiết lập hệ thống</p>
                <h1 className="mt-2 text-3xl font-bold tracking-tight text-slate-950">Thông tin cơ quan</h1>
                <p className="mt-2 max-w-2xl text-sm leading-6 text-slate-500">Cập nhật tiêu đề hiển thị và vị trí hành chính của cơ quan trên HUB.</p>
            </header>

            <section className="overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm">
                <div className="border-b border-slate-100 px-5 py-5 sm:px-7">
                    <h2 className="text-lg font-bold text-slate-950">Thông tin hiển thị</h2>
                    <p className="mt-1 text-sm text-slate-500">Tiêu đề này sẽ xuất hiện trong các màn hình của hệ thống.</p>
                </div>
                <div className="flex flex-col gap-3 p-5 sm:flex-row sm:items-end sm:p-7">
                    <label className="flex-1">
                        <span className="mb-2 block text-sm font-semibold text-slate-600">Tiêu đề</span>
                        <input type="text" className="w-full rounded-xl border border-slate-200 px-4 py-3 text-sm text-slate-800 outline-none transition placeholder:text-slate-400 focus:border-cyan-400 focus:ring-2 focus:ring-cyan-100 disabled:bg-slate-50" placeholder="Nhập tiêu đề" disabled={!changedTitle} value={title} onChange={(e) => setTitle(e.target.value)} />
                    </label>
                    <button type="button" className="rounded-xl bg-cyan-500 px-5 py-3 text-sm font-bold text-slate-950 transition hover:bg-cyan-400" onClick={async () => { if (changedTitle) await handleTitleChange(); else setChangedTitle(true); }}>
                        {changedTitle ? "Lưu tiêu đề" : "Sửa tiêu đề"}
                    </button>
                </div>
            </section>

            <section className="overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm">
                <div className="border-b border-slate-100 px-5 py-5 sm:px-7">
                    <div className="flex flex-wrap items-center justify-between gap-3">
                        <div>
                            <h2 className="text-lg font-bold text-slate-950">Vị trí cơ quan</h2>
                            <p className="mt-1 text-sm text-slate-500">Nhập hoặc chọn đúng tên trong danh sách do API cung cấp.</p>
                        </div>
                        <span className="rounded-full bg-cyan-50 px-3 py-1 text-xs font-semibold text-cyan-700">{province && commune ? `${province} · ${commune}` : "Chưa thiết lập"}</span>
                    </div>
                </div>
                <div className="grid gap-5 p-5 sm:grid-cols-2 sm:p-7">
                    <label>
                        <span className="mb-2 block text-sm font-semibold text-slate-600">Tỉnh / Thành phố</span>
                        <input list="province-options" type="text" value={province} disabled={!changedPosition} onChange={(e) => { void handleProvinceChange(e.target.value); }} className={`w-full rounded-xl border px-4 py-3 text-sm text-slate-800 outline-none transition placeholder:text-slate-400 focus:border-cyan-400 focus:ring-2 focus:ring-cyan-100 disabled:bg-slate-50 ${provinceError ? "border-red-300" : "border-slate-200"}`} placeholder="Nhập để tìm tỉnh/thành phố" />
                        <datalist id="province-options">{provinceArr.province_list.map((option) => <option key={option.id} value={option.name} />)}</datalist>
                        {provinceError && <span className="mt-2 block text-xs font-medium text-red-600">{provinceError}</span>}
                    </label>
                    <label>
                        <span className="mb-2 block text-sm font-semibold text-slate-600">Xã / Phường</span>
                        <input list="commune-options" type="text" value={commune} disabled={!changedPosition || !selectProvinceID || isLoadingCommunes} onChange={(e) => handleCommuneChange(e.target.value)} className={`w-full rounded-xl border px-4 py-3 text-sm text-slate-800 outline-none transition placeholder:text-slate-400 focus:border-cyan-400 focus:ring-2 focus:ring-cyan-100 disabled:bg-slate-50 ${communeError ? "border-red-300" : "border-slate-200"}`} placeholder={isLoadingCommunes ? "Đang tải danh sách xã/phường..." : "Nhập để tìm xã/phường"} />
                        <datalist id="commune-options">{communeArr.commune_list.map((option) => <option key={option.id} value={option.name} />)}</datalist>
                        {communeError && <span className="mt-2 block text-xs font-medium text-red-600">{communeError}</span>}
                    </label>
                </div>
                <div className="flex flex-col gap-3 border-t border-slate-100 bg-slate-50 px-5 py-5 sm:flex-row sm:items-center sm:justify-between sm:px-7">
                    <p className="text-xs leading-5 text-slate-500">Chỉ gửi API khi cả tỉnh/thành phố và xã/phường đều khớp danh sách.</p>
                    {changedPosition ? <button type="button" className="rounded-xl bg-cyan-500 px-5 py-3 text-sm font-bold text-slate-950 transition hover:bg-cyan-400" onClick={async () => { await handlePositionChange(); }}>Lưu vị trí</button> : <button type="button" className="rounded-xl border border-slate-300 bg-white px-5 py-3 text-sm font-bold text-slate-700 transition hover:border-cyan-400 hover:text-cyan-700" onClick={() => setChangedPosition(true)}>Sửa vị trí cơ quan</button>}
                </div>
            </section>

            <header>
                <h1 className="text-3xl font-bold tracking-tight text-slate-950">Thông tin máy</h1>
                <p className="mt-2 max-w-2xl text-sm leading-6 text-slate-500">Cập nhật giao diện hiển thị của người dùng trên thiết bị này.</p>
            </header>

            <section className="overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm">
                <div className="flex flex-col gap-5 px-5 py-5">
                    <div className="flex flex-col gap-2">
                        <p className="text-sm font-semibold text-slate-600">IP máy</p>
                        <p className="mt-1 font-mono text-lg font-bold text-cyan-700">{machineIp}</p>
                        <button type="button" className="mt-2 w-[20%] rounded-xl bg-cyan-500 px-5 py-3 text-sm font-bold text-slate-950 transition hover:bg-cyan-400" onClick={() => { navigator.clipboard.writeText(machineIp);}}>Sao chép địa chỉ IP</button>
                    </div>
                </div>
                <div className="flex flex-col gap-5 border-t border-slate-100 px-5 py-5 sm:flex-row sm:items-center sm:justify-between sm:px-7">
                    <div className="flex flex-col gap-2">
                        <p className="text-sm font-semibold text-slate-600">Giao diện</p>
                        <div className="mt-2 inline-flex rounded-xl bg-slate-100 p-1" role="group" aria-label="Chọn giao diện">
                            {(["desktop", "kiosk"] as const).map((option) => (
                                <button
                                    key={option}
                                    type="button"
                                    disabled={isSavingUI}
                                    onClick={() => void handleUIChange(option)}
                                    className={`rounded-lg px-4 py-2 text-sm font-bold transition ${ui === option ? "bg-cyan-500 text-slate-950 shadow-sm" : "text-slate-500 hover:text-slate-800"}`}
                                >
                                    {option === "desktop" ? "Desktop" : "Kiosk"}
                                </button>
                            ))}
                        </div>
                    </div>
                </div>
            </section>
        </div>
    )
}