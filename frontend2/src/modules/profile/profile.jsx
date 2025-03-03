import React, { useState } from 'react';
import axios from 'axios';
import { useEffect } from 'react';
import DataTable from '../../components/DataTable';

const profileStyles = {
    profileContainer: {
        padding: '20px',
        maxWidth: '800px',
        margin: '0 auto',
    },
    profileSection: {
        backgroundColor: '#fff',
        borderRadius: '8px',
        padding: '20px',
        marginBottom: '20px',
        boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
    },
    profileField: {
        marginBottom: '12px',
        display: 'flex',
        alignItems: 'center',
        color: '#333',
    },
    label: {
        fontWeight: 'bold',
        minWidth: '150px',
        marginRight: '10px',
        color: '#333',
    },
    value: {
        color: '#333',
    },
    sectionTitle: {
        borderBottom: '2px solid #eee',
        paddingBottom: '10px',
        marginBottom: '20px',
        color: '#2c3e50',
    }
};

const Profile = ({ type }) => {
    const [profileData, setProfileData] = useState(null);
    const [error, setError] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchProfileData = async () => {
            try {
                setLoading(true);
                const token = localStorage.getItem('token');
                console.log("Fetching with token:", token);
                
                const response = await axios.get(import.meta.env.VITE_APP_URI + '/profile', {
                    headers: {
                        'Authorization': `Bearer ${token}`,
                        'Accept': 'application/json'
                    }
                });

                console.log("Full API Response:", response.data);

                if (response.data.Data?.Result && response.data.Data.Result.length > 0) {
                    setProfileData(response.data.Data.Result[0]);
                    setError(null);
                } else {
                    setError('No profile data found');
                }
            } catch (err) {
                console.error("Profile fetch error:", err);
                setError(err.message || 'Failed to fetch profile data');
            } finally {
                setLoading(false);
            }
        };

        fetchProfileData();
    }, []);

    // Effect to log profile data updates
    useEffect(() => {
        console.log("Profile Data Updated:", profileData);
    }, [profileData]);

    const formatDate = (dateString) => {
        return new Date(dateString).toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'long',
            day: 'numeric'
        });
    };

    const renderContent = () => {
    };

    return (
        <div>
           <>
                        <h2 style={profileStyles.sectionTitle}>Citizen Profile</h2>
                        {profileData ? (
                            <div style={profileStyles.profileContainer}>
                                <div style={profileStyles.profileSection}>
                                    <h3 style={profileStyles.sectionTitle}>Personal Details</h3>
                                    <div style={profileStyles.profileField}>
                                        <span style={profileStyles.label}>Name:</span>
                                        <span style={profileStyles.value}>{profileData.name}</span>
                                    </div>
                                    <div style={profileStyles.profileField}>
                                        <span style={profileStyles.label}>Date of Birth:</span>
                                        <span style={profileStyles.value}>{formatDate(profileData.dob)}</span>
                                    </div>
                                    <div style={profileStyles.profileField}>
                                        <span style={profileStyles.label}>Gender:</span>
                                        <span style={profileStyles.value}>{profileData.gender === 'M' ? 'Male' : 'Female'}</span>
                                    </div>
                                    <div style={profileStyles.profileField}>
                                        <span style={profileStyles.label}>Phone:</span>
                                        <span style={profileStyles.value}>{profileData.phone}</span>
                                    </div>
                                    <div style={profileStyles.profileField}>
                                        <span style={profileStyles.label}>Education:</span>
                                        <span style={profileStyles.value}>{profileData.educational_id}</span>
                                    </div>
                                    <div style={profileStyles.profileField}>
                                        <span style={profileStyles.label}>Household ID:</span>
                                        <span style={profileStyles.value}>{profileData.household_id}</span>
                                    </div>
                                    <div style={profileStyles.profileField}>
                                        <span style={profileStyles.label}>Village ID:</span>
                                        <span style={profileStyles.value}>{profileData.village_id}</span>
                                    </div>
                                </div>
                                
                                <div style={profileStyles.profileSection}>
                                    <h3 style={profileStyles.sectionTitle}>Additional Information</h3>
                                    <div style={profileStyles.profileField}>Vaccination Details
                                        <DataTable 
                                            tableName="vaccination" 
                                            preFilters={{
                                                citizen_id: {
                                                    operator: 'eq',
                                                    value: profileData.id
                                                }
                                            }} 
                                        />
                                    </div>
                                    <div style={profileStyles.profileField}>IT Details
                                        <DataTable 
                                            tableName="tax_filing" 
                                            preFilters={{
                                                citizen_id: {
                                                    operator: 'eq',
                                                    value: profileData.id
                                                }
                                            }} 
                                        />
                                    </div>
                                    <div style={profileStyles.profileField}>Assets
                                        <DataTable 
                                            tableName="assets" 
                                            preFilters={{
                                                owner_id: {
                                                    operator: 'eq',
                                                    value: profileData.id
                                                }
                                            }} 
                                        />
                                    </div>
                                    <div style={profileStyles.profileField}>Certificates
                                        <DataTable 
                                            tableName="certificates" 
                                            preFilters={{
                                                citizen_issued: {
                                                    operator: 'eq',
                                                    value: profileData.id
                                                }
                                            }} 
                                        />
                                    </div>
                                </div>
                            </div>
                        ) : (
                            <div style={profileStyles.profileSection}>Loading profile data...</div>
                        )}
                    </>
            {/* {renderContent()} */}
        </div>
    );
};

export default Profile; 