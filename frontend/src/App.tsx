import { Routes, Route, Navigate } from "react-router-dom";
import LoginPage from "./pages/LoginPage";
import DashboardPage from "./pages/DashboardPage";
import { useAuthStore } from "./stores/authStore";

const ProtectedRoute = ({ children }: { children: JSX.Element }) => {
  const token = useAuthStore((s) => s.accessToken);
  return token ? children : <Navigate to="/login" />;
};

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route
        path="/dashboard"
        element={
          <ProtectedRoute>
            <DashboardPage />
          </ProtectedRoute>
        }
      />
      <Route path="*" element={<Navigate to="/login" />} />
    </Routes>
  );
}
