import { useMemo, useState } from 'react';
import { Link } from 'react-router-dom';
import Header from '../../header/header';
import aiBootsImage from '../../assets/ai boots.png';
import type { Service } from '../../interface/services';
import ServiceBtn from './serviceBtn';

const data: Service[] = [
  {
    id: '01',
    name: 'Chứng thực bản sao',
    description: 'Thực hiện chứng thực bản sao giấy tờ, văn bản từ bản chính theo quy định.',
    category: 'Chứng thực'
  },
  {
    id: '02',
    name: 'Chứng thực chữ ký',
    description: 'Thực hiện chứng thực chữ ký trong giấy tờ, văn bản theo quy định.',
    category: 'Chứng thực'
  },
  { id: '03', name: 'Đăng ký kết hôn', description: 'Thực hiện thủ tục đăng ký kết hôn theo quy định của pháp luật.', category: 'Hộ tịch' },
  { id: '04', name: 'Cấp giấy chứng nhận an toàn thực phẩm', description: 'Đăng ký cấp giấy chứng nhận cơ sở đủ điều kiện an toàn thực phẩm.', category: 'An toàn thực phẩm' },
  { id: '05', name: 'Xác nhận tình trạng hôn nhân', description: 'Cấp xác nhận tình trạng hôn nhân phục vụ các thủ tục hành chính.', category: 'Hộ tịch' },
  { id: '06', name: 'Thủ tục đăng ký khai sinh', description: 'Đăng ký khai sinh và cấp giấy khai sinh cho trẻ em.', category: 'Hộ tịch' }
]

export default function HomePage() {
  const [searchTerm, setSearchTerm] = useState('');

  const filteredServices = useMemo(() => {
    const normalizedValue = searchTerm.trim().toLowerCase();

    return data.filter((service) => {
      const serviceName = service.name.toLowerCase();
      const serviceDescription = service.description.toLowerCase();

      return !normalizedValue || serviceName.includes(normalizedValue) || serviceDescription.includes(normalizedValue);
    });
  }, [searchTerm]);

  return (
    <div className="min-h-screen bg-[#f3f7f5] text-slate-800">
      <div className="mx-auto max-w-[1440px] px-4 py-5 md:px-6 lg:px-8">
        <Header />

        <main className="space-y-8">
          <section className="overflow-hidden rounded-[30px] bg-gradient-to-br from-[#edfdfc] via-white to-[#eef4ff] p-5 shadow-[0_28px_80px_rgba(15,23,42,0.06)] ring-1 ring-slate-100 md:p-8 lg:p-10">
            <div className="grid items-center gap-8 lg:grid-cols-[1.2fr_0.8fr]">
              <div className="space-y-6">
                <div className="inline-flex items-center rounded-full border border-teal-200 bg-white/70 px-3 py-1 text-xs font-semibold uppercase tracking-[0.18em] text-teal-700 shadow-sm">
                  Dịch vụ công trực tuyến
                </div>

                <div className="space-y-4">
                  <h1 className="max-w-xl text-3xl font-black leading-tight tracking-tight text-slate-900 md:text-5xl">
                    Bạn muốn thực hiện thủ tục nào hôm nay?
                  </h1>
                  <p className="max-w-lg text-base leading-7 text-slate-600 md:text-lg">
                    Tìm nhanh, thực hiện đúng quy trình và hoàn tất thủ tục một cách thuận tiện, an toàn và hiệu quả.
                  </p>
                </div>

                <div className="w-full max-w-2xl">
                  <label htmlFor="service-search" className="sr-only">
                    Tìm kiếm thủ tục
                  </label>
                  <div className="flex items-center gap-3 rounded-[18px] border border-slate-200 bg-white px-4 py-3 shadow-[0_12px_24px_rgba(15,23,42,0.04)] transition focus-within:border-teal-400 focus-within:shadow-[0_18px_32px_rgba(13,148,136,0.12)]">
                    <svg
                      aria-hidden="true"
                      viewBox="0 0 24 24"
                      className="h-5 w-5 flex-shrink-0 text-slate-400"
                      fill="none"
                      stroke="currentColor"
                      strokeWidth="1.8"
                    >
                      <circle cx="11" cy="11" r="6" />
                      <path d="m16 16 4 4" strokeLinecap="round" />
                    </svg>
                    <input
                      id="service-search"
                      type="search"
                      value={searchTerm}
                      onChange={(event) => setSearchTerm(event.target.value)}
                      placeholder="Tìm kiếm thủ tục, ví dụ: kết hôn, khai sinh..."
                      className="w-full border-0 bg-transparent text-sm text-slate-700 placeholder:text-slate-400 focus:outline-none md:text-base"
                    />
                  </div>
                </div>

              </div>

              <div className="flex justify-center lg:justify-end">
                <div className="relative w-full max-w-[420px] rounded-[28px] border border-slate-200 bg-white/80 p-4 shadow-[0_22px_50px_rgba(15,23,42,0.08)] backdrop-blur-sm">
                  <div className="absolute -left-3 top-8 h-16 w-16 rounded-full bg-teal-100 blur-2xl" />
                  <div className="absolute -right-3 bottom-10 h-20 w-20 rounded-full bg-blue-100 blur-2xl" />
                  <div className="relative flex w-full items-center justify-center rounded-[22px] border border-slate-200 bg-[#eef5f5] p-3">
                    <img
                      src={aiBootsImage}
                      alt="AI Boots"
                      className="h-[260px] w-auto object-contain"
                    />
                  </div>
                </div>
              </div>
            </div>
          </section>

          <section id="services" className="rounded-[28px] bg-white p-4 shadow-[0_16px_40px_rgba(15,23,42,0.04)] ring-1 ring-slate-100 md:p-6 lg:p-8">
            <div className="mb-6 flex flex-col gap-2 md:flex-row md:items-end md:justify-between">
              <div>
                <p className="text-xs font-semibold uppercase tracking-[0.2em] text-slate-400">Danh mục</p>
                <h2 className="mt-2 text-2xl font-bold text-slate-900">Thủ tục phổ biến</h2>
              </div>
              <div className="text-sm text-slate-500">
                {filteredServices.length} thủ tục
              </div>
            </div>

            {filteredServices.length > 0 ? (
              <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
                {filteredServices.map((service) => (
                  <Link key={service.id} to={service.name === 'Đăng ký kết hôn' ? '/wedding' : '/scan'} className="block h-full">
                    <ServiceBtn service={service} />
                  </Link>
                ))}
              </div>
            ) : (
              <div className="rounded-[20px] border border-dashed border-slate-300 bg-slate-50 px-4 py-10 text-center text-sm text-slate-500">
                Không tìm thấy thủ tục phù hợp.
              </div>
            )}
          </section>
        </main>
      </div>
    </div>
  )
}