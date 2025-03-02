import React from 'react';

const Profile = ({ type }) => {
    console.log("type", type);
  const renderContent = () => {
    switch(type) {
      case 'USER':
        return (
          <>
            <h2>Citizen Profile</h2>
            {/* Add sections for: */}
            <div>Vaccination Details</div>
            <div>IT Details</div>
            <div>Personal Details</div>
            <div>Assets</div>
            <div>Certificates</div>
          </>
        );
      case 'admin':
        return (
          <>
            <h2>Admin Profile</h2>
            {/* Add admin specific profile content */}
          </>
        );
      case 'monitor':
        return (
          <>
            <h2>Government Monitor Profile</h2>
            {/* Add monitor specific profile content */}
          </>
        );
      case 'employee':
        return (
          <>
            <h2>Government Employee Profile</h2>
            {/* Add employee specific profile content */}
          </>
        );
      default:
        return <h2>Profile</h2>;
    }
  };

  return (
    <div>
      {renderContent()}
    </div>
  );
};

export default Profile; 