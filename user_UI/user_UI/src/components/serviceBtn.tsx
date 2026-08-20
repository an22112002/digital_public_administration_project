import type { Service } from '../api/servicesAPI';

export default function ServiceBtn({ service }: { service: Service }) {
    return (
        <div className="cursor-pointer rounded-xl border border-slate-200 bg-white p-4 shadow-sm transition-shadow duration-300 hover:shadow-md">
            <h3 className="text-sm font-semibold text-slate-800">{service.title}</h3>
            <p className="mt-2 text-xs leading-5 text-slate-500">{service.realTitle}</p>
        </div>
    )
}