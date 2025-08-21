import {BrowserRouter, Routes, Route, Navigate} from "react-router-dom"
import { AdyenUploadPage } from "./pages/Adyen";
import { PXG } from "./pages/navigation";
import Layout from "./components/layout";
import { Canada } from "./pages/Canada";
import { Shopify } from "./pages/Shopify";
import { Ferrule } from "./pages/Ferrule";
import { GlobalPayments } from "./pages/GlobalP";
import { Spec } from "./pages/Spec";
import { Defect } from "./pages/Defect&Warranty";
import { Loomis } from "./pages/Loomis";

function App() {
  return (
    <BrowserRouter>
      <Routes>
        {/* Redirección */}
        <Route path="/" element={<Navigate to="/pxgboost" replace />} />

        {/* Ruta padre con Layout */}
        <Route path="/" element={<Layout />}>
          <Route path="pxgboost" element={<PXG />} />
          <Route path="Adyen" element={<AdyenUploadPage />} />
          <Route path="Canada" element={<Canada />} />
          <Route path="Shopify" element={<Shopify />} />
          <Route path="Ferrule" element={<Ferrule />} />
          <Route path="GlobalPayments" element={<GlobalPayments />} />
          <Route path="Spec" element={<Spec />} />
          <Route path="Defect" element={<Defect />} />  
          <Route path="Loomis" element={<Loomis />} />          
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

export default App;