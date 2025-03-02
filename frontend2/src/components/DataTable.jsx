import React, { useState, useEffect } from 'react';
import axios from 'axios';
import DTable from '../atoms/table';
import DDropdown from '../atoms/DDropdown';
import './DataTable.css';

const DataTable = () => {
    const [selectedTable, setSelectedTable] = useState('panchayat_employees');
    const [tableData, setTableData] = useState([]);
    const [headers, setHeaders] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    const tables = [
        'village_representative',
        'schemes',
        'users',
        'villages'
    ];

    useEffect(() => {
        fetchTableData();
    }, [selectedTable]);

    const fetchTableData = async () => {
        try {
            setLoading(true);
            const token = localStorage.getItem('token');
            const response = await axios.get(import.meta.env.VITE_APP_URI + '/query_table', {
                headers: {
                    // 'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                },
                data: {
                    Query: "SELECT",
                    Data: {
                        table_name: selectedTable,  
                        filters:[]
                    },
                }
            });

            if (response.data.Status === 'Success' && response.data.Data.Result) {
                const data = response.data.Data.Result;
                if (data.length > 0) {
                    // Create headers from the first row
                    const headersList = Object.keys(data[0]).map(key => ({
                        key: key,
                        label: key.split('_').map(word => 
                            word.charAt(0).toUpperCase() + word.slice(1)
                        ).join(' ')
                    }));
                    setHeaders(headersList);
                    setTableData(data);
                } else {
                    setHeaders([]);
                    setTableData([]);
                }
                setError(null);
            } else {
                setError('No data available');
                setHeaders([]);
                setTableData([]);
            }
        } catch (err) {
            console.error('Error fetching table data:', err);
            setError(err.message || 'Failed to fetch data');
            setHeaders([]);
            setTableData([]);
        } finally {
            setLoading(false);
        }
    };

    const handleDelete = async (id) => {
        try {
            const token = localStorage.getItem('token');
            await axios.delete(import.meta.env.VITE_APP_URI + '/delete', {
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                },
                data: {
                    Query: "DELETE",
                    Data: {
                        table_name: selectedTable,
                        filters: {
                            id: {
                                operator: 'eq',
                                value: id
                            }
                        }
                    }
                }
            });
            fetchTableData(); // Refresh the table
        } catch (err) {
            console.error('Error deleting record:', err);
            setError(err.message || 'Failed to delete record');
        }
    };

    const handleEdit = (id) => {
        // Implement edit functionality
        console.log('Edit record with ID:', id);
    };

    return (
        <div className="data-table-container">
            <div className="table-controls">
                <DDropdown
                    name={selectedTable}
                    data={tables}
                    func={setSelectedTable}
                />
            </div>
            
            {loading ? (
                <div>Loading...</div>
            ) : error ? (
                <div className="error-message">{error}</div>
            ) : (
                <DTable
                    headers={headers}
                    data={tableData}
                    onDelete={handleDelete}
                    onEdit={handleEdit}
                />
            )}
        </div>
    );
};

export default DataTable; 