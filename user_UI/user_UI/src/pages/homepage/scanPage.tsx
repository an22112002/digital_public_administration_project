import { useState } from 'react'
import Header from '../../header/header'

export default function ScanPage() {
  type DocumentItem = {
    id: string
    name: string
    status: 'done' | 'pending' | 'processing'
    color: string
  }

  type DocumentType = 'CCCD' | 'Giấy phép lái xe'

  const [selectedScanner, setSelectedScanner] = useState('Máy quét 01')
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [scannedFiles, setScannedFiles] = useState<DocumentItem[]>([
    { id: 'scan_001.jpg', name: 'scan_001.jpg', status: 'done', color: 'bg-emerald-500' },
    { id: 'scan_002.jpg', name: 'scan_002.jpg', status: 'done', color: 'bg-emerald-500' },
    { id: 'scan_003.jpg', name: 'scan_003.jpg', status: 'pending', color: 'bg-amber-400' },
    { id: 'scan_004.jpg', name: 'scan_004.jpg', status: 'processing', color: 'bg-blue-500' },
  ])

  const documentSummary = [
    'scan_001.jpg',
    'scan_002.jpg',
    'scan_003.jpg',
  ]

  const documentTypes: DocumentType[] = ['CCCD', 'Giấy phép lái xe']

  const handleAddDocument = (type: DocumentType) => {
    const nextIndex = scannedFiles.length + 1
    const newFile: DocumentItem = {
      id: `scan_${String(nextIndex).padStart(3, '0')}.jpg`,
      name: `scan_${String(nextIndex).padStart(3, '0')}.jpg`,
      status: 'pending',
      color: 'bg-amber-400',
    }

    setScannedFiles((current) => [...current, newFile])
    setIsModalOpen(false)
    console.log(`Đã thêm tài liệu: ${type} -> ${newFile.name}`)
  }

  return (
    <div className="min-h-screen bg-[#eef5f4] px-4 py-8 text-slate-800">
      <div className="mx-auto max-w-6xl">
        <Header />

        <main className="rounded-[30px] bg-white p-5 shadow-[0_30px_70px_rgba(15,23,42,0.08)] ring-1 ring-slate-100 md:p-8">
          <div className="grid gap-6 xl:grid-cols-[1.35fr_0.65fr]">
            <section className="rounded-[24px] bg-[#f4fbfb] p-5 ring-1 ring-[#dfeff1]">
              <h2 className="mb-5 text-2xl font-bold text-slate-800">File quét</h2>

              <div className="grid gap-4 sm:grid-cols-2">
                {scannedFiles.map((file) => (
                  <div
                    key={file.id}
                    className="rounded-[18px] border border-[#dfecef] bg-white/80 p-4 shadow-[0_12px_28px_rgba(15,23,42,0.04)]"
                  >
                    <div className="mb-3 flex items-center justify-between">
                      <span className="text-sm font-medium text-slate-600">{file.name}</span>
                      <span className={`h-3.5 w-3.5 rounded-full ${file.color}`} />
                    </div>
                    <div className="h-20 rounded-2xl bg-gradient-to-br from-[#effaf7] via-[#f4fbfb] to-[#edf5ff]" />
                  </div>
                ))}
              </div>
            </section>

            <aside className="rounded-[24px] bg-[#f4fbfb] p-5 ring-1 ring-[#dfeff1]">
              <div className="mb-5 flex items-center justify-between gap-3">
                <h2 className="text-2xl font-bold text-slate-800">Tài liệu</h2>
                <button
                  type="button"
                  onClick={() => setIsModalOpen(true)}
                  className="rounded-full bg-[#eafaf6] px-3 py-2 text-sm font-semibold text-[#118a67] transition hover:bg-[#dff7f0]"
                >
                  Thêm tài liệu
                </button>
              </div>

              <div className="space-y-3">
                {documentSummary.map((item) => (
                  <div
                    key={item}
                    className="rounded-2xl border border-[#dfecef] bg-white/90 px-4 py-3 text-sm font-medium text-slate-700 shadow-sm"
                  >
                    {item}
                  </div>
                ))}
              </div>
            </aside>
          </div>

          <div className="mt-8 flex items-center justify-between gap-4 border-t border-slate-200 pt-5">
            <div className="flex items-center gap-3">
              <label className="text-sm font-medium text-slate-600" htmlFor="scanner-select">
                Máy quét
              </label>
              <select
                id="scanner-select"
                value={selectedScanner}
                onChange={(event) => setSelectedScanner(event.target.value)}
                className="rounded-xl border border-slate-200 bg-white px-3 py-2.5 text-sm font-medium text-slate-700 shadow-sm outline-none transition focus:border-[#32b5b8]"
              >
                <option>Máy quét 01</option>
                <option>Máy quét 02</option>
                <option>Máy quét 03</option>
              </select>
            </div>

            <div className="flex items-center gap-3">
              <button className="inline-flex items-center justify-center rounded-[16px] bg-[#28a9a9] px-8 py-3.5 text-base font-semibold text-white shadow-[0_12px_30px_rgba(40,169,169,0.35)] transition hover:bg-[#219a9a]">
                Quét
              </button>

              <button className="inline-flex items-center justify-center rounded-[16px] bg-[#1ea56d] px-8 py-3.5 text-base font-semibold text-white shadow-[0_12px_30px_rgba(30,165,109,0.3)] transition hover:bg-[#17945f]">
                Nộp hồ sơ
              </button>
            </div>
          </div>
        </main>
      </div>

      {isModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/40 px-4">
          <div className="w-full max-w-md rounded-[24px] bg-white p-6 shadow-[0_30px_80px_rgba(15,23,42,0.2)]">
            <div className="mb-5 flex items-center justify-between">
              <h3 className="text-xl font-bold text-slate-800">Chọn loại giấy tờ</h3>
              <button
                type="button"
                onClick={() => setIsModalOpen(false)}
                className="text-xl font-medium text-slate-400 transition hover:text-slate-600"
              >
                ×
              </button>
            </div>

            <div className="space-y-3">
              {documentTypes.map((type) => (
                <button
                  key={type}
                  type="button"
                  onClick={() => handleAddDocument(type)}
                  className="flex w-full items-center justify-between rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-left text-base font-medium text-slate-700 transition hover:border-[#32b5b8] hover:bg-[#f0fbfb]"
                >
                  <span>{type}</span>
                  <span className="text-sm text-slate-400">→</span>
                </button>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
