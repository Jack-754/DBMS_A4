import React, { useState, useEffect } from 'react';
import axios from 'axios';
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer,
  PieChart, Pie, Cell
} from 'recharts';
import './DataDashboard.css';

const DataDashboard = () => {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedVillage, setSelectedVillage] = useState('');

  const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884d8'];

  useEffect(() => {
    fetchStats();
  }, [selectedVillage]);

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
      console.log(response);
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
        <div className="chart-container">
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={[
                  { name: 'Male', value: stats.demographics[0].male_population },
                  { name: 'Female', value: stats.demographics[0].female_population },
                  { name: 'Other', value: stats.demographics[0].other_population }
                ]}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                outerRadius={80}
                fill="#8884d8"
                dataKey="value"
              >
                {stats.demographics[0] && COLORS.map((color, index) => (
                  <Cell key={`cell-${index}`} fill={color} />
                ))}
              </Pie>
              <Tooltip />
              <Legend />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </section>

      {/* Education Section */}
      <section className="dashboard-section">
        <h2>Education Distribution</h2>
        <div className="chart-container">
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={stats.education}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="educational_qualification" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Bar dataKey="count" fill="#8884d8" />
              <Bar dataKey="percentage" fill="#82ca9d" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </section>

      {/* Age Distribution */}
      <section className="dashboard-section">
        <h2>Age Distribution</h2>
        <div className="chart-container">
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={[stats.age[0]]}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="village_name" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Bar dataKey="under_18" fill="#8884d8" />
              <Bar dataKey="age_18_30" fill="#82ca9d" />
              <Bar dataKey="age_31_50" fill="#ffc658" />
              <Bar dataKey="above_50" fill="#ff8042" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </section>

      {/* Schemes Section */}
      <section className="dashboard-section">
        <h2>Scheme Enrollment</h2>
        <div className="chart-container">
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={stats.schemes}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="scheme_name" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Bar dataKey="enrolled_citizens" fill="#8884d8" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </section>

      {/* Financial Statistics */}
      <section className="dashboard-section">
        <h2>Financial Overview</h2>
        <div className="stats-grid">
          {stats.financial[0] && (
            <>
              <div className="stat-card">
                <h3>Tax Payers</h3>
                <p>{stats.financial[0].tax_payers}</p>
              </div>
              <div className="stat-card">
                <h3>Average Tax Amount</h3>
                <p>₹{stats.financial[0].avg_tax_amount}</p>
              </div>
              <div className="stat-card">
                <h3>Income Declarants</h3>
                <p>{stats.financial[0].income_declarants}</p>
              </div>
              <div className="stat-card">
                <h3>Average Declared Income</h3>
                <p>₹{stats.financial[0].avg_declared_income}</p>
              </div>
            </>
          )}
        </div>
      </section>
    </div>
  );
};

export default DataDashboard; 