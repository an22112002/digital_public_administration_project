import { BrowserRouter, Routes, Route } from "react-router-dom";
import Homepage from "../pages/homePage/index.tsx";
import ScannerPage from "../pages/scannerPage/index.tsx";
import InfoPage from "../pages/infoPage/index.tsx";
import ModePage from "../pages/modePage/index.tsx";
import ServicePage from "../pages/servicePage/index.tsx";
import LLMPage from "../pages/LLMPage/index.tsx";

export default function Routers() {
  return (
    <>
        <BrowserRouter>
            <Routes>
                <Route path="/" element={<Homepage />}>
                    <Route path="info" element={<InfoPage />} />
                    <Route path="service" element={<ServicePage />} />
                    <Route path="llm" element={<LLMPage />} />
                    <Route path="mode" element={<ModePage />} />
                    <Route path="scanner" element={<ScannerPage />} />
                </Route>
            </Routes>
        </BrowserRouter>
    </>
  )
}