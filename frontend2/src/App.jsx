import { useEffect, useState } from 'react'
import './App.css'
// import { callAPI } from './services/ApiHelper'
import { Outlet } from 'react-router-dom'
import Navbar from './modules/navbar/navbar'

const getTabs = (userType) => {
  const commonTabs = [];

  userType = userType?.trim().toUpperCase() || '';
  console.log("userType:", userType);

  switch (userType) {
    case 'CITIZEN':
      return [
        ...commonTabs,
        { label: "Village Representatives", icon: 1, link: "/village_representative" },
        { label: "Profile", icon: 1, link: "/app/profile" },
        { label: "Schemes", icon: 1, link: "/app/schemes" },
      ];

    case 'ADMIN':
      return [
        ...commonTabs,
        { label: "Users", icon: 1, link: "admin/users" },
        { label: "Villages", icon: 1, link: "admin/villages" },
      ];

    case 'GOVT_MONITOR':
      return [
        ...commonTabs,
        { label: "Profile", icon: 1, link: "monitor/profile" },
        { label: "Dashboard", icon: 1, link: "monitor/data" },
      ];

    case 'GOVT_EMPLOYEE':
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
    <div className="app-container">
      <Navbar tabs={tabs} />
      <main className="content-container">
        <Outlet />
      </main>
    </div>
  )
}

export default App
