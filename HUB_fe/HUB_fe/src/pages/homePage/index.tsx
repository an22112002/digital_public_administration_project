import { Outlet } from "react-router-dom";
import { useNavigate } from "react-router-dom";

export default function Homepage() {
    const navigate = useNavigate();

    return (
        <div className="w-[100vw] h-[100vh] flex flex-row">
            {/* Navigator */}
            <nav className="w-64 bg-gray-800 text-white p-4">
                <div className="font-bold text-lg text-gray-600">Cài đặt</div>
                <ul className="space-y-3 padding-3">
                    <li className="hover:bg-gray-600 p-2 hover:text-blue-500 hover:cursor-pointer" onClick={() => navigate("/info")}>Thông tin</li>
                    <li className="hover:bg-gray-600 p-2 hover:text-blue-500 hover:cursor-pointer" onClick={() => navigate("/service")}>Dịch vụ</li>
                    <li className="hover:bg-gray-600 p-2 hover:text-blue-500 hover:cursor-pointer" onClick={() => navigate("/paper")}>Giấy tờ bổ sung</li>
                </ul>
                <div className="font-bold text-lg text-gray-600">Thiết bị ngoại vi</div>
                <ul className="space-y-3 padding-3">
                    <li className="hover:bg-gray-600 p-2 hover:text-blue-500 hover:cursor-pointer" onClick={() => navigate("/scanner")}>Máy scan</li>
                </ul>
            </nav>

            {/* Frame */}
            <div className="w-full p-4">
                <Outlet />
            </div>

        </div>
    );
}