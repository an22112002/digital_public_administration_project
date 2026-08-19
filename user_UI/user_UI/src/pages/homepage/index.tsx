import { Link } from 'react-router-dom';
import Header from '../../header/header';
import aiBootsImage from '../../assets/ai boots.png';
import type { Service } from '../../interface/services';
import ServiceBtn from './serviceBtn';

const data: Service[] = [
  {
    id: '1',
    name: 'Đăng ký kết hôn',
    description: 'Khai báo thông tin để thực hiện thủ tục đăng ký kết hôn theo quy định của pháp luật.'
  },
  {
    id: '2',
    name: 'Đăng ký khai sinh',
    description: 'Khai báo thông tin để cấp giấy khai sinh cho trẻ em mới sinh một cách nhanh chóng.'
  }
]

export default function HomePage() {
  return (
    <div className="min-h-screen bg-[#eef5f4] px-4 py-6 text-slate-800 md:px-8">
      <div className="mx-auto max-w-6xl">
        <Header />

        <main className="rounded-[30px] bg-white p-5 shadow-[0_30px_70px_rgba(15,23,42,0.08)] ring-1 ring-slate-100 md:p-8">
          <div className="mb-6 flex flex-col items-center justify-center gap-4">
            <div className="flex w-full max-w-[360px] items-center justify-center rounded-[18px] border border-slate-200 bg-[#eef5f5] p-3 shadow-sm">
              <img
                src={aiBootsImage}
                alt="AI Boots"
                className="h-[220px] w-auto object-contain"
              />
            </div>

            <h2 className="text-center text-2xl font-bold text-slate-800 md:text-4xl">
              Bạn muốn thực hiện thủ tục nào hôm nay?
            </h2>
          </div>

          <div className="grid gap-4 md:grid-cols-2">
            {data.map((service) => (
              <Link key={service.id} to="/scan" className="block">
                <ServiceBtn service={service} />
              </Link>
            ))}
          </div>
        </main>
      </div>
    </div>
  )
}