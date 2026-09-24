import { useEffect, useState, type ReactNode } from 'react'
import dv_cong from '../assets/images/dv_cong_so.jpg'
import { getTitle } from '../api/settingAPI'

type HeaderProps = {
  title?: string
  subtitle?: string
  action?: ReactNode
}

export default function Header({
  title,
  subtitle = 'HỖ TRỢ THỰC HIỆN DỊCH VỤ CÔNG',
  action,
}: HeaderProps) {
  const [pageTitle, setPageTitle] = useState<string>('Phần mềm hỗ trợ nhập liệu hồ sơ hành chính công');

  useEffect(() => {
    const fetchTitle = async () => {
      try {
        const title = await getTitle();
        if (title?.title) {
          setPageTitle(title.title);
        }
      } catch (error) {
        console.error('Error fetching title:', error);
      }
    };
    fetchTitle();
  }, []);

  return (
    <header className="mb-8 flex items-center justify-between rounded-[24px] border border-[#f7c7b5] bg-gradient-to-r from-[#e63a12] via-[#bd2517] to-[#921507] px-6 py-5 shadow-[0_12px_30px_rgba(170,30,10,0.2)]">
      <div className="flex items-center gap-4">
        <div className="flex h-14 w-14 items-center justify-center overflow-hidden rounded-2xl border border-white bg-white shadow-sm">
          <img
            src={dv_cong}
            alt="DV Cong So Logo"
            className="h-full w-full object-cover"
          />
        </div>
        <div className="min-w-0">
          <p className="text-[11px] font-black uppercase tracking-[0.22em] text-[#fff6e8]">{subtitle}</p>
          <h1 className="mt-1 text-xl font-black tracking-tight text-white">{title ?? pageTitle}</h1>
        </div>
        {showBackButtonClick() && (
          <button className="inline-flex items-center gap-2 rounded-full bg-white px-4 py-2 text-sm font-semibold text-[#a21608] shadow-sm transition hover:bg-[#ffe6dc]"
            onClick={() => {
              window.history.back();
            }}
          >
            Trở lại
          </button>
        )}
      </div>

      {action ?? (
        <>
          {/* <button className="inline-flex items-center gap-2 rounded-full bg-[#edf4ff] px-4 py-2 text-sm font-semibold text-[#2d6cdf] shadow-sm transition hover:bg-[#dfeeff]">
            Hướng dẫn
          </button> */}
        </>
      )}
    </header>
  )
}

function showBackButtonClick() {
  const url = new URL(window.location.href);
  if (url.pathname === '/' || url.pathname === '/desktop' || url.pathname === '/kiosk') {
   return false;
  }
  return true;
}
