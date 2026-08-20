import { useState } from 'react'
import Header from '../../header/header'

type DocumentItem = {
  id: string
  name: string
  status: 'done' | 'pending'
  color: string
}

type DocumentType = 'CCCD của bên nam' | 'CCCD của bên nữ' | 'Giấy xác nhận tình trạng hôn nhân'

const documentTypes: DocumentType[] = [
  'CCCD của bên nam',
  'CCCD của bên nữ',
  'Giấy xác nhận tình trạng hôn nhân',
]

export default function WeddingPage() {
  const [selectedScanner, setSelectedScanner] = useState('Máy quét 01')
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [scannedFiles, setScannedFiles] = useState<DocumentItem[]>([
    { id: 'wedding_001.jpg', name: 'wedding_001.jpg', status: 'done', color: 'bg-emerald-500' },
    { id: 'wedding_002.jpg', name: 'wedding_002.jpg', status: 'pending', color: 'bg-amber-400' },
  ])

  const handleAddDocument = (type: DocumentType) => {
    const nextIndex = scannedFiles.length + 1
    const newFile: DocumentItem = {
      id: `wedding_${String(nextIndex).padStart(3, '0')}.jpg`,
      name: `${type} - wedding_${String(nextIndex).padStart(3, '0')}.jpg`,
      status: 'pending',
      color: 'bg-amber-400',
    }

    setScannedFiles((current) => [...current, newFile])
    setIsModalOpen(false)
  }

  const handleRemoveDocument = (documentId: string) => {
    setScannedFiles((current) => current.filter((file) => file.id !== documentId))
  }

  return (
    <div className="min-h-screen bg-[#eef5f4] px-4 py-8 text-slate-800">
      <div className="mx-auto max-w-6xl">
        <Header />

        <main className="rounded-[30px] bg-white p-5 shadow-[0_30px_70px_rgba(15,23,42,0.08)] ring-1 ring-slate-100 md:p-8">
          <div className="mb-6 border-b border-slate-200 pb-5">
            <p className="text-sm font-semibold uppercase tracking-[0.18em] text-teal-600">Hộ tịch</p>
            <h1 className="mt-2 text-2xl font-bold text-slate-800 md:text-3xl">Thủ tục đăng ký kết hôn</h1>
            <p className="mt-2 text-sm text-slate-500">Quét và nộp giấy tờ cần thiết cho hồ sơ đăng ký kết hôn.</p>
          </div>

          <div className="grid gap-6 xl:grid-cols-[1.35fr_0.65fr]">
            <section className="rounded-[24px] bg-[#f4fbfb] p-5 ring-1 ring-[#dfeff1]">
              <h2 className="mb-5 text-2xl font-bold text-slate-800">File quét</h2>
              <div className="grid gap-4 sm:grid-cols-2">
                {scannedFiles.map((file) => (
                  <div key={file.id} className="rounded-[18px] border border-[#dfecef] bg-white/80 p-4 shadow-[0_12px_28px_rgba(15,23,42,0.04)]">
                    <div className="mb-3 flex items-center justify-between gap-3">
                      <span className="text-sm font-medium text-slate-600">{file.name}</span>
                      <div className="flex items-center gap-2">
                        <span className={`h-3.5 w-3.5 flex-shrink-0 rounded-full ${file.color}`} />
                        <button
                          type="button"
                          onClick={() => handleRemoveDocument(file.id)}
                          aria-label={`Xóa ${file.name}`}
                          title="Xóa tài liệu"
                          className="inline-flex h-7 w-7 flex-shrink-0 items-center justify-center rounded-full text-lg leading-none text-slate-400 transition hover:bg-rose-50 hover:text-rose-600"
                        >
                          ×
                        </button>
                      </div>
                    </div>
                    <div className="h-20 rounded-2xl bg-gradient-to-br from-[#effaf7] via-[#f4fbfb] to-[#edf5ff]" />
                  </div>
                ))}
              </div>
            </section>

            <aside className="rounded-[24px] bg-[#f4fbfb] p-5 ring-1 ring-[#dfeff1]">
              <div className="mb-5 flex items-center justify-between gap-3">
                <h2 className="text-2xl font-bold text-slate-800">Giấy tờ cần thiết</h2>
                <button type="button" onClick={() => setIsModalOpen(true)} className="rounded-full bg-[#eafaf6] px-3 py-2 text-sm font-semibold text-[#118a67] transition hover:bg-[#dff7f0]">
                  Thêm tài liệu
                </button>
              </div>
              <div className="space-y-3">
                {documentTypes.map((item) => (
                  <div key={item} className="rounded-2xl border border-[#dfecef] bg-white/90 px-4 py-3 text-sm font-medium text-slate-700 shadow-sm">
                    {item}
                  </div>
                ))}
              </div>
            </aside>
          </div>

          <div className="mt-8 flex flex-col gap-4 border-t border-slate-200 pt-5 sm:flex-row sm:items-center sm:justify-between">
            <div className="flex items-center gap-3">
              <label className="text-sm font-medium text-slate-600" htmlFor="wedding-scanner-select">Máy quét</label>
              <select id="wedding-scanner-select" value={selectedScanner} onChange={(event) => setSelectedScanner(event.target.value)} className="rounded-xl border border-slate-200 bg-white px-3 py-2.5 text-sm font-medium text-slate-700 shadow-sm outline-none transition focus:border-[#32b5b8]">
                <option>Máy quét 01</option>
                <option>Máy quét 02</option>
                <option>Máy quét 03</option>
              </select>
            </div>
            <div className="flex items-center gap-3">
              <button type="button" className="inline-flex items-center justify-center rounded-[16px] bg-[#1ea56d] px-8 py-3.5 text-base font-semibold text-white shadow-[0_12px_30px_rgba(30,165,109,0.3)] transition hover:bg-[#17945f]">Nộp hồ sơ</button>
            </div>
          </div>
        </main>
      </div>

      {isModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/40 px-4">
          <div className="w-full max-w-md rounded-[24px] bg-white p-6 shadow-[0_30px_80px_rgba(15,23,42,0.2)]">
            <div className="mb-5 flex items-center justify-between">
              <h3 className="text-xl font-bold text-slate-800">Chọn giấy tờ để quét</h3>
              <button type="button" onClick={() => setIsModalOpen(false)} className="text-xl font-medium text-slate-400 transition hover:text-slate-600" aria-label="Đóng">×</button>
            </div>
            <div className="space-y-3">
              {documentTypes.map((type) => (
                <button key={type} type="button" onClick={() => handleAddDocument(type)} className="flex w-full items-center justify-between rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-left text-base font-medium text-slate-700 transition hover:border-[#32b5b8] hover:bg-[#f0fbfb]">
                  <span>{type}</span>
                  <span className="text-sm text-slate-400">Quét và thêm</span>
                </button>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  )
}