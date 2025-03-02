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
    // Check if email is valid
    if (!email.trim()) {
      // validationErrors.email = "Email is required";
      setErrors('Email is required');
      return;
    }
    // Check if password meets length requirement
    if (!password.trim()) {
      setErrors('Password is required');
      return;
    } 
    else if (password.length < 6) {
      setErrors('Password must be at least 6 characters');
      return;
    }

    const response = await axios.post(import.meta.env.VITE_APP_URI + '/login', {
      Query: "",
      Add: "Login",
      Data: {
        userId: email,
        password: password
      }
    }, {
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('token')}`
      },
      withCredentials: true
    });
    console.log("response",response);
    if(response.data.Status === "Success"){
      // localStorage.setItem('name', response.data.firstName); // Example: Store token
      localStorage.setItem('user_id', response.data.Data.Result[0].userId);
      localStorage.setItem('user_type', response.data.Data.Result[0].type);
      localStorage.setItem('token', response.data.token);

      console.log("response.data.userType", localStorage.getItem('user_type'));
      navigate('/profile');
      // window.location.href = '/app';
      setErrors('');
    }
    else{
      setErrors('Invalid email or password');
    }
    setIsLoading(false);
  };

  const handleGoogleSignIn = async () => {
    window.location.href = "http://localhost:8000/api/v1/auth/google";  
    // const response = await callAPI('/auth/google', 'GET');
    // if(!response.error){
    //   localStorage.setItem('name', response.data.firstName); // Example: Store token
    //   window.location.href = '/app';
    //   setErrors('');
    // }
    // else{
    //   setErrors('Invalid email or password');
    // }
  }
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