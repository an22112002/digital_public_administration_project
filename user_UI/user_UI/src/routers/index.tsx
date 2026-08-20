import { BrowserRouter, Routes, Route } from 'react-router-dom';
import HomePage from '../pages/homepage';
import ScanPage from '../pages/scanpage';

export default function Routers() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/scan/:serviceID" element={<ScanPage />} />
      </Routes>
    </BrowserRouter>
  )
}