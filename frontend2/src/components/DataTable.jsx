import React, { useState, useEffect } from 'react';
import axios from 'axios';
import DTable from '../atoms/table';
import DDropdown from '../atoms/DDropdown';
import Modal from '../molecules/Modal';
import DButton from '../atoms/DButton';
import './DataTable.css';
import { useLocation } from 'react-router-dom';

const DataTable = ({ tableName = '', preFilters = {} }) => {
    const [selectedTable, setSelectedTable] = useState(tableName);
    const [tableData, setTableData] = useState([]);
    const [headers, setHeaders] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [isEditModalOpen, setIsEditModalOpen] = useState(false);
    const [editingRow, setEditingRow] = useState(null);
    const [editFormData, setEditFormData] = useState({});
    const [filters, setFilters] = useState([]);
    const [isFilterModalOpen, setIsFilterModalOpen] = useState(false);
    const [isAddModalOpen, setIsAddModalOpen] = useState(false);
    const [addFormData, setAddFormData] = useState({});
    const location = useLocation();
    const userType = localStorage.getItem('user_type');
    const isProfilePage = location.pathname === '/app/profile';
    const showActions = userType !== 'CITIZEN' && !isProfilePage;
    console.log("preFilters", preFilters)
    console.log("tableName", tableName)

    // Convert preFilters to internal filter format on mount and when preFilters change
    useEffect(() => {
        if (Object.keys(preFilters).length > 0) {
            const initialFilters = Object.entries(preFilters).map(([column, filterData]) => ({
                column,
                operator: filterData.operator || 'eq',
                value: filterData.value?.toString() || '',
                id: Date.now() + Math.random()
            }));
            setFilters(initialFilters);
        }
    }, [preFilters]);

    // Update selectedTable when tableName prop changes
    useEffect(() => {
        if (tableName) {
            setSelectedTable(tableName);
        }
    }, [tableName]);

    // Fetch data when filters or selectedTable changes
    useEffect(() => {
        fetchTableData();
    }, [selectedTable, filters]);

    const operators = [
        { value: 'eq', label: 'Equals' },
        { value: 'ne', label: 'Not Equals' },
        { value: 'gt', label: 'Greater Than' },
        { value: 'lt', label: 'Less Than' },
        { value: 'gte', label: 'Greater Than or Equal' },
        { value: 'lte', label: 'Less Than or Equal' },
        { value: 'contains', label: 'Contains' },
        { value: 'between', label: 'Between' }
    ];

    const addFilter = () => {
        setFilters([...filters, {
            column: headers[0]?.key || '',
            operator: 'eq',
            value: '',
            id: Date.now()
        }]);
    };

    const removeFilter = (filterId) => {
        setFilters(filters.filter(f => f.id !== filterId));
    };

    const updateFilter = (id, field, value) => {
        setFilters(filters.map(filter => 
            filter.id === id ? { ...filter, [field]: value } : filter
        ));
    };

    const clearFilters = () => {
        setFilters(Object.keys(preFilters).length > 0 ? 
            Object.entries(preFilters).map(([column, filterData]) => ({
                column,
                operator: filterData.operator || 'eq',
                value: Array.isArray(filterData.value) ? filterData.value.join(', ') : filterData.value,
                id: Date.now() + Math.random()
            })) : 
            []
        );
        fetchTableData();
    };

    const applyFilters = () => {
        fetchTableData();
    };

    const tables = [
        'village_representative',
        'schemes',
        'users',
        'villages'
    ];

    const fetchTableData = async () => {
        try {
            setLoading(true);
            const token = localStorage.getItem('token');
            
            // Transform filters into the required format
            const transformedFilters = {};
            filters.forEach(filter => {
                if (filter.value !== '') {
                    transformedFilters[filter.column] = {
                        operator: filter.operator,
                        value: filter.operator === 'between' 
                            ? filter.value.split(',').map(v => v.trim())
                            : filter.value
                    };
                }
            });

            // Add preFilters to transformed filters
            Object.entries(preFilters).forEach(([column, filterData]) => {
                if (!transformedFilters[column]) {
                    transformedFilters[column] = filterData;
                }
            });

            const response = await axios.post(import.meta.env.VITE_APP_URI + '/query_table', {
                Query: "SELECT",
                Data: {
                    table_name: selectedTable,
                    filters: transformedFilters
                }
            }, {
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                }
            });

            if (response.data.Status === 'Success' && response.data.Data.Result) {
                const data = response.data.Data.Result;
                if (data.length > 0) {
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
                alert(response.data.Message || 'Failed to fetch table data');
                setError('No data available');
                setHeaders([]);
                setTableData([]);
            }
        } catch (err) {
            console.error('Error fetching table data:', err);
            setError(err.message || 'Failed to fetch data');
            setHeaders([]);
            setTableData([]);
            alert(err.response?.data?.Message || err.message || 'Error fetching table data');
        } finally {
            setLoading(false);
        }
    };

    const handleDelete = async (row) => {
        try {
            console.log(row)
            const filters = {}
            for (const key in row) {
                filters[key] = {
                    operator: 'eq',
                    value: row[key]
                }
            }
            const token = localStorage.getItem('token');
            await axios.    post(import.meta.env.VITE_APP_URI + '/delete',
                {
                    Query: "DELETE",
                    Data: {
                        table_name: selectedTable,
                        filters: filters
                    }
                },
                {
                    headers: {
                        'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                },
            });
            if(response.data.Status === "Success") {
                fetchTableData();
            } else {
                alert(response.data.Message || 'Delete operation failed');
            } // Refresh the table
        } catch (err) {
            alert(err.response?.data?.Message || err.message || 'Failed to delete record');
            console.error('Error deleting record:', err);
            setError(err.message || 'Failed to delete record');
        }
    };

    const handleEdit = (row) => {
        console.log(row)
        setEditingRow(row);
        setEditFormData(row);
        setIsEditModalOpen(true);
    };

    const handleEditSubmit = async () => {
        try {
            const filters = {};
            for (const key in editingRow) {
                filters[key] = {
                    operator: 'eq',
                    value: editingRow[key]
                };
            }

            const token = localStorage.getItem('token');
            await axios.post(import.meta.env.VITE_APP_URI + '/update', {
                Query: "UPDATE",
                Data: {
                    table_name: selectedTable,
                    filters: filters,
                    new_values: editFormData
                }
            }, {
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                }
            });

            if(response.data.Status === "Success") {
                setIsEditModalOpen(false);
                fetchTableData();
            } else {
                alert(response.data.Message || 'Update operation failed');
            }
        } catch (err) {
            console.error('Error updating record:', err);
            setError(err.message || 'Failed to update record');
            alert(err.response?.data?.Message || err.message || 'Failed to update record');
        }
    };

    const handleInputChange = (key, value) => {
        setEditFormData(prev => ({
            ...prev,
            [key]: value
        }));
    };

    const handleAdd = () => {
        setAddFormData({});
        setIsAddModalOpen(true);
    };

    const handleAddSubmit = async () => {
        try {
            const token = localStorage.getItem('token');
            await axios.post(import.meta.env.VITE_APP_URI + '/insert', {
                Query: "INSERT",
                Data: {
                    table_name: selectedTable,
                    values: addFormData
                }
            }, {
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                }
            });

            if(response.data.Status === "Success") {
                setIsAddModalOpen(false);
                fetchTableData();
            } else {
                alert(response.data.Message || 'Add operation failed');
            }// Refresh the table
        } catch (err) {
            console.error('Error adding record:', err);
            setError(err.message || 'Failed to add record');
            alert(err.response?.data?.Message || err.message || 'Failed to add record');
        }
    };

    const handleAddInputChange = (key, value) => {
        setAddFormData(prev => ({
            ...prev,
            [key]: value
        }));
    };

    return (
        <div className="data-table-container">
            <div className="table-controls">
                {showActions && (
                    <DButton
                        text="Add New"
                        onClick={handleAdd}
                        buttonClass="success-button"
                    />
                )}
                {/* <DDropdown
                    name={selectedTable}
                    data={tables}
                    func={setSelectedTable}
                /> */}
                <div className="filter-controls">
                    <DButton
                        text="Add Filter"
                        onClick={addFilter}
                        buttonClass="primary-button"
                    />
                    {filters.length > 0 && (
                        <>
                            <DButton
                                text="Apply Filters"
                                onClick={applyFilters}
                                buttonClass="success-button"
                            />
                            <DButton
                                text="Clear Filters"
                                onClick={clearFilters}
                                buttonClass="warning-button"
                            />
                        </>
                    )}
                </div>
            </div>

            {filters.length > 0 && (
                <div className="filters-container">
                    {filters.map((filter) => (
                        <div key={filter.id} className="filter-row">
                            <select
                                value={filter.column}
                                onChange={(e) => updateFilter(filter.id, 'column', e.target.value)}
                                className="filter-select"
                            >
                                {headers.map((header) => (
                                    <option key={header.key} value={header.key}>
                                        {header.label}
                                    </option>
                                ))}
                            </select>

                            <select
                                value={filter.operator}
                                onChange={(e) => updateFilter(filter.id, 'operator', e.target.value)}
                                className="filter-select"
                            >
                                {operators.map((op) => (
                                    <option key={op.value} value={op.value}>
                                        {op.label}
                                    </option>
                                ))}
                            </select>

                            <input
                                type="text"
                                value={filter.value}
                                onChange={(e) => updateFilter(filter.id, 'value', e.target.value)}
                                placeholder={filter.operator === 'between' ? 'Enter values separated by comma' : 'Enter value'}
                                className="filter-input"
                            />

                            <DButton
                                text="Remove"
                                onClick={() => removeFilter(filter.id)}
                                buttonClass="delete-button"
                            />
                        </div>
                    ))}
                </div>
            )}
            
            {loading ? (
                <div>Loading...</div>
            ) : error ? (
                <div className="error-message">{error}</div>
            ) : (
                <>
                    <DTable
                        headers={headers}
                        data={tableData}
                        onDelete={handleDelete}
                        onEdit={handleEdit}
                    />
                    {isAddModalOpen && (
                        <Modal
                            openModal={isAddModalOpen}
                            setOpenModal={setIsAddModalOpen}
                            modalName="Add New Record"
                            height="auto"
                            width="50%"
                        >
                            <div className="edit-form">
                                {headers.map(header => (
                                    <div key={header.key} className="form-group">
                                        <label>{header.label}:</label>
                                        <input
                                            type="text"
                                            value={addFormData[header.key] || ''}
                                            onChange={(e) => handleAddInputChange(header.key, e.target.value)}
                                            className="edit-input"
                                        />
                                    </div>
                                ))}
                                <div className="edit-form-buttons">
                                    <DButton
                                        text="Save"
                                        onClick={handleAddSubmit}
                                        buttonClass="edit-btn-primary"
                                    />
                                    <DButton
                                        text="Cancel"
                                        onClick={() => setIsAddModalOpen(false)}
                                        buttonClass="delete-btn-primary"
                                    />
                                </div>
                            </div>
                        </Modal>
                    )}
                    {isEditModalOpen && editingRow && (
                        <Modal
                            openModal={isEditModalOpen}
                            setOpenModal={setIsEditModalOpen}
                            modalName="Edit Record"
                            height="auto"
                            width="50%"
                        >
                            <div className="edit-form">
                                {headers.map(header => (
                                    <div key={header.key} className="form-group">
                                        <label>{header.label}:</label>
                                        <input
                                            type="text"
                                            value={editFormData[header.key] || ''}
                                            onChange={(e) => handleInputChange(header.key, e.target.value)}
                                            className="edit-input"
                                        />
                                    </div>
                                ))}
                                <div className="edit-form-buttons">
                                    <DButton
                                        text="Save"
                                        onClick={handleEditSubmit}
                                        buttonClass="edit-btn-primary"
                                    />
                                    <DButton
                                        text="Cancel"
                                        onClick={() => setIsEditModalOpen(false)}
                                        buttonClass="delete-btn-primary"
                                    />
                                </div>
                            </div>
                        </Modal>
                    )}
                </>
            )}
        </div>
    );
};

export default DataTable; 