import { useState, useEffect } from 'react'
import reactLogo from './assets/react.svg'
import viteLogo from '/vite.svg'
import './App.css'
import DButton from './atoms/DButton'
// import { callAPI } from './services/ApiHelper'
import AuthPage from './modules/auth/authPage'
import Navbar from './modules/navbar/navbar'
import { Outlet } from 'react-router-dom'

const getTabs = (userType) => {
  const commonTabs = [];

  switch(userType) {
    case 'citizen':
      return [
        ...commonTabs,
        { label: "Village Representatives", icon: 1, link: "citizen/village_representative" },
        { label: "Profile", icon: 1, link: "citizen/profile" },
        { label: "Schemes", icon: 1, link: "citizen/schemes" },
      ];
    
    case 'admin':
      return [
        ...commonTabs,
        { label: "Users", icon: 1, link: "admin/users" },
        { label: "Villages", icon: 1, link: "admin/villages" },
      ];
    
    case 'govt_monitor':
      return [
        ...commonTabs,
        { label: "Profile", icon: 1, link: "monitor/profile" },
        { label: "Dashboard", icon: 1, link: "monitor/data" },
      ];
    
    case 'govt_employee':
      return [
        ...commonTabs,
        { label: "Profile", icon: 1, link: "employee/profile" },
        { label: "Users", icon: 1, link: "employee/users" },
        { label: "Schemes", icon: 1, link: "employee/schemes" },
        { label: "Vaccination", icon: 1, link: "employee/vaccination" },
        { label: "Household", icon: 1, link: "employee/household" },
        { label: "Tax Filing", icon: 1, link: "employee/tax_filing" },
      ];
    
    default:
      return commonTabs;
  }
};

function App() {
  const [tabs, setTabs] = useState([]);

  useEffect(() => {
    const userType = localStorage.getItem('user_type');
    setTabs(getTabs(userType));
  }, []);

  // const signIn=async ()=>{
  //   const email_="aashray_tandon@gmail.com";
  //   const password_="Test@1234";
  //   const user={
  //     email:email_,
  //     password:password_
  //   }
  //   const response = await callAPI("/signin","POST",user);
  //   console.log(response);
  // }

  return (
    <>
      <div style={{
        backgroundColor: "var(--bg-primary)",
        minHeight: "100vh",
        minWidth:"100vw",
        display: "flex",
        overflow: "hidden",
      }}>

        <div style={{
          zIndex: 100,
        }}>
          <Navbar tabs={tabs}/>
        </div>

        <div style={{
          flexGrow:1,
          padding:"20px",
          overflowY:"hidden",
          height:"100vh",
          display:"flex",
          flexDirection:"column",
        }}>
          <Outlet/>
        </div>
      
      
      </div>
    </>
  )
}

export default App
