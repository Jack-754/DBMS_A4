import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'

import App from './App.jsx'
import { createBrowserRouter, RouterProvider, Navigate } from 'react-router-dom'
import Dashboard from './modules/dashboard/dashboard.jsx'
import Profile from './modules/profile/profile.jsx'
import Users from './modules/users/users.jsx'
import Schemes from './modules/schemes/schemes.jsx'
import Pmembers from './modules/p_members/p_members.jsx'
// import Admin from './modules/admin/admin.jsx'
import AuthPage from './modules/auth/authPage.jsx'
// import Expenses from './modules/expenses/expenses.jsx'
import DataDashboard from './modules/monitor/DataDashboard.jsx'
import Vaccination from './modules/Vaccination/Vaccination.jsx'
import Taxfiling from './modules/Taxfiling/Taxfiling.jsx'
import Household from './modules/Household/Household.jsx'
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

  // if (!allowedRoles.includes(userType)) {
  //   return <Navigate to="/app/dashboard" replace />;
  // }

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
  {
    path: '/app',
    element: <ProtectedRoute allowedRoles={['CITIZEN', 'SYSTEM_ADMINISTRATOR', 'GOVERNMENT_MONITOR', 'PANCHAYAT_EMPLOYEES']}><App /></ProtectedRoute>,
    children: [
      {
        path: "",
        element: <Dashboard />
      },
      {
        path: "dashboard",
        element: <Dashboard />
      },
      // Citizen Routes
      {
        path: "profile",
        element: <ProtectedRoute allowedRoles={['CITIZEN', 'SYSTEM_ADMINISTRATOR', 'GOVERNMENT_MONITOR', 'PANCHAYAT_EMPLOYEES']}>
          <Profile type={localStorage.getItem('user_type')} />
        </ProtectedRoute>
      },
      {
        path: "schemes",
        element: <ProtectedRoute allowedRoles={['CITIZEN']}>
          <Schemes />
        </ProtectedRoute>
      },
      // Admin & Government Employee Routes
      {
        path: "users",
        element: <ProtectedRoute allowedRoles={['SYSTEM_ADMINISTRATOR']}>
          <Users />
        </ProtectedRoute>
      },
      // Government Monitor Routes
      {
        path: "data",
        element: <ProtectedRoute allowedRoles={['GOVERNMENT_MONITOR']}>
          <DataDashboard />
        </ProtectedRoute>
      },
      {
        path: "p_members",
        element: <ProtectedRoute allowedRoles={['GOVERNMENT_MONITOR', 'CITIZEN']}>
          <Pmembers />
        </ProtectedRoute>
      },
      {
        path: "vaccination",
        element: <ProtectedRoute allowedRoles={['PANCHAYAT_EMPLOYEES']}>
          <Vaccination />
        </ProtectedRoute>
      },
      {
        path: "tax_filing",
        element: <ProtectedRoute allowedRoles={['PANCHAYAT_EMPLOYEES']}>
          <Taxfiling />
        </ProtectedRoute>
      },
      {
        path: "household",
        element: <ProtectedRoute allowedRoles={['PANCHAYAT_EMPLOYEES']}>
          <Household />
        </ProtectedRoute>
      }
    ]
  },


    
  
])

createRoot(document.getElementById('root')).render(
  // <StrictMode>
    <RouterProvider router={router} />
  // </StrictMode>,
)
