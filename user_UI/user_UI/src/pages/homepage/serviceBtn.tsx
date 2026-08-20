import type { Service } from "../../interface/services"

export default function ServiceBtn({ service }: { service: Service }) {
    return (
        <div className="group h-full cursor-pointer rounded-[22px] border border-slate-200 bg-gradient-to-br from-white to-slate-50 p-5 shadow-sm transition-all duration-300 hover:-translate-y-0.5 hover:border-teal-200 hover:shadow-[0_18px_35px_rgba(13,148,136,0.08)]">
            <div className="mb-4 flex items-center justify-between">
                <span className="inline-flex h-8 w-8 items-center justify-center rounded-full bg-teal-50 text-xs font-bold text-teal-700">
                    {service.id}
                </span>
                <span className="text-[10px] font-semibold uppercase tracking-[0.18em] text-slate-400 group-hover:text-teal-600">
                    Mở
                </span>
            </div>
            <h3 className="text-base font-semibold leading-6 text-slate-800">{service.name}</h3>
            <p className="mt-3 text-sm leading-6 text-slate-500">{service.description}</p>
        </div>
    )
}