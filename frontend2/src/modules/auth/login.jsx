import React, { useEffect, useState } from 'react';
import './auth.css';

// import { callAPI } from '../../services/ApiHelper'
import { useNavigate } from 'react-router-dom';
import Loader from '../../molecules/Loader';
import axios from 'axios';

const Login = ({ className, onBackClick }) => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [errors, setErrors] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const navigate = useNavigate();

  // Email validation regex
  const isValidEmail = (email) => /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setErrors('');
    setIsLoading(true);

    try {
      // Validation
      if (!email.trim()) {
        setErrors('Email is required');
        setIsLoading(false);
        return;
      }
      if (!password.trim()) {
        setErrors('Password is required');
        setIsLoading(false);
        return;
      } 
      if (password.length < 6) {
        setErrors('Password must be at least 6 characters');
        setIsLoading(false);
        return;
      }

      const response = await axios.post(import.meta.env.VITE_APP_URI + '/login', {
        Query: "",
        Add: "Login",
        Data: {
            "username": email,
            "password": password
          // userId: email,
          // password: password
        }
      }, {
        headers: {
          'Content-Type': 'application/json'
        },
      
      });
      console.log(response.data);

      if(response.data.Status === "Success"){
        localStorage.setItem('user_id', response.data.Data.Result[0].userId);
        localStorage.setItem('user_type', response.data.Data.Result[0].type);
        localStorage.setItem('token', response.data.access_token);
        setErrors('');

        // Navigate based on user type
        if (response.data.Data.Result[0].type === 'SYSTEM_ADMINISTRATOR') {
          navigate('/app/users');
        } else {
          navigate('/app/profile');
        }
      } else {
        setErrors(response.data.message || 'Invalid email or password');
        alert(response.data.Message || 'Login failed');
      }
    } catch (error) {
      setErrors(error.response?.data?.message || 'An error occurred during login');
      alert(error.response?.data?.Message || error.message || 'An error occurred during login');
    } finally {
      setIsLoading(false);
    }
  };

  const handleGoogleSignIn = () => {
    window.location.href = import.meta.env.VITE_APP_URI + "/auth/google";
  };

  if(isLoading){
    return <Loader/>
  }

  return (
    <form className={`signIn ${className}`} onSubmit={handleSubmit}>
      <h3>Welcome<br />Back !</h3>
      
      <button type="button" className="login-with-google-btn" onClick={handleGoogleSignIn}>
        Sign in with Google
      </button>
      <p className={`or_hi`}>- or -</p>

      {/* Email Input */}
      <input 
        type="text" 
        placeholder="Email" 
        autoComplete="off" 
        value={email} 
        onChange={(e) => setEmail(e.target.value)} 
      />
      

      {/* Password Input */}
      <input 
        type="password" 
        placeholder="Password" 
        value={password} 
        onChange={(e) => setPassword(e.target.value)} 
      />
      {errors && <p className="error">{errors}</p>}

      <button className="form-btn sx back" type="button" onClick={onBackClick}>Back</button>
      <button className="form-btn dx" type="submit">Log In</button>
    </form>
  );
};

export default Login;