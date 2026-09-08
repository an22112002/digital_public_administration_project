import type { Service } from '../api/servicesAPI';
import {useState} from "react";
import { InfoCircleOutlined, InfoCircleTwoTone } from "@ant-design/icons";
import { useNavigate } from "react-router-dom";

export default function ServiceBtn({ service, index }: { service: Service; index: number }) {
    const [showInfo, setShowInfo] = useState(false);
    const navigate = useNavigate();
    return (
        <div className="group h-full cursor-pointer rounded-[22px] border border-slate-200 bg-gradient-to-br from-white to-slate-50 p-5 shadow-sm transition-all duration-300 hover:-translate-y-0.5 hover:border-teal-200 hover:shadow-[0_18px_35px_rgba(13,148,136,0.08)]">
            <div className="mb-4 flex items-center justify-between">
                <span className="inline-flex h-8 w-8 items-center justify-center rounded-full bg-teal-50 text-xs font-bold text-teal-700">
                    {index + 1}
                </span>

                <div className="mt-2 flex items-center justify-between gap-2">
                    <span className="text-sm font-medium text-slate-600">{service.category.toUpperCase()}</span>
                    <button
                        onClick={() => setShowInfo(!showInfo)}
                        className="text-slate-400 hover:text-teal-600 focus:outline-none"
                    >
                        {showInfo ? <InfoCircleTwoTone twoToneColor="#0d9488" /> : <InfoCircleOutlined />}
                    </button>
                </div>
            </div>
            <h3 className="text-base font-semibold leading-6 text-slate-800 hover:text-teal-600cd ./"
                onClick={() => navigate(`/scan/${service.serviceID}`)}
            >{service.title}</h3>
            
            {showInfo && (
                <div className="mt-2 text-sm text-slate-600">
                    <p>Nội dung:</p>
                    <p>{service.realTitle}</p>
                </div>
            )}
        </div>
    )
}