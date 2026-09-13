import type { ReactNode } from 'react'
import aiBootsLogo from '../assets/dv_cong_so.jpg'

type HeaderProps = {
  title?: string
  subtitle?: string
  action?: ReactNode
}

export default function Header({
  title = 'Cấu hình chính của phần mềm hỗ trợ phần mềm',
  subtitle = 'HỖ TRỢ THỰC HIỆN DỊCH VỤ CÔNG',
  action,
}: HeaderProps) {
  return (
    <header className="mb-8 flex items-center justify-between rounded-[10px] bg-gradient-to-r from-[#b61606] to-[#a32007] px-6 py-4 text-white shadow-[0_10px_30px_rgba(170,30,10,0.22)]">
      <div className="flex items-center gap-4">
        <div className="flex h-14 w-14 items-center justify-center overflow-hidden rounded-[12px] border border-white bg-white shadow-sm">
          <img
            src={aiBootsLogo}
            alt="AI Boots Logo"
            className="h-full w-full object-cover"
          />
        </div>
        <div>
          <p className="text-[11px] font-black uppercase tracking-[0.22em] text-[#fff5e7]">{subtitle}</p>
          <h1 className="mt-1 text-[24px] font-black tracking-tight text-white">{title}</h1>
        </div>
      </div>

      {action ?? null}
    </header>
  )
}
