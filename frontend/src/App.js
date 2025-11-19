import "@/App.css";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { AuthProvider, useAuth } from "@/context/AuthContext";
import Layout from "@/components/Layout";
import Dashboard from "@/pages/Dashboard";
import Reservations from "@/pages/Reservations";
import Operations from "@/pages/Operations";
import Management from "@/pages/Management";
import Flights from "@/pages/Flights";
import Hotels from "@/pages/Hotels";
import Admin from "@/pages/Admin";
import Login from "@/pages/Login";

// Protected Route Component
const ProtectedRoute = ({ children, page }) => {
  const { isAuthenticated, canAccessPage, loading } = useAuth();

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  if (page && !canAccessPage(page)) {
    return <Navigate to="/" replace />;
  }

  return children;
};

function AppRoutes() {
  const { isAuthenticated, loading } = useAuth();

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  return (
    <Routes>
      <Route 
        path="/login" 
        element={isAuthenticated ? <Navigate to="/" replace /> : <Login />} 
      />
      <Route 
        path="/" 
        element={
          <ProtectedRoute>
            <Layout />
          </ProtectedRoute>
        }
      >
        <Route index element={<Dashboard />} />
        <Route 
          path="reservations" 
          element={
            <ProtectedRoute page="reservations">
              <Reservations />
            </ProtectedRoute>
          } 
        />
        <Route 
          path="operations" 
          element={
            <ProtectedRoute page="operations">
              <Operations />
            </ProtectedRoute>
          } 
        />
        <Route 
          path="management" 
          element={
            <ProtectedRoute page="management">
              <Management />
            </ProtectedRoute>
          } 
        />
        <Route 
          path="flights" 
          element={
            <ProtectedRoute page="flights">
              <Flights />
            </ProtectedRoute>
          } 
        />
        <Route 
          path="admin" 
          element={
            <ProtectedRoute page="admin">
              <Admin />
            </ProtectedRoute>
          } 
        />
      </Route>
    </Routes>
  );
}

function App() {
  return (
    <div className="App">
      <AuthProvider>
        <BrowserRouter>
          <AppRoutes />
        </BrowserRouter>
      </AuthProvider>
    </div>
  );
}

export default App;
