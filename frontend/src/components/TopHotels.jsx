import { Hotel, TrendingUp } from 'lucide-react';

const TopHotels = ({ data }) => {
  return (
    <div
      className="bg-white rounded-2xl p-6 lg:p-8 border border-slate-200 shadow-lg"
      style={{
        boxShadow: "0 8px 32px rgba(8, 145, 178, 0.12)"
      }}
      data-testid="top-hotels"
    >
      <div className="flex items-center gap-3 mb-6">
        <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-amber-500 to-orange-600 flex items-center justify-center shadow-lg">
          <Hotel className="w-6 h-6 text-white" />
        </div>
        <div>
          <h3 className="text-lg font-bold text-slate-800">En Yoğun Oteller</h3>
          <p className="text-sm text-slate-500">Bu ay</p>
        </div>
      </div>

      <div className="space-y-4">
        {data.map((hotel, index) => (
          <div
            key={index}
            className="flex items-center justify-between p-4 rounded-xl bg-gradient-to-r from-slate-50 to-slate-100 hover:from-cyan-50 hover:to-teal-50 transition-all duration-300 border border-slate-200"
            data-testid={`hotel-item-${index}`}
          >
            <div className="flex items-center gap-4">
              <div className="w-10 h-10 rounded-lg bg-white flex items-center justify-center font-bold text-slate-700 shadow-sm">
                {index + 1}
              </div>
              <div>
                <p className="font-semibold text-slate-800">{hotel.name}</p>
                <p className="text-sm text-slate-500">{hotel.location}</p>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <TrendingUp className="w-4 h-4 text-green-500" />
              <span className="font-bold text-slate-800">{hotel.guests}</span>
              <span className="text-sm text-slate-500">misafir</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default TopHotels;
