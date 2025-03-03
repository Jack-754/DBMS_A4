import React from 'react';
import DataTable from '../../components/DataTable';

const Pmembers = () => {
  return (
    <div>
      <h1>Panchayat Members</h1>
      <div>
        {/* Add data visualization components here */}
        <div className="PanchayatMembers">
            
          <DataTable tableName="panchayat_employees" />
          {/* Add charts, graphs, and statistics */}
        </div>
      </div>
    </div>
  );
};

export default Pmembers; 