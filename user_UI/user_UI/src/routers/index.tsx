import { BrowserRouter, Routes, Route } from 'react-router-dom';
import HomePage from '../pages/homepage';
import ScanPage from '../pages/scanpage';

export default function Routers() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/desktop">
          <Route index element={<HomePage />} />
          <Route path="scan/:serviceID" element={<ScanPage />} />
        </Route>
        <Route path="/kiosk">
          {/* Giao diện Kiosk Homepage */}
          <Route index element={<HomePage />} /> 
          {/* Giao diện Kiosk Scan */}
          <Route path="scan/:serviceID" element={<ScanPage />} />
        </Route>
      </Routes>
    </BrowserRouter>
  )
}