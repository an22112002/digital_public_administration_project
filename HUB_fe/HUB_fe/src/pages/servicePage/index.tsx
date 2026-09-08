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
        <div className="width-full height-full flex flex-col p-4">
            <div className="flex items-center justify-between mb-4">
                <h1 className="text-2xl font-bold">Danh sách dịch vụ</h1>
                <button
                    className="w-auto bg-blue-500 hover:bg-blue-700 disabled:bg-gray-400 text-white font-bold py-2 px-4 rounded"
                    onClick={() => void fetchServices()}
                    disabled={loading}
                >
                    {loading ? "Đang tải..." : "Cập nhật"}
                </button>
            </div>

            {error && <div className="mb-4 rounded border border-red-300 bg-red-50 p-3 text-red-700">{error}</div>}

            <div className="mb-4 flex flex-wrap gap-3">
                <input
                    type="search"
                    className="min-w-[240px] flex-1 rounded border border-gray-300 p-2"
                    placeholder="Tìm theo tên hoặc ID dịch vụ"
                    value={searchTerm}
                    onChange={(event) => setSearchTerm(event.target.value)}
                    aria-label="Tìm kiếm dịch vụ theo tên hoặc ID"
                />
                <select
                    className="rounded border border-gray-300 p-2"
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

            <div className="overflow-x-auto">
                <table className="w-full text-left border-collapse border-[2px] border-gray-900">
                    <thead className="bg-blue-500 text-white">
                        <tr>
                            <th className="p-2 text-center border-[2px] border-gray-900">ID</th>
                            <th className="p-2 border-[2px] border-gray-900">Tên dịch vụ</th>
                            <th className="p-2 border-[2px] border-gray-900">Tên thực</th>
                            <th className="p-2 border-[2px] border-gray-900">Danh mục</th>
                            <th className="p-2 text-center border-[2px] border-gray-900">Hoạt động</th>
                        </tr>
                    </thead>
                    <tbody>
                        {loading ? (
                            <tr><td className="p-4 text-center" colSpan={5}>Đang tải danh sách dịch vụ...</td></tr>
                        ) : services.length === 0 ? (
                            <tr><td className="p-4 text-center" colSpan={5}>Chưa có dịch vụ nào.</td></tr>
                        ) : filteredServices.length === 0 ? (
                            <tr><td className="p-4 text-center" colSpan={5}>Không tìm thấy dịch vụ phù hợp.</td></tr>
                        ) : filteredServices.map((service) => (
                            <tr key={service.serviceID} className="border-gray-900 border-[2px]">
                                <td className="p-2 text-center">{service.serviceID}</td>
                                <td className="p-2">{service.title}</td>
                                <td className="p-2">{service.realTitle}</td>
                                <td className="p-2">{service.category}</td>
                                <td className="p-2 text-center">
                                    <input
                                        type="checkbox"
                                        className="h-5 w-5 cursor-pointer accent-blue-600 disabled:cursor-not-allowed"
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