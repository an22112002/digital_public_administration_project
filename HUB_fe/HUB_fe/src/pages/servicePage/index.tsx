import { importFileXLSX } from "../../api/serviceAPI";
import { useState } from "react";

export default function ServicePage() {
    const [file, setFile] = useState<File | null>(null);

    const handleFileUpload = async () => {
        if (file) {
            const response = await importFileXLSX(file);
            if (response.success) {
                alert("File đã được tải lên và xử lý thành công.");
            } else {
                alert(`Lỗi khi xử lý file: ${response.message}`);
            }
        }
    }

    return (
        <div className="width-full height-full flex flex-col p-4">
            <div className="w-full h-auto p-4 grid grid-cols-2 gap-4">
                <div className="p-2 border rounded">
                    <div className="font-bold text-lg text-gray-600">Cập nhật dịch vụ</div>
                </div>
                {/* tải file lên xử lý */}
                <div>
                    <div className="p-2 border rounded">
                        <div className="font-bold text-lg text-gray-600">Tải file lên</div>
                        <input type="file"
                            className="w-full p-2 border-[1px] border-gray-300 rounded"
                            onChange={(e) => {
                                const file = e.target.files?.[0];
                                if (file) {
                                    setFile(file);
                                }
                            }}
                        />

                        <button
                            className="bg-blue-500 text-white p-2 rounded hover:bg-blue-600 mt-2"
                            onClick={async () => await handleFileUpload()}
                        >
                            Tải lên và xử lý
                        </button>
                    </div>
                </div>
            </div>
        </div>
    );
}