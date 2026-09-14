import { useEffect, useState, type ReactNode } from 'react'
import dv_cong from '../assets/dv_cong_so.jpg'
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
  const [pageTitle, setPageTitle] = useState<string>('');

  useEffect(() => {
    const fetchTitle = async () => {
      const title = await getTitle();
      setPageTitle(title.title);
    };
    fetchTitle();
  }, []);

  return (
    <header className="mb-8 flex items-center justify-between rounded-[10px] bg-gradient-to-r from-[#b61606] to-[#a32007] px-6 py-4 text-white shadow-[0_10px_30px_rgba(170,30,10,0.22)]">
      <div className="flex items-center gap-4">
        <div className="flex h-14 w-14 items-center justify-center overflow-hidden rounded-[12px] border border-white bg-white shadow-sm">
          <img
            src={dv_cong}
            alt="DV Cong So Logo"
            className="h-full w-full object-cover"
          />
        </div>
        <div>
          <p className="text-[11px] font-black uppercase tracking-[0.22em] text-[#fff5e7]">{subtitle}</p>
          <h1 className="mt-1 text-[24px] font-black tracking-tight text-white">{title ?? pageTitle}</h1>
        </div>
        {showBackButtonClick() && (
          <button className="inline-flex items-center gap-2 rounded-full bg-red-500 px-4 py-2 text-sm font-semibold text-white shadow-sm transition hover:bg-red-600"
            onClick={
              () => {
                window.history.back();
              }
            }
          >
            Trở lại
          </button>)}
      </div>

      {action ?? (
        <>
        </>
      )}
    </header>
  )
}

function showBackButtonClick() {
  const url = new URL(window.location.href);
  if (url.pathname === '/') {
   return false;
  }
  return true;
}