import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.jsx'
import { createBrowserRouter, RouterProvider, Navigate } from 'react-router-dom'
import Dashboard from './modules/dashboard/dashboard.jsx'
import Profile from './modules/profile/profile.jsx'
import Users from './modules/users/users.jsx'
import Schemes from './modules/schemes/schemes.jsx'
// import Admin from './modules/admin/admin.jsx'
import AuthPage from './modules/auth/authPage.jsx'
// import Expenses from './modules/expenses/expenses.jsx'
import DataDashboard from './modules/monitor/DataDashboard.jsx'
import { useState, useEffect } from "react";



// Protected Route with role check
const ProtectedRoute = ({ children, allowedRoles }) => {
  const [isAuthenticated, setIsAuthenticated] = useState(null);
  const [userType, setUserType] = useState(null);

  useEffect(() => {
    setIsAuthenticated(localStorage.getItem("token") !== null);
    setUserType(localStorage.getItem("user_type"));
  }, []);

  if (isAuthenticated === null) {
    return <div>Loading...</div>; // Avoid premature navigation
  }

  if (!isAuthenticated) {
    return <Navigate to="/auth" replace />;
  }

  if (!allowedRoles.includes(userType)) {
    return <Navigate to="/app/dashboard" replace />;
  }

  return children;
};

const router = createBrowserRouter([
  {
    path: '/',
    element: <AuthPage />
  },
  {
    path: '/auth',
    element: <AuthPage />
  },
  
    //Citizen: Village rep, profile pg (vaccination, IT, personal details, assets, certificates), schemes (enroll)
    //Admin: Users (Edit, delete), Villages
    //Govt monitor: Profile, data
    //Govt Employee: Profile pg, Users(Edit, delete), scheme, vaccination, household, tax filing
    // path: '/app',
    // element: <ProtectedRoute allowedRoles={['citizen', 'admin', 'govt_monitor', 'govt_employee']}><App /></ProtectedRoute>,
    // children: [
      // {
      //   path: "",
      //   element: <Dashboard />
      // },
      // {
      //   path: "dashboard",
      //   element: <Dashboard />
      // },
      // Citizen Routes
      {
        path: "/profile",
        element: <ProtectedRoute allowedRoles={['USER', 'admin', 'govt_monitor', 'govt_employee']}>
          <Profile type={localStorage.getItem('user_type')} /> {/* Will show vaccination, IT, personal details, assets, certificates */}
        </ProtectedRoute>
      },
      {
        path: "/schemes",
        element: <ProtectedRoute allowedRoles={['USER']}>
          <Schemes />
        </ProtectedRoute>
      },
      // Admin Routes
      {
        path: "/users",
        element: <ProtectedRoute allowedRoles={['admin', 'govt_employee']}>
          <Users canEdit canDelete />
        </ProtectedRoute>
      },

      {
        path: "/data",
        element: <ProtectedRoute allowedRoles={['govt_monitor']}>
          <DataDashboard />
        </ProtectedRoute>
      },
      // Govt Employee Routes
    
  
])

createRoot(document.getElementById('root')).render(
  // <StrictMode>
    <RouterProvider router={router} />
  // </StrictMode>,
)
