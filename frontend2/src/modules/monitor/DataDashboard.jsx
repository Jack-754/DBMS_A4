import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './DataDashboard.css';

const DataDashboard = () => {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchStats();
  }, []);

  const fetchStats = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem('token');
      const response = await axios.post(
        `${import.meta.env.VITE_APP_URI}/get_stats`,
        {
          Query: "STATS",
          Data: {
            village_id: '1',
            stat_type: 'all'
          }
        },
        {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        }
      );

      if (response.data.Status === 'Success') {
        setStats(response.data.Data.Result);
        setError(null);
      } else {
        setError(response.data.Message);
        alert(response.data.Message || 'Failed to fetch statistics');
      }
    } catch (err) {
      setError(err.message);
      alert(err.response?.data?.Message || err.message || 'Error fetching statistics');
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <div className="dashboard-loading">Loading statistics...</div>;
  if (error) return <div className="dashboard-error">Error: {error}</div>;
  if (!stats) return <div className="dashboard-error">No data available</div>;

  return (
    <div className="dashboard-container">
      <h1>Village Statistics Dashboard</h1>

      {/* Demographics Section */}
      <section className="dashboard-section">
        <h2>Demographics</h2>
        {stats.demographics[0] && (
          <div className="info-grid">
            <div className="info-item">
              <label>Village Name:</label>
              <span>{stats.demographics[0].village_name}</span>
            </div>
            <div className="info-item">
              <label>Total Population:</label>
              <span>{stats.demographics[0].total_population}</span>
            </div>
            <div className="info-item">
              <label>Male Population:</label>
              <span>{stats.demographics[0].male_population}</span>
            </div>
            <div className="info-item">
              <label>Female Population:</label>
              <span>{stats.demographics[0].female_population}</span>
            </div>
            <div className="info-item">
              <label>Other Population:</label>
              <span>{stats.demographics[0].other_population}</span>
            </div>
            <div className="info-item">
              <label>Total Households:</label>
              <span>{stats.demographics[0].total_households}</span>
            </div>
          </div>
        )}
      </section>

      {/* Education Section */}
      <section className="dashboard-section">
        <h2>Education Distribution</h2>
        <div className="table-container">
          <table>
            <thead>
              <tr>
                <th>Qualification</th>
                <th>Count</th>
                <th>Percentage</th>
              </tr>
            </thead>
            <tbody>
              {stats.education.map((edu, index) => (
                <tr key={index}>
                  <td>{edu.educational_qualification}</td>
                  <td>{edu.count}</td>
                  <td>{edu.percentage}%</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>

      {/* Age Distribution */}
      <section className="dashboard-section">
        <h2>Age Distribution</h2>
        {stats.age[0] && (
          <div className="info-grid">
            <div className="info-item">
              <label>Under 18:</label>
              <span>{stats.age[0].under_18}</span>
            </div>
            <div className="info-item">
              <label>18-30 years:</label>
              <span>{stats.age[0].age_18_30}</span>
            </div>
            <div className="info-item">
              <label>31-50 years:</label>
              <span>{stats.age[0].age_31_50}</span>
            </div>
            <div className="info-item">
              <label>Above 50:</label>
              <span>{stats.age[0].above_50}</span>
            </div>
          </div>
        )}
      </section>

      {/* Schemes Section */}
      <section className="dashboard-section">
        <h2>Scheme Enrollment</h2>
        <div className="table-container">
          <table>
            <thead>
              <tr>
                <th>Scheme Name</th>
                <th>Enrolled Citizens</th>
              </tr>
            </thead>
            <tbody>
              {stats.schemes.map((scheme, index) => (
                <tr key={index}>
                  <td>{scheme.scheme_name}</td>
                  <td>{scheme.enrolled_citizens}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>

      {/* Financial Statistics */}
      <section className="dashboard-section">
        <h2>Financial Overview</h2>
        {stats.financial[0] && (
          <div className="info-grid">
            <div className="info-item">
              <label>Tax Payers:</label>
              <span>{stats.financial[0].tax_payers}</span>
            </div>
            <div className="info-item">
              <label>Average Tax Amount:</label>
              <span>₹{stats.financial[0].avg_tax_amount}</span>
            </div>
            <div className="info-item">
              <label>Income Declarants:</label>
              <span>{stats.financial[0].income_declarants}</span>
            </div>
            <div className="info-item">
              <label>Average Declared Income:</label>
              <span>₹{stats.financial[0].avg_declared_income}</span>
            </div>
          </div>
        )}
      </section>
    </div>
  );
};

export default DataDashboard; 