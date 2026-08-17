import { BrowserRouter, Routes, Route } from "react-router-dom";
import Homepage from "../pages/homePage/index.tsx";
import ScannerPage from "../pages/scannerPage/index.tsx";
import InfoPage from "../pages/infoPage/index.tsx";
import ServicePage from "../pages/servicePage/index.tsx";

export default function Routers() {
  return (
    <>
        <BrowserRouter>
            <Routes>
                <Route path="/" element={<Homepage />}>
                    <Route path="info" element={<InfoPage />} />
                    <Route path="service" element={<ServicePage />} />
                    <Route path="paper" element={<div>Paper Page</div>} />
                    <Route path="scanner" element={<ScannerPage />} />
                </Route>
            </Routes>
        </BrowserRouter>
    </>
  )
}