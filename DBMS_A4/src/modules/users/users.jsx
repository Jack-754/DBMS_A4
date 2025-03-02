import React from 'react';

const Users = ({ canEdit, canDelete }) => {
  return (
    <div>
      <h1>Users Management</h1>
      <div>
        {/* Add user list table here */}
        <table>
          <thead>
            <tr>
              <th>Name</th>
              <th>Role</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {/* Add user rows here */}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default Users; 