import { useState, useEffect } from "react";
import { getTitle, saveTitle, getProvince, getCommune, listProvince, listCommune, saveNewPosition } from "../../api/settingAPI";
import type { ProvinceListResponse, CommuneListResponse } from "../../api/settingAPI";

export default function InfoPage() {
    const [title, setTitle] = useState("");
    const [changedTitle, setChangedTitle] = useState(false);
    const [province, setProvince] = useState("");
    const [commune, setCommune] = useState("");
    const [selectProvinceID, setSelectProvinceID] = useState<string | null>(null);
    const [selectCommuneID, setSelectCommuneID] = useState<string | null>(null);
    const [provinceArr, setProvinceArr] = useState<ProvinceListResponse>({ province_list: [] });
    const [communeArr, setCommuneArr] = useState<CommuneListResponse>({ commune_list: [] });
    const [changedPosition, setChangedPosition] = useState(false);

    const fetchTitle = async () => {
        const response = await getTitle();
        setTitle(response.title);
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
        load();
    }, []);

    const handleTitleChange = async () => {
        const response = await saveTitle(title);
        if (response.success) {
            alert("Tiêu đề đã được cập nhật thành công.");
            setChangedTitle(false);
        }
    }

    const handlePositionChange = async () => {
        if (selectProvinceID && selectCommuneID) {
            const response = await saveNewPosition(selectProvinceID, selectCommuneID);
            if (response.success) {
                alert("Vị trí đã được cập nhật thành công.");
                // Refresh the displayed province and commune after saving
                const saveProvince = await getProvince();
                setProvince(saveProvince.province);
                const saveCommune = await getCommune();
                setCommune(saveCommune.commune);
                setChangedPosition(false);
            }
        }
    }

    return (
        <div className="w-full h-full p-4">
            <h1 className="font-bold text-lg text-gray-600">THÔNG TIN</h1>
            <div className="grid grid-cols-3 gap-4">
                {/* TIÊU ĐỀ */}
                <span className="font-bold text-lg flex items-center ml-[20%]">Tiêu đề</span>
                <div className="p-2 border rounded col-span-2">
                    <div className="flex flex-row items-center space-x-2">
                        {changedTitle ? (
                            <button 
                                className="bg-green-500 text-white p-2 rounded hover:bg-green-600"
                                onClick={async () => {
                                    await handleTitleChange();
                                }}
                            >
                                Lưu
                            </button>
                        ) : (
                            <button className="bg-blue-500 text-white p-2 rounded hover:bg-blue-600" onClick={() => setChangedTitle(true)}>
                                Sửa
                            </button>
                        )}&nbsp;
                        <input 
                            type="text" 
                            className="w-full p-2 border-[1px] border-gray-300 rounded" 
                            placeholder="Nhập tiêu đề" 
                            disabled={!changedTitle}
                            value={title}
                            onChange={(e) => setTitle(e.target.value)}
                        />
                    </div>
                </div>

                {/* TỈNH THÀNH PHỐ */}
                <span className="font-bold text-lg flex items-center ml-[20%]">Tỉnh / Thành phố</span>
                <div className="p-2 border rounded col-span-2">
                    <div className="flex flex-row items-center space-x-2">
                        <select
                            className="w-full p-2 border-[1px] border-gray-300 rounded"
                            value={selectProvinceID || ""}
                            onChange={(e) => {
                                const selectedProvince = provinceArr.province_list.find(province => province.id === e.target.value);
                                if (selectedProvince) {
                                    setSelectProvinceID(selectedProvince.id);
                                    // Load communes for the selected province
                                    listCommune(selectedProvince.id).then((communeListResponse: CommuneListResponse) => {
                                        setCommuneArr(communeListResponse);
                                        // Reset commune selection
                                        setCommune("");
                                        setSelectCommuneID(null);
                                    });
                                }
                            }}
                            disabled={!changedPosition}
                        >
                            {provinceArr.province_list.map((option) => (
                                <option key={option.id} value={option.id}>
                                    {option.name}
                                </option>
                            ))}
                        </select>
                    </div>
                </div>

                {/* XÃ / PHƯỜNG */}
                <span className="font-bold text-lg flex items-center ml-[20%]">Xã / Phường</span>
                <div className="p-2 border rounded col-span-2">
                    <div className="flex flex-row items-center space-x-2">
                        <select
                            className="w-full p-2 border-[1px] border-gray-300 rounded"
                            value={selectCommuneID || ""}
                            onChange={(e) => {
                                const selectedCommune = communeArr.commune_list.find(commune => commune.id === e.target.value);
                                if (selectedCommune) {
                                    setSelectCommuneID(selectedCommune.id);
                                }
                            }}
                            disabled={!changedPosition}
                        >
                            {communeArr.commune_list.map((option) => (
                                <option key={option.id} value={option.id}>
                                    {option.name}
                                </option>
                            ))}
                        </select>
                    </div>
                </div>

                <div></div>
                <div className="p-2 border rounded col-span-2">
                    {changedPosition ? (
                        <button 
                            className="w-[50%] bg-green-500 text-white p-2 rounded hover:bg-green-600"
                            onClick={async () => {
                                await handlePositionChange();
                            }}
                        >
                            Lưu
                        </button>
                    ) : (
                        <button className="w-[50%] bg-blue-500 text-white p-2 rounded hover:bg-blue-600" onClick={() => setChangedPosition(true)}>
                            Sửa vị trí cơ quan
                        </button>
                    )}
                    <div>
                        <span className="font-bold">Vị trí cơ quan hiện tại: </span> {province} - {commune}
                    </div>
                </div>
            </div>
        </div>
    )
}