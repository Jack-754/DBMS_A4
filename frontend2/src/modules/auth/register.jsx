import React, { useState } from 'react';
import './auth.css';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import Loader from '../../molecules/Loader';

const Register = ({ className, onLoginClick ,onSuccess}) => {
  const [name, setName] = useState('');
  const [citizen_id, setCitizen_id] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirm_password, setconfirm_password] = useState('');
  const [errors, setErrors] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const navigate = useNavigate();

  //  Email validation regex
  const isValidEmail = (email) => /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);


  const handleSubmit = async (e) => {
    e.preventDefault();
    setErrors('');
    setIsLoading(true);
    // Validate Name
    if (!name.trim()) {
      setErrors('Name is required');
      return;
      // validationErrors.first_name = "First Name is required";
    }
    if (!citizen_id.trim()) {
      setErrors('Citizen ID is required');
      return;
      // validationErrors.lst_name = "Last Name is required";
    }

    if (!/^\d+$/.test(citizen_id)) {
      setErrors('Citizen ID must contain only numbers');
      return;
    }

    // Validate Email
    if (!email.trim()) {
      setErrors('Email is required');
      return;
      // validationErrors.email = "Email is required";
    } 
    // else if (!isValidEmail(email)) {
    //   setErrors('Invalid email format');
    //   return;

    //   // validationErrors.email = "Invalid email format";
    // }

    // Validate Password
    if (!password.trim()) {
      setErrors('Password is required');
      return;
      // validationErrors.password = "Password is required";
    } 
    else if (password.length < 6) {
      setErrors('Password must be at least 6 characters');
      return;
      // validationErrors.password = "Password must be at least 6 characters";
    }

    // Validate Confirm Password
    if (!confirm_password.trim()) {
      setErrors('Please confirm your password');
      return;
      // validationErrors.confirmPassword = "Please confirm your password";
    } 
    else if (password !==confirm_password) {
      setErrors('Passwords do not match');
      return;
      // validationErrors.confirmPassword = "Passwords do not match";
    }

    const response = await axios.post(import.meta.env.VITE_APP_URI + '/register', {
      Query: "",
      Add: "Register",
      Data: {
        name: name,
        citizen_id: citizen_id,
        username: email,
        password: password,
      }
    }, {
      headers: {
        'Content-Type': 'application/json'
      }
    });

    if (response.data.Status === "Success") {
      // Store the received data in localStorage
      localStorage.setItem('user_id', response.data.Data.Result[0].userId);
      localStorage.setItem('user_type', response.data.Data.Result[0].type);
      localStorage.setItem('token', response.data.token);
      
      setErrors('');
      setEmail('');
      setPassword('');
      setName('');
      setCitizen_id('');
      setconfirm_password('');
      
      if (onSuccess) {
        onSuccess();
      }
      navigate('/profile');
    } else {
      setErrors(response.data.message || 'Registration failed. Please try again.');
      alert(response.data.Message || 'Registration failed');
    }
    setIsLoading(false);
  };
  if(isLoading){
    return <Loader/>
  }
  return (
    <form className={`signUp ${className}`} onSubmit={handleSubmit}>
      <h3>Create Your Account</h3>
      {/* First Name Input */}
      <input
        className="w100"
        type="text"
        name="name"
        placeholder="Name"
        autoComplete="off"
        value={name}
        onChange={(e) => setName(e.target.value)}
      />

      {/* Citizen ID Input */}
      <input
        className="w100"
        type="number"
        name="citizen_id"
        placeholder="Citizen ID"
        autoComplete="off"
        value={citizen_id}
        onChange={(e) => setCitizen_id(e.target.value)}
      />

      {/* Email Input */}
      <input
        className="w100"
        type="text"
        name="email"
        placeholder="Email"
        autoComplete="off"
        value={email}
        onChange={(e) => setEmail(e.target.value)}
      />

      {/* Password Input */}
      <input
        type="password"
        name="password"
        placeholder="Password"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
      />

      {/* Confirm Password Input */}
      <input
        type="password"
        name="confirmPassword"
        placeholder="Confirm Password"
        value={confirm_password}
        onChange={(e) => setconfirm_password(e.target.value)}
      />
      {errors && <p className="error">{errors}</p>}
      <button className="form-btn sx log-in" type="button" onClick={onLoginClick}>
        Log In
      </button>
      <button className="form-btn dx" type="submit">Sign Up</button>
    </form>
  );
};

export default Register;