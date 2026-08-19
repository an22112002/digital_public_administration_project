import type { ReactNode } from 'react'
import aiBootsLogo from '../assets/ai boots.png'

type HeaderProps = {
  title?: string
  subtitle?: string
  action?: ReactNode
}

export default function Header({
  title = 'Xã Nam Cường',
  subtitle = 'Kiosk',
  action,
}: HeaderProps) {
  return (
    <header className="mb-8 flex items-center justify-between rounded-[22px] bg-white/80 px-5 py-4 shadow-sm backdrop-blur-sm">
      <div className="flex items-center gap-3">
        <div className="flex h-12 w-12 items-center justify-center overflow-hidden rounded-2xl bg-gradient-to-br from-[#32b5b8] to-[#1e7bd8] shadow-md shadow-cyan-200">
          <img
            src={aiBootsLogo}
            alt="AI Boots Logo"
            className="h-full w-full object-cover"
          />
        </div>
        <div>
          <p className="text-[10px] font-medium uppercase tracking-[0.24em] text-slate-400">{subtitle}</p>
          <h1 className="text-xl font-bold text-slate-800">{title}</h1>
        </div>
      </div>

      {action ?? (
        <button className="inline-flex items-center gap-2 rounded-full bg-[#edf4ff] px-4 py-2 text-sm font-medium text-[#2d6cdf] shadow-sm transition hover:bg-[#e1edff]">
          <span className="text-base">?</span>
          Hướng dẫn
        </button>
      )}
    </header>
  )
}
