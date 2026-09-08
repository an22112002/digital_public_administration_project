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
        <div className="width-full height-full flex flex-col p-4">
            <div className="w-full h-auto p-4">
                <div className="font-bold text-lg text-gray-600">Phần mềm NAPS2</div>
                <div className="grid grid-cols-3 gap-4">
                    {/* Đường dẫn NAPS2 */}
                    <span className="font-bold text-lg flex items-center ml-[20%]">Đường dẫn NAPS2</span>
                    <div className="p-2 border rounded col-span-2">
                        <div className="flex flex-row items-center space-x-2">
                            {changeNAPS2Path ? (
                                <button 
                                    className="bg-green-500 text-white p-2 rounded hover:bg-green-600"
                                    onClick={async () => {
                                        await handleNAPS2PathChange();
                                    }}
                                >
                                    Lưu
                                </button>
                            ) : (
                                <button className="bg-blue-500 text-white p-2 rounded hover:bg-blue-600" onClick={() => setChangeNAPS2Path(true)}>
                                    Sửa
                                </button>
                            )}&nbsp;
                            <input 
                                type="text" 
                                className="w-full p-2 border-[1px] border-gray-300 rounded" 
                                placeholder="Nhập đường dẫn NAPS2" 
                                disabled={!changeNAPS2Path}
                                value={NAPS2Path}
                                onChange={(e) => setNAPS2Path(e.target.value)}
                            />
                        </div>
                    </div>

                    {/* Trạng thái cài đặt NAPS2 */}
                    <span className="font-bold text-lg flex items-center ml-[20%]">Trạng thái cài đặt NAPS2</span>
                    <div className="p-2 border rounded col-span-2">
                        {installStatus}
                    </div>
                </div>
                

                <div className="font-bold text-lg text-gray-600">Danh sách máy scan tìm được</div>
                <table className="w-full text-left border-collapse border-[2px] border-gray-900">
                    <thead className="bg-blue-500 text-white">
                        <tr>
                            <th className="p-2 text-center border-[2px] border-gray-900" rowSpan={2}>Tên máy scan</th>
                            <th className="p-2 text-center border-[2px] border-gray-900" colSpan={3}>Driver</th>
                            <th className="p-2 text-center border-[2px] border-gray-900" rowSpan={2}>Trạng thái</th>
                        </tr>
                        <tr>
                            <th className="p-2 text-center border-[2px] border-gray-900">WIA</th>
                            <th className="p-2 text-center border-[2px] border-gray-900">TWAIN</th>
                            <th className="p-2 text-center border-[2px] border-gray-900">ESCL</th>
                        </tr>
                    </thead>
                    <tbody>
                        {devices && devices.length > 0 ? (
                            <>
                                {devices.map((device, index) => (
                                    <tr key={index} className="border-gray-900 border-[2px]">
                                        <td className="p-2 text-center">{device.name}</td>
                                        <td className="p-2 text-center">{device.driver.includes("WIA") ? "✔" : "✖"}</td>
                                        <td className="p-2 text-center">{device.driver.includes("TWAIN") ? "✔" : "✖"}</td>
                                        <td className="p-2 text-center">{device.driver.includes("ESCL") ? "✔" : "✖"}</td>
                                        <td className="p-2 text-center">{device.status === "connected" ? "Kết nối" : "Ngắt kết nối"}</td>
                                    </tr>
                                ))}
                            </>
                        ) : (
                            <tr>
                                <td className="p-2 text-center" colSpan={5}>
                                    Không tìm thấy máy scan nào.
                                </td>
                            </tr>
                        )}
                    </tbody>
                </table>
            </div>

            <div className="w-full h-auto p-4 flex justify-end">
                <button className="w-auto bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded" onClick={handleRefresh}>
                    Cập nhật
                </button>
            </div>
        </div>
    )
}
