import React, { useState } from 'react';
import './SharePointLogin.css';

const SharePointLogin = ({ onLoginSuccess, onLogout }) => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');

  const handleLogin = async (e) => {
    e.preventDefault();
    console.log('Login attempt:', username);
    
    try {
      const response = await fetch('http://localhost:5000/api/sharepoint-auth', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          action: 'login',
          username: username,
          password: password
        }),
      });

      const data = await response.json();
      console.log('Login response:', data);

      if (data.success) {
        if (onLoginSuccess) {
          onLoginSuccess(data.user);
        }
      } else {
        alert(data.error || 'Login failed');
      }
    } catch (error) {
      console.error('Login error:', error);
      alert('Network error. Please try again.');
    }
  };

  return (
    <div className="sharepoint-login-card">
      <div className="login-header">
        <h3>SharePoint Login</h3>
        <p>Sign in with your Microsoft 365 credentials</p>
      </div>

      <form className="login-form" onSubmit={handleLogin}>
        <div className="form-group">
          <label htmlFor="username">Username/Email</label>
          <input
            id="username"
            type="text"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            placeholder="Enter your username or email"
            required
          />
        </div>

        <div className="form-group">
          <label htmlFor="password">Password</label>
          <input
            id="password"
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            placeholder="Enter your password"
            required
          />
        </div>

        <button
          type="submit"
          className="btn login-btn"
          disabled={!username || !password}
        >
          Sign In
        </button>
      </form>

      <div className="login-help">
        <p><strong>Login Information:</strong></p>
        <p>• Use your Microsoft 365 username (e.g., <code>username@cpncorp.com</code>)</p>
        <p>• Enter your regular network password</p>
        <p>• You must have access to the SharePoint site: <code>askcal</code></p>
      </div>
    </div>
  );
};

export default SharePointLogin;
