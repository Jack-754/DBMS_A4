import { useEffect, useState } from 'react'
import '../styles.css'
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
        { label: "Profile", icon: 1, link: "/app/profile" },
        { label: "Panchayat Members", icon: 1, link: "/app/p_members" },
        { label: "Schemes", icon: 1, link: "/app/schemes" },
      ];

    case 'SYSTEM_ADMINISTRATOR':
      return [
        ...commonTabs,
        { label: "Users", icon: 1, link: "/app/users" },
      ];

    case 'GOVERNMENT_MONITOR':
      return [
        ...commonTabs,
        { label: "Profile", icon: 1, link: "/app/profile" },
        { label: "Dashboard", icon: 1, link: "/app/data" },
      ];

    case 'PANCHAYAT_EMPLOYEES':
      return [
        ...commonTabs,
        { label: "Profile", icon: 1, link: "/app/profile" },
        { label: "Schemes", icon: 1, link: "/app/schemes" },
        { label: "Vaccination", icon: 1, link: "/app/vaccination" },
        { label: "Household", icon: 1, link: "/app/household" },
        { label: "Tax Filing", icon: 1, link: "/app/tax_filing" },
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
