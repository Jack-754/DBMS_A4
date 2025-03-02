 import React ,{useState,useEffect} from 'react';
import './navbar.css';
import DButton from '../../atoms/DButton';
import { Link,NavLink } from 'react-router-dom';
import { callAPI } from '../../services/ApiHelper'

const icon_map = {
    1:"/icons/dashboard.svg",
    2:"/icons/expenses.svg",
    3:"/icons/admin.svg",
    4:"/icons/admin-white.svg",
    5:"/icons/expenses-white.svg",
    6:"/icons/dashboard-white.svg",
}
const icon_map_dark = {
    6:"/icons/dashboard.svg",
    5:"/icons/expenses.svg",
    4:"/icons/admin.svg",
    3:"/icons/admin-white.svg",
    2:"/icons/expenses-white.svg",
    1:"/icons/dashboard-white.svg",
}

const signOut = async () => {
    const response = await callAPI('/signout', 'POST');
    localStorage.removeItem('name');
    localStorage.removeItem('access-token');    
    if(!response.error) window.location.href = '/';
}

function Navbar({ tabs }) {
    const [activeIndex, setActiveIndex] = useState(0);
    const [isDarkMode, setIsDarkMode] = useState(false);
    const [iconMap, setIconMap] = useState(icon_map);
    useEffect(() => {
        if (isDarkMode) {
          document.body.setAttribute("data-theme", "dark");
          setIconMap(icon_map_dark);
        } else {
          document.body.removeAttribute("data-theme");
          setIconMap(icon_map);
        }
      }, [isDarkMode]);

    return (
        <nav className="main-menu">
            <div style={{height:"100px", display:"flex", justifyContent:"center", alignItems:"center"}}>
                <h1>Trackify</h1>
                <img className="logo" src={iconMap[1]} alt="logo" />
            </div>
            <ul>
                {tabs.map((tab, index) => (
                    <li
                        key={index}
                        className={`nav-item ${activeIndex === index ? 'active' : ''}`}
                        onClick={() => setActiveIndex(index)}
                    >
                        <b></b>
                        <b></b>
                        <Link to={tab.link} className='link'>
                            <img src={`${activeIndex === index ? iconMap[index+1] : iconMap[6-index]}`} className={`nav-icon `}></img>
                            <span className="nav-text">{tab.label}</span>
                        </Link>
                    </li>
                ))}
            </ul>
            <div style={{
                position: "absolute",
                bottom: "5vh",
                display: "flex",
                flexDirection: "column",
                alignItems: "center",
                width: "100%",
                gap: "20px",
            }}>
                <DButton
                    text={isDarkMode ? "Light Mode" : "Dark Mode"}
                    onClick={() => setIsDarkMode(!isDarkMode)}
                    buttonClass='button-nav-primary'
                />
                <DButton
                    text = "Sign Out"
                    onClick={signOut}
                    buttonClass='button-nav-primary'
                />
            </div>
        </nav>
    );
}

export default Navbar;