import React, { useState, useEffect } from 'react';
import './navbar.css';
import DButton from '../../atoms/DButton';
import { Link, useLocation } from 'react-router-dom';
import axios from 'axios';

// Import icons from react-icons
import { FaUser, FaUsers, FaBuilding, FaChartBar, FaSyringe, FaHome, FaFileAlt } from 'react-icons/fa';
import { MdDashboard } from 'react-icons/md';

const iconMap = {
  'Profile': FaUser,
  'Users': FaUsers,
  'Villages': FaBuilding,
  'Dashboard': MdDashboard,
  'Schemes': FaChartBar,
  'Vaccination': FaSyringe,
  'Household': FaHome,
  'Tax Filing': FaFileAlt,
  'Village Representatives': FaUsers,
};

const signOut = async () => {
  // try {
    // const response = await axios.post(import.meta.env.VITE_APP_URI + '/signout', {
    //   Query: "",
    //   Add: "Signout",
    //   Data: {}
    // }, {
    //   headers: {
    //     'Content-Type': 'application/json',
    //     'Accept': 'application/json'
    //   }
    // });
    localStorage.removeItem('user_type');
    localStorage.removeItem('token');
    localStorage.removeItem('user_id');
    window.location.href = '/';
  // } catch (error) {
  //   console.error('Signout error:', error);
  // }
};

function Navbar({ tabs }) {
  const [isDarkMode, setIsDarkMode] = useState(false);
  const location = useLocation();

  useEffect(() => {
    if (isDarkMode) {
      document.body.setAttribute("data-theme", "dark");
    } else {
      document.body.removeAttribute("data-theme");
    }
  }, [isDarkMode]);

  return (
    <nav className="main-menu">
      <div className="logo-container">
        <h1>GPMS</h1>
      </div>
      
      <ul>
        {tabs.map((tab, index) => {
          const Icon = iconMap[tab.label] || MdDashboard;
          const isActive = location.pathname.includes(tab.link);
          
          return (
            <li
              key={index}
              className={`nav-item ${isActive ? 'active' : ''}`}
            >
              <Link to={tab.link} className='link'>
                <Icon className="nav-icon" />
                <span className="nav-text">{tab.label}</span>
              </Link>
            </li>
          );
        })}
      </ul>

      <div className="button-container">
        <DButton
          text={isDarkMode ? "Light Mode" : "Dark Mode"}
          onClick={() => setIsDarkMode(!isDarkMode)}
          buttonClass='button-nav-primary'
        />
        <DButton
          text="Sign Out"
          onClick={signOut}
          buttonClass='button-nav-primary'
        />
      </div>
    </nav>
  );
}

export default Navbar;