import { useEffect, useState } from "react";
import { getServices, updateServiceActive, type Service } from "../../api/serviceAPI";

export default function ServicePage() {
    // const [file, setFile] = useState<File | null>(null);
    const [services, setServices] = useState<Service[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");
    const [updatingServiceId, setUpdatingServiceId] = useState<Service["serviceID"] | null>(null);
    const [searchTerm, setSearchTerm] = useState("");
    const [categoryFilter, setCategoryFilter] = useState("");

    const fetchServices = async () => {
        setLoading(true);
        setError("");
        try {
            setServices(await getServices());
        } catch {
            setError("Không thể tải danh sách dịch vụ.");
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        void fetchServices();
    }, []);

    const handleActiveChange = async (service: Service, active: boolean) => {
        setUpdatingServiceId(service.serviceID);
        setError("");
        try {
            await updateServiceActive(service.serviceID, active);
            setServices((currentServices) => currentServices.map((currentService) =>
                currentService.serviceID === service.serviceID
                    ? { ...currentService, active }
                    : currentService,
            ));
        } catch {
            setError(`Không thể cập nhật trạng thái dịch vụ "${service.title}".`);
        } finally {
            setUpdatingServiceId(null);
        }
    };

    const categories = Array.from(new Set(services.map((service) => service.category))).sort();
    const normalizedSearchTerm = searchTerm.trim().toLowerCase();
    const filteredServices = services.filter((service) => {
        const matchesSearch = normalizedSearchTerm === ""
            || String(service.serviceID).toLowerCase().includes(normalizedSearchTerm)
            || service.title.toLowerCase().includes(normalizedSearchTerm)
            || service.realTitle.toLowerCase().includes(normalizedSearchTerm);
        const matchesCategory = categoryFilter === "" || service.category === categoryFilter;
        return matchesSearch && matchesCategory;
    });

    // const handleFileUpload = async () => {
    //     if (file) {
    //         const response = await importFileXLSX(file);
    //         if (response.success) {
    //             alert("File đã được tải lên và xử lý thành công.");
    //         } else {
    //             alert(`Lỗi khi xử lý file: ${response.message}`);
    //         }
    //     }
    // }

    return (
        <div className="mx-auto flex max-w-6xl flex-col gap-8">
            <header className="flex flex-col gap-5 sm:flex-row sm:items-end sm:justify-between">
                <div>
                    <p className="text-xs font-bold uppercase tracking-[0.2em] text-cyan-600">Vận hành hệ thống</p>
                    <h1 className="mt-2 text-3xl font-bold tracking-tight text-slate-950">Dịch vụ tích hợp</h1>
                    <p className="mt-2 max-w-2xl text-sm leading-6 text-slate-500">Bật hoặc tắt các dịch vụ mà HUB được phép sử dụng trong quy trình xử lý.</p>
                </div>
                <button
                    className="inline-flex items-center justify-center gap-2 rounded-xl bg-cyan-500 px-5 py-3 text-sm font-bold text-slate-950 transition hover:bg-cyan-400 disabled:cursor-not-allowed disabled:bg-slate-200 disabled:text-slate-500"
                    onClick={() => void fetchServices()}
                    disabled={loading}
                >
                    <span aria-hidden="true">↻</span>{loading ? "Đang tải..." : "Cập nhật danh sách"}
                </button>
            </header>

            {error && <div className="rounded-xl border border-red-200 bg-red-50 p-4 text-sm font-medium text-red-700">{error}</div>}

            <section className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm sm:p-6">
                <div className="mb-4 flex items-center justify-between gap-3">
                    <div>
                        <h2 className="text-lg font-bold text-slate-950">Danh sách dịch vụ</h2>
                        <p className="mt-1 text-sm text-slate-500">{filteredServices.length} dịch vụ đang hiển thị</p>
                    </div>
                    <span className="rounded-full bg-cyan-50 px-3 py-1 text-xs font-semibold text-cyan-700">{services.filter((service) => service.active).length} đang bật</span>
                </div>
                <div className="mb-5 flex flex-col gap-3 sm:flex-row">
                <input
                    type="search"
                    className="min-w-[240px] flex-1 rounded-xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm outline-none transition placeholder:text-slate-400 focus:border-cyan-400 focus:bg-white focus:ring-2 focus:ring-cyan-100"
                    placeholder="Tìm theo tên hoặc ID dịch vụ"
                    value={searchTerm}
                    onChange={(event) => setSearchTerm(event.target.value)}
                    aria-label="Tìm kiếm dịch vụ theo tên hoặc ID"
                />
                <select
                    className="rounded-xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm text-slate-700 outline-none transition focus:border-cyan-400 focus:bg-white focus:ring-2 focus:ring-cyan-100"
                    value={categoryFilter}
                    onChange={(event) => setCategoryFilter(event.target.value)}
                    aria-label="Lọc dịch vụ theo danh mục"
                >
                    <option value="">Tất cả danh mục</option>
                    {categories.map((category) => (
                        <option key={category} value={category}>{category}</option>
                    ))}
                </select>
                </div>

                <div className="overflow-x-auto rounded-xl border border-slate-200">
                <table className="w-full min-w-[700px] text-left">
                    <thead className="bg-slate-950 text-xs uppercase tracking-wider text-slate-300">
                        <tr>
                            <th className="px-4 py-3 text-center">ID</th>
                            <th className="px-4 py-3">Tên dịch vụ</th>
                            <th className="px-4 py-3">Tên thực</th>
                            <th className="px-4 py-3">Danh mục</th>
                            <th className="px-4 py-3 text-center">Hoạt động</th>
                        </tr>
                    </thead>
                    <tbody>
                        {loading ? (
                            <tr><td className="p-8 text-center text-sm text-slate-500" colSpan={5}>Đang tải danh sách dịch vụ...</td></tr>
                        ) : services.length === 0 ? (
                            <tr><td className="p-8 text-center text-sm text-slate-500" colSpan={5}>Chưa có dịch vụ nào.</td></tr>
                        ) : filteredServices.length === 0 ? (
                            <tr><td className="p-8 text-center text-sm text-slate-500" colSpan={5}>Không tìm thấy dịch vụ phù hợp.</td></tr>
                        ) : filteredServices.map((service) => (
                            <tr key={service.serviceID} className="border-t border-slate-100 transition hover:bg-cyan-50/40">
                                <td className="px-4 py-4 text-center text-xs font-semibold text-slate-400">{service.serviceID}</td>
                                <td className="px-4 py-4 text-sm font-semibold text-slate-800">{service.title}</td>
                                <td className="px-4 py-4 text-sm text-slate-500">{service.realTitle}</td>
                                <td className="px-4 py-4"><span className="rounded-full bg-slate-100 px-3 py-1 text-xs font-medium text-slate-600">{service.category}</span></td>
                                <td className="px-4 py-4 text-center">
                                    <input
                                        type="checkbox"
                                        className="h-5 w-5 cursor-pointer accent-cyan-500 disabled:cursor-not-allowed"
                                        checked={service.active}
                                        disabled={updatingServiceId === service.serviceID}
                                        onChange={(event) => void handleActiveChange(service, event.target.checked)}
                                        aria-label={`Trạng thái hoạt động của ${service.title}`}
                                    />
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
                </div>
            </section>

            {/* <div className="mt-6">
                <input type="file" accept=".xlsx" onChange={(event) => setFile(event.target.files?.[0] ?? null)} />
                <button
                    className="ml-2 bg-green-500 hover:bg-green-600 disabled:bg-gray-400 text-white font-bold py-2 px-4 rounded"
                    onClick={() => void handleFileUpload()}
                    disabled={!file}
                >
                    Nhập file XLSX
                </button>
            </div> */}
        </div>
    );
}