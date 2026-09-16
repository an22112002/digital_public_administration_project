import { BrowserRouter, Routes, Route } from 'react-router-dom';
import HomePage from '../pages/homepage';
import KiotsHomePage from '../pages/homepage/kiots';
import ScanPage from '../pages/scanpage';
import KiotsScanPage from '../pages/scanpage/kiots';

export default function Routers() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/desktop">
          <Route index element={<HomePage />} />
          <Route path="scan/:serviceID" element={<ScanPage />} />
        </Route>
        <Route path="/kiosk">
          <Route index element={<KiotsHomePage />} />
          <Route path="scan/:serviceID" element={<KiotsScanPage />} />
        </Route>
      </Routes>
    </BrowserRouter>
  )
}