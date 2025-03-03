import React from 'react';
import DataTable from '../../components/DataTable';

const Schemes = () => {
  return (
    <div>
      <h1>Government Schemes</h1>
      <div>
        {/* Add list of schemes with enrollment options */}
        <div className="schemes-list">
          <DataTable tableName="schemes" />
          {/* Add scheme cards or list items here */}
        </div>
      </div>
    </div>
  );
};

export default Schemes; 