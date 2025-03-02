import React, { useState } from 'react';
import './auth.css';
import Register from './register';
import Login from './login';

const AuthPage = () => {
  const [isLoginActive, setIsLoginActive] = useState(false);

  return (
    // <div className='auth_container'>
      <div className="container">
        <Register
          className={isLoginActive ? 'inactive-sx' : 'active-sx'}
          onLoginClick={() => setIsLoginActive(true)}
          onSuccess={() => setIsLoginActive(true)}
        />
        <Login
          className={isLoginActive ? 'active-dx' : 'inactive-dx'}
          onBackClick={() => setIsLoginActive(false)}
        />
      {/* </div> */}
    </div>
  );
};

export default AuthPage;