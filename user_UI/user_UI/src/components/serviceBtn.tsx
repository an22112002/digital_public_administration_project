import type { Service } from '../api/servicesAPI';
import { useNavigate } from 'react-router-dom';

export default function ServiceBtn({
  service,
  index = 1,
  scanPath = '/desktop/scan',
}: {
  service: Service;
  index?: number;
  scanPath?: string;
}) {
  const navigate = useNavigate();

  return (
    <div
      className="group relative flex h-full min-h-[140px] cursor-pointer flex-col justify-center rounded-[10px] border border-[#e7a666] bg-[#ffbd89] px-6 py-5 text-center shadow-[0_4px_10px_rgba(15,23,42,0.03)] transition-all duration-300 hover:bg-[#ffeedd] hover:shadow-[0_0_0_3px_rgba(162,74,10,0.15),0_8px_20px_rgba(162,74,10,0.16)]"
      onClick={() => navigate(`${scanPath}/${service.serviceID}`)}
      title="Chọn dịch vụ"
    >
      <span className="absolute right-2 top-2 flex h-9 w-9 items-center justify-center rounded-full border border-[#d09b6b] bg-[#ffeedd]/80 text-[20px] text-[#a24a0a]/80 shadow-sm opacity-80 transition-all duration-500 animate-pulse">
        👆
      </span>

      <div className="mb-2 text-[15px] font-bold uppercase tracking-[0.04em] text-[#a24a0a]">
        {service.category.toUpperCase()}
      </div>

      <div className="text-[15px] font-medium leading-6 text-[#40250e]">
        <span className="mr-2 inline-flex h-7 min-w-[28px] items-center justify-center rounded-full bg-[#a24a0a] px-2 text-[12px] font-black text-white shadow-sm">
          {index}
        </span>
        {service.title}
      </div>
    </div>
  );
}
