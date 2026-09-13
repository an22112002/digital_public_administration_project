import type { Service } from '../../interface/services'

export default function ServiceBtn({ service }: { service: Service }) {
  return (
    <div className="group relative flex h-full min-h-[138px] cursor-pointer flex-col justify-center rounded-[14px] border border-[#f8b879] bg-[#ffd7aa] px-6 py-5 text-center shadow-[0_8px_20px_rgba(15,23,42,0.05)] transition-all duration-300 hover:bg-[#f6ac6e] hover:shadow-[0_0_0_3px_rgba(162,74,10,0.12)]">
      <span className="absolute right-3 top-3 flex h-8 w-8 items-center justify-center rounded-full border border-[#a24a0a] bg-[#fffaf4]/85 text-[18px] text-[#a24a0a] opacity-85 transition-all duration-500 animate-pulse">
        👆
      </span>

      <div className="mb-2 text-[16px] font-black uppercase tracking-[0.02em] text-[#4c2a0d]">
        {service.category}
      </div>

      <div className="text-[16px] font-medium leading-6 text-[#44280f]">
        {service.name}
      </div>
    </div>
  )
}