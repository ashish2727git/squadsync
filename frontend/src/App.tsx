import { Routes, Route, Navigate } from "react-router-dom";
import LoginPage from "./pages/LoginPage";
import { RegisterPage } from "./pages/RegisterPage";
import DashboardPage from "./pages/DashboardPage";
import { VaultPage } from "./pages/VaultPage";
import { ProfilePage } from "./pages/ProfilePage";
import { OnboardingPage } from "./pages/OnboardingPage";
import { SquadDetailPage } from "./pages/SquadDetailPage";
import { JoinSquadPage } from "./pages/JoinSquadPage";
import { WarRoomPage } from "./pages/WarRoomPage";
import { useAuthStore } from "./stores/authStore";
import { NotificationSystem } from "./components/NotificationSystem";
import { ErrorBoundary } from "./components/ErrorBoundary";

const ProtectedRoute = ({ children }: { children: JSX.Element }) => {
  const token = useAuthStore((s) => s.accessToken);
  return token ? children : <Navigate to="/login" />;
};

export default function App() {
  return (
    <ErrorBoundary>
      <NotificationSystem />
      <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route path="/register" element={<RegisterPage />} />
      <Route
        path="/dashboard"
        element={
          <ProtectedRoute>
            <DashboardPage />
          </ProtectedRoute>
        }
      />
      <Route
        path="/vault"
        element={
          <ProtectedRoute>
            <VaultPage />
          </ProtectedRoute>
        }
      />
      <Route
        path="/profile"
        element={
          <ProtectedRoute>
            <ProfilePage />
          </ProtectedRoute>
        }
      />
      <Route
        path="/onboarding"
        element={
          <ProtectedRoute>
            <OnboardingPage />
          </ProtectedRoute>
        }
      />
      <Route
        path="/squads/:squadId"
        element={
          <ProtectedRoute>
            <SquadDetailPage />
          </ProtectedRoute>
        }
      />
      <Route
        path="/join/:squadId"
        element={
          <ProtectedRoute>
            <JoinSquadPage />
          </ProtectedRoute>
        }
      />
      <Route
        path="/squads/:squadId/warroom"
        element={
          <ProtectedRoute>
            <WarRoomPage />
          </ProtectedRoute>
        }
      />
      <Route path="/" element={<Navigate to="/dashboard" />} />
      <Route path="*" element={<Navigate to="/login" />} />
    </Routes>
    </ErrorBoundary>
  );
}
