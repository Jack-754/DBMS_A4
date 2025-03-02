import React from 'react';
import './Loader.css'; // Make sure CSS file is in same directory

const Loader = () => {
  return (
    <div className="fixed inset-0 flex items-center justify-center" style={{
        height: "100vh",
        width: "100vw",
        backgroundColor: "var(--loader-bg)",
    }}>
      <div id="loader">
        {[...Array(5)].map((_, index) => (
          <div 
            key={index}
            className="loader-circle"
            style={{
              animationDelay: `-${index * 0.4}s`
            }}
          ></div>
        ))}
      </div>
    </div>
  );
};

export default Loader;