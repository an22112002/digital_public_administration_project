import { useEffect, useState, type ReactNode } from 'react'
import dv_cong from '../assets/dv_cong_so.jpg'
import { getTitle } from '../api/settingAPI'

type HeaderProps = {
  title?: string
  subtitle?: string
  action?: ReactNode
}

export default function Header({
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
    <header className="mb-8 flex items-center justify-between border-b border-slate-200 pb-5">
      <div className="flex items-center gap-3">
        <div className="flex h-12 w-12 items-center justify-center overflow-hidden rounded-2xl bg-gradient-to-br from-[#32b5b8] to-[#1e7bd8] shadow-md shadow-cyan-200">
          <img
            src={dv_cong}
            alt="DV Cong So Logo"
            className="h-full w-full object-cover"
          />
        </div>
        <div>
          <p className="text-xs font-semibold uppercase tracking-[0.22em] text-slate-400">HỖ TRỢ THỰC HIỆN DỊCH VỤ CÔNG</p>
          <h1 className="text-xl font-bold tracking-tight text-slate-800">{pageTitle}</h1>
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
  if (url.pathname === '/') {
   return false;
  }
  return true;
}