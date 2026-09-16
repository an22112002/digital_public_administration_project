import Header from '../../header/header';
import aiBootsImage from '../../assets/ai boots.png';
import type { Service } from '../../api/servicesAPI';
import ServiceBtn from '../../components/serviceBtn';
import { useEffect, useState } from 'react';
import { getServicesList, getCategories } from '../../api/servicesAPI';

export default function HomePage() {
  const [searchTerm, setSearchTerm] = useState('');
  const [services, setServices] = useState<Service[]>([]);
  const [categories, setCategories] = useState<string[]>([]);
  const [selectedCategory, setSelectedCategory] = useState('');

  useEffect(() => {
    const fetchCategories = async () => {
      try {
        const categoriesList = await getCategories();
        setCategories(categoriesList);
      } catch (error) {
        console.error('Error fetching categories:', error);
      }
    };

    fetchCategories();
  }, []);

  useEffect(() => {
    const fetchServices = async () => {
      try {
        const servicesList = await getServicesList(selectedCategory, searchTerm);
        setServices(servicesList);
      } catch (error) {
        console.error('Error fetching services:', error);
      }
    };

    fetchServices();
  }, [selectedCategory, searchTerm]);

  return (
    <div className="min-h-screen bg-[#fffaf4] text-slate-800">
      <div className="mx-auto max-w-[1440px] px-4 py-5 md:px-6 lg:px-8">
        <Header />

        <main className="space-y-8">
          <section className="overflow-hidden rounded-[30px] border border-[#ffd8ba] bg-gradient-to-r from-[#ffb86d] via-[#d65d12] to-[#8d3b05] p-4 shadow-[0_16px_50px_rgba(15,23,42,0.12)] md:p-8">
            <div className="grid items-center gap-8 lg:grid-cols-[1fr_320px]">
              <div className="space-y-6">
                <div className="flex w-full justify-center lg:justify-center">
                  <div className="inline-flex w-full max-w-[560px] items-center justify-center rounded-full border-2 border-white/90 bg-[#fffaf4] px-6 py-3 text-center text-[12px] font-black uppercase tracking-[0.22em] text-[#a84802] shadow-[0_12px_30px_rgba(0,0,0,0.18)] md:text-[14px]">
                    DỊCH VỤ CÔNG TRỰC TUYẾN
                  </div>
                </div>

                <div className="w-full space-y-4">
                  <h1 className="w-full text-3xl font-black leading-tight tracking-tight text-white md:text-5xl">
                    Bạn muốn thực hiện dịch vụ nào hôm nay?
                  </h1>
                </div>

                <div className="w-full max-w-2xl">
                  <label htmlFor="service-search" className="sr-only">
                    Tìm kiếm dịch vụ
                  </label>
                  <div className="flex items-center gap-3 rounded-[16px] border border-white/80 bg-white px-4 py-3 shadow-[0_12px_24px_rgba(15,23,42,0.04)]">
                    <svg
                      aria-hidden="true"
                      viewBox="0 0 24 24"
                      className="h-5 w-5 flex-shrink-0 text-slate-500"
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
                      placeholder="Tìm dịch vụ nhanh: khai sinh, kết hôn..."
                      className="w-full border-0 bg-transparent text-sm text-slate-700 placeholder:text-slate-400 focus:outline-none md:text-base"
                    />
                  </div>
                </div>

                <div className="w-full max-w-[280px]">
                  <select
                    value={selectedCategory}
                    onChange={(event) => setSelectedCategory(event.target.value)}
                    className="w-full rounded-[14px] border border-white/80 bg-white px-4 py-3 text-sm font-semibold text-slate-700 shadow-sm outline-none focus:border-orange-500"
                  >
                    <option value="">Tất Cả Dịch Vụ</option>
                    {categories.map((category) => (
                      <option key={category.toUpperCase()} value={category}>
                        {category.toUpperCase()}
                      </option>
                    ))}
                  </select>
                </div>
              </div>

              <div className="flex justify-center lg:justify-end">
                <div className="relative flex w-full max-w-[280px] items-center justify-center overflow-hidden rounded-[20px] bg-transparent p-0 shadow-none">
                  <img
                    src={aiBootsImage}
                    alt="Hỗ trợ người dân"
                    className="h-[280px] w-full rounded-[20px] object-contain object-center"
                  />
                </div>
              </div>
            </div>
          </section>

          <section className="rounded-[28px] bg-[#fffaf4] p-4 shadow-[0_16px_40px_rgba(15,23,42,0.04)] ring-1 ring-[#f6d8be] md:p-6 lg:p-8">
            <div className="mb-6 flex flex-col gap-2 md:flex-row md:items-end md:justify-between">
              <div>
                <h2 className="mt-2 text-2xl font-bold text-[#9a3f03]">Các dịch vụ hỗ trợ</h2>
              </div>
              <div className="text-sm font-semibold text-[#a44d03]">
                {services.length} dịch vụ
              </div>
            </div>

            {services.length > 0 ? (
              <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
                {services.map((service, index) => (
                  <ServiceBtn key={service.serviceID} service={service} index={index + 1} />
                ))}
              </div>
            ) : (
              <div className="rounded-[20px] border border-dashed border-slate-300 bg-slate-50 px-4 py-10 text-center text-sm text-slate-500">
                Không tìm thấy dịch vụ phù hợp.
              </div>
            )}
          </section>
        </main>
      </div>
    </div>
  );
}
