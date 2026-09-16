import { BrowserRouter, Routes, Route } from 'react-router-dom';
import HomePage from '../pages/homepage';
import KioskHomePage from '../pages/homepage/kiosk';
import ScanPage from '../pages/scanpage';
import KioskScanPage from '../pages/scanpage/kiosk';

export default function Routers() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/desktop">
          <Route index element={<HomePage />} />
          <Route path="scan/:serviceID" element={<ScanPage />} />
        </Route>
        <Route path="/kiosk">
          <Route index element={<KioskHomePage />} />
          <Route path="scan/:serviceID" element={<KioskScanPage />} />
        </Route>
      </Routes>
    </BrowserRouter>
  )
}
