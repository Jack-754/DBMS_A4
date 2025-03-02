import React, { useState } from "react";

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