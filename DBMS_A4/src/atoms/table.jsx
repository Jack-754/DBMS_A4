import React, { useState } from "react";
// import "./table.css"; // Import your CSS file

// const DynamicTable = ({ columns, data, onButtonClick, onAddCustomer }) => {
//   const [searchTerm, setSearchTerm] = useState("");
//   const [rowsToShow, setRowsToShow] = useState(5);
//   const [sortConfig, setSortConfig] = useState({ column: null, order: null });
//   const [originalData] = useState([...data]); // Store the original data

//   // Function to determine if a column is numeric
//   const isNumericColumn = (col) => {
//     return data.every((row) => !isNaN(parseFloat(row[col])) && isFinite(row[col]));
//   };

//   // Sorting function
//   const sortData = (dataToSort) => {
//     if (!sortConfig.column) return dataToSort;

//     if (sortConfig.order === "default") {
//       return [...originalData]; // Reset to original order
//     }

//     return [...dataToSort].sort((a, b) => {
//       const aValue = a[sortConfig.column] || "";
//       const bValue = b[sortConfig.column] || "";

//       if (isNumericColumn(sortConfig.column)) {
//         return sortConfig.order === "asc" ? aValue - bValue : bValue - aValue;
//       } else {
//         return sortConfig.order === "asc"
//           ? aValue.toString().localeCompare(bValue.toString())
//           : bValue.toString().localeCompare(aValue.toString());
//       }
//     });
//   };

//   // Handle sorting selection from dropdown
//   const handleSortChange = (column, order) => {
//     setSortConfig({ column, order });
//   };

//   // Filter data based on search input
//   const filteredData = data.filter((row) =>
//     columns.some(
//       (col) =>
//         row[col] &&
//         row[col].toString().toLowerCase().includes(searchTerm.toLowerCase())
//     )
//   );

//   // Sort the filtered data
//   const sortedData = sortData(filteredData);

//   // Ensure table maintains size (fills empty rows)
//   const displayedData = [...sortedData, ...Array(Math.max(0, rowsToShow - sortedData.length)).fill({})];

//   return (
//     <div className="table-container">
//       {/* Controls (Search + Dropdown + Add Customer Button) */}
//       <div className="table-controls">
//         <div className="table-controls-1">
//           <select
//             className="row-dropdown"
//             value={rowsToShow}
//             onChange={(e) => setRowsToShow(Number(e.target.value))}
//           >
//             <option value={5}>Show 5 rows</option>
//             <option value={10}>Show 10 rows</option>
//             <option value={15}>Show 15 rows</option>
//             <option value={data.length}>Show All</option>
//           </select>
//           <input
//             type="text"
//             placeholder="Search..."
//             className="search-input"
//             value={searchTerm}
//             onChange={(e) => setSearchTerm(e.target.value)}
//           />
//         </div>

//         <button className="add-customer-btn" onClick={onAddCustomer}>
//           Add Customer
//         </button>
//       </div>

//       {/* Table */}
//       <table className="dynamic-table">
//         {/* Table Head */}
//         <thead>
//           <tr>
//             {columns.map((column, index) => (
//               <th key={index} className="sortable-header">
//                 <div className="header-container">
//                   {column}
//                   <select
//                     className="sort-dropdown"
//                     onChange={(e) => handleSortChange(column, e.target.value)}
//                   >
//                     <option value="default">🔄</option>
//                     <option value="asc">⬆️</option>
//                     <option value="desc">⬇️</option>
//                   </select>
//                 </div>
//               </th>
//             ))}
//             <th>Actions</th>
//           </tr>
//         </thead>

//         {/* Table Body */}
//         <tbody>
//           {displayedData.slice(0, rowsToShow).map((row, rowIndex) => (
//             <tr key={rowIndex}>
//               {columns.map((col, colIndex) => (
//                 <td key={colIndex}>{row[col] || "—"}</td> // Placeholder for empty rows
//               ))}
//               <td className="buttons_container">
//                 {row.buttons ? (
//                   row.buttons.map((button, btnIndex) => (
//                     <button
//                       key={btnIndex}
//                       className="action-button"
//                       onClick={() => onButtonClick(button, row)}
//                     >
//                       {button.label}
//                     </button>
//                   ))
//                 ) : (
//                   "—"
//                 )}
//               </td>
//             </tr>
//           ))}
//         </tbody>
//       </table>
//     </div>
//   );
// };

// export default DynamicTable;


// import { useState } from 'react';
// import './table1.css';

// const DTable = () => {
//   const initialTransactions = [
//     {
//       id: 1,
//       amount: '$100',
//       date: 'Feb 28',
//       description: 'Eclair',
//       category: 'Investment',
//       paymentMode: 'EMI'
//     },
//     {
//       id: 2,
//       amount: '$150',
//       date: 'Mar 01',
//       description: 'Website Hosting',
//       category: 'Technology',
//       paymentMode: 'Credit Card'
//     },
//     {
//       id: 3,
//       amount: '$200',
//       date: 'Mar 05',
//       description: 'Office Supplies',
//       category: 'Operations',
//       paymentMode: 'Debit Card'
//     }
//   ];

//   const [transactions, setTransactions] = useState(initialTransactions);

//   const handleDelete = (id) => {
//     setTransactions(transactions.filter(transaction => transaction.id !== id));
//   };

//   const handleEdit = (id) => {
//     // Implement edit logic here
//     console.log('Edit transaction with id:', id);
//   };

//   return (
//     <div className="recent-transactions card">
//       <h3>Recent Transactions</h3>
//       <table>
//         <thead>
//           <tr>
//             <th>Amount</th>
//             <th>Date</th>
//             <th>Description</th>
//             <th>Category</th>
//             <th>Payment Mode</th>
//             <th></th>
//             <th></th>
//           </tr>
//         </thead>
//         <tbody>
//           {transactions.map((transaction) => (
//             <tr key={transaction.id}>
//               <td>{transaction.amount}</td>
//               <td>{transaction.date}</td>
//               <td>{transaction.description}</td>
//               <td>{transaction.category}</td>
//               <td>{transaction.paymentMode}</td>
//               <td>
//                 <button 
//                   onClick={() => handleDelete(transaction.id)}
//                   className="delete-btn"
//                 >
//                   Delete
//                 </button>
//               </td>
//               <td>
//                 <button 
//                   onClick={() => handleEdit(transaction.id)}
//                   className="edit-btn"
//                 >
//                   Edit
//                 </button>
//               </td>
//             </tr>
//           ))}
//         </tbody>
//       </table>
//     </div>
//   );
// };

// export default DTable;

import './table.css';
import DButton from "./DButton";
// import { ReactComponent as NoDataImage } from '/icons/no-data.svg';

const DTable = ({ headers, data, onDelete, onEdit }) => {
  if (!data || data.length === 0) {
    return (
      <div className="no-data-container ">
        <img src="/icons/no-data.svg" alt="No Data" className="no-data-image" />
        <h3 className="no-data-text">No expenses available</h3>
      </div>
    );
  }
  return (
    <div className="recent-transactions card">
      <table>
        <thead>
          <tr>
            {headers.map((header) => (
              <th key={header.key}>{header.label}</th>
            ))}
            <th></th>
            <th></th>
          </tr>
        </thead>
        <tbody>
          {data.map((row) => (
            <tr key={row.id}>
              {headers.map((header) => (
                <td key={`${row.id}-${header.key}`}>{row[header.key]}</td>
              ))}
              <td>
                <DButton
                  text="Delete"
                  onClick={() => onDelete(row.id)}
                  buttonClass="delete-btn-primary"
                />
              </td>
              <td>
                <DButton
                  text="Edit"
                  onClick={() => onEdit(row.id)}
                  buttonClass="edit-btn-primary"
                />
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default DTable;