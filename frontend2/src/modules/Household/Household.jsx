import React from 'react';
import DataTable from '../../components/DataTable';

const Household = () => {
  return (
    <div>
      <h1>Household</h1>
      <div>
        {/* Add data visualization components here */}
        <div className="Household">
            
          <DataTable tableName="households" />
          {/* Add charts, graphs, and statistics */}
        </div>
      </div>
    </div>
  );
};

export default Household; 