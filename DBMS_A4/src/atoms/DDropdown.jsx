// import React,{useState} from 'react'
// import { FaChevronDown } from "react-icons/fa"; // Import dropdown icon
// import './DDropdown.css'

// function DDropdown({name,data,func}) {

//     const [isDropdownOpen, setIsDropdownOpen] = useState(false);
//     const [selected, setSelected] = useState(name);

//     const toggleDropdown = () => {
//         console.log("***");
//         setIsDropdownOpen(!isDropdownOpen); // Toggle dropdown visibility
//     };

//     return (
//         <div className='dropdown-container'>
//             <div className="custom-dropdown" onClick={toggleDropdown}>
//                 <span>{selected.charAt(0).toUpperCase() + selected.slice(1)}</span>
//                 <FaChevronDown className="dropdown-icon" />
//             </div>

//             {/* Custom Dropdown Menu */}
//             {isDropdownOpen && (
//                 <div className={`custom-dropdown-menu ${isDropdownOpen ? "open" : ""}`}>
//                     {/* <div
//                         className="dropdown-item"
//                         onClick={() => handleTimeframeChange("weekly")}
//                     >
//                         Weekly
//                     </div>
//                     <div
//                         className="dropdown-item"
//                         onClick={() => handleTimeframeChange("monthly")}
//                     >
//                         Monthly
//                     </div> */}
//                     {data.map((item,index) => (
//                         <div
//                             key={index}
//                             className="dropdown-item"
//                             onClick={() => {
//                                 setSelected(item);
//                                 func();
//                                 setIsDropdownOpen(false);
//                             }}
//                         >
//                             {item}
//                         </div>
//                     ))}
//                 </div>
//             )}
//         </div>
//     )
// }

// export default DDropdown

import React from "react";
import { useState } from "react";
import { FaChevronDown } from "react-icons/fa";
import "./DDropdown.css";

function DDropdown({ name, data, func }) {
    const [isDropdownOpen, setIsDropdownOpen] = useState(false);
    const [selected, setSelected] = useState(name);

    const toggleDropdown = () => {
        console.log("***");
        setIsDropdownOpen(!isDropdownOpen); // Toggle dropdown visibility
    };

    return (
        <div className="dropdown-container">
            <div className="custom-dropdown" onClick={toggleDropdown}>
                <span>{selected.charAt(0).toUpperCase() + selected.slice(1)}</span>
                <FaChevronDown className={`dropdown-icon ${isDropdownOpen ? "rotate" : ""}`} />
            </div>

            {isDropdownOpen && (
                <div className="custom-dropdown-menu">
                    {data.map((item, index) => (
                        <div
                            key={index}
                            className="dropdown-item"
                            onClick={() => {
                                setSelected(item);
                                func(item); // Pass selected item
                                setIsDropdownOpen(false);
                            }}
                        >
                            {item}
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
}

export default DDropdown;
