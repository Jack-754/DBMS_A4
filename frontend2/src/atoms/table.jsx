import React, { useState } from "react";

import './table.css';
import DButton from "./DButton";
// import { ReactComponent as NoDataImage } from '/icons/no-data.svg';

const DTable = ({ headers, data, onDelete, onEdit }) => {
  if (!data || data.length === 0) {
    return (
      <div className="no-data-container">
        <img src="/icons/no-data.svg" alt="No Data" className="no-data-image" />
        <h3 className="no-data-text">No expenses available</h3>
      </div>
    );
  }
  return (
    <div className="recent-transactions">
      <table role="grid" aria-label="Expenses table">
        <thead>
          <tr>
            {headers.map((header) => (
              <th key={header.key} scope="col">{header.label}</th>
            ))}
            <th scope="col" aria-label="Delete action"></th>
            <th scope="col" aria-label="Edit action"></th>
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
                  onClick={() => onDelete(row)}
                  buttonClass="delete-btn-primary"
                  aria-label={`Delete expense ${row.id}`}
                />
              </td>
              <td>
                <DButton
                  text="Edit"
                  onClick={() => onEdit(row)}
                  buttonClass="edit-btn-primary"
                  aria-label={`Edit expense ${row.id}`}
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