import "@/App.css";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import Layout from "@/components/Layout";
import Dashboard from "@/pages/Dashboard";
import Reservations from "@/pages/Reservations";
import Management from "@/pages/Management";
import Flights from "@/pages/Flights";
import Admin from "@/pages/Admin";

function App() {
  return (
    <div className="App">
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Layout />}>
            <Route index element={<Dashboard />} />
            <Route path="reservations" element={<Reservations />} />
            <Route path="management" element={<Management />} />
            <Route path="flights" element={<Flights />} />
            <Route path="admin" element={<Admin />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </div>
  );
}

export default App;
