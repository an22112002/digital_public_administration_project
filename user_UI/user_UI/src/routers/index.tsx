import { BrowserRouter, Routes, Route } from 'react-router-dom';
import HomePage from '../pages/homepage';
import ScanPage from '../pages/scanpage';
import WeddingPage from '../pages/homepage/weddingPage';

export default function Routers() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/scan/:servicesID" element={<ScanPage />} />
        <Route path="/wedding" element={<WeddingPage />} />
      </Routes>
    </BrowserRouter>
  )
}