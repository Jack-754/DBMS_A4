import React, { useState } from 'react';
import './auth.css';
// import { callAPI } from '../../services/ApiHelper'
import Loader from '../../molecules/Loader';

const Register = ({ className, onLoginClick ,onSuccess}) => {
  const [first_name, setFirst_name] = useState('');
  const [last_name, setLast_name] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirm_password, setconfirm_password] = useState('');
  const [errors, setErrors] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  //  Email validation regex
  const isValidEmail = (email) => /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);


  const handleSubmit = async (e) => {
    e.preventDefault();
    setErrors('');
    setIsLoading(true);
    // Validate Name
    if (!first_name.trim()) {
      setErrors('First Name is required');
      return;
      // validationErrors.first_name = "First Name is required";
    }
    if (!last_name.trim()) {
      setErrors('Last Name is required');
      return;
      // validationErrors.lst_name = "Last Name is required";
    }

    // Validate Email
    if (!email.trim()) {
      setErrors('Email is required');
      return;
      // validationErrors.email = "Email is required";
    } 
    else if (!isValidEmail(email)) {
      setErrors('Invalid email format');
      return;

      // validationErrors.email = "Invalid email format";
    }

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

    const response = await callAPI('/signup', 'POST',{first_name:first_name, last_name:last_name, email:email, password:password, confirm_password:confirm_password,role_name:'user'});
    console.log("response",response);
    // If all validations pass, proceed with submission
    setIsLoading(false);
    if(!response.error){
      onSuccess();
      setErrors('');
      setEmail('');
      setPassword('');
      setFirst_name('');
      setLast_name('');
      setconfirm_password('');
    }
    else{
      setErrors(response.message);
    }
  };
  if(isLoading){
    return <Loader/>
  }
  return (
    <form className={`signUp ${className}`} onSubmit={handleSubmit}>
      <h3>Create Your Account</h3>

      {/* Fisrt Name Input */}
      <input
        className="w100"
        type="text"
        name="name"
        placeholder="First Name"
        autoComplete="off"
        value={first_name}
        onChange={(e) => setFirst_name(e.target.value)}
      />

      {/* Last Name Input */}
      <input
        className="w100"
        type="text"
        name="name"
        placeholder="Last Name"
        autoComplete="off"
        value={last_name}
        onChange={(e) => setLast_name(e.target.value)}
      />
      

      {/* Email Input */}
      <input
        className="w100"
        type="email"
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