import React from "react";
import ReactDOM from "react-dom/client";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { Toaster } from "sonner";
import R20Page from "./pages/R20Page";
import "./index.css";

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <BrowserRouter>
      <Toaster position="top-right" richColors />
      <Routes>
        <Route path="/r20/input/:role" element={<R20Page />} />
        <Route path="*" element={<Navigate to="/r20/input/GH" replace />} />
      </Routes>
    </BrowserRouter>
  </React.StrictMode>,
);
