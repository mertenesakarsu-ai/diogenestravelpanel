import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts';

const ArrivalDepartureChart = ({ data }) => {
  return (
    <div className="h-80" data-testid="arrival-departure-chart">
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={data} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
          <XAxis 
            dataKey="date" 
            stroke="#64748b"
            style={{ fontSize: '12px', fontWeight: '500' }}
          />
          <YAxis 
            stroke="#64748b"
            style={{ fontSize: '12px', fontWeight: '500' }}
          />
          <Tooltip 
            contentStyle={{
              backgroundColor: 'white',
              border: '1px solid #e2e8f0',
              borderRadius: '12px',
              boxShadow: '0 4px 12px rgba(0,0,0,0.1)'
            }}
            cursor={{ fill: 'rgba(8, 145, 178, 0.05)' }}
          />
          <Legend 
            wrapperStyle={{
              paddingTop: '20px',
              fontSize: '14px',
              fontWeight: '500'
            }}
          />
          <Bar 
            dataKey="arrivals" 
            fill="#0891b2" 
            name="Geliş"
            radius={[8, 8, 0, 0]}
          />
          <Bar 
            dataKey="departures" 
            fill="#14b8a6" 
            name="Gidiş"
            radius={[8, 8, 0, 0]}
          />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
};

export default ArrivalDepartureChart;
