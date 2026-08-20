import { BrowserRouter, Routes, Route } from 'react-router-dom';
import HomePage from '../pages/homepage';
import ScanPage from '../pages/homepage/scanPage';
import WeddingPage from '../pages/homepage/weddingPage';

export default function Routers() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/scan" element={<ScanPage />} />
        <Route path="/wedding" element={<WeddingPage />} />
      </Routes>
    </BrowserRouter>
  )
}