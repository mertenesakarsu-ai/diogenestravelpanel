import React, { useState, useEffect } from 'react';
import { X } from 'lucide-react';

const ReservationMonitor = ({ isOpen, onClose }) => {
  const [currentTime, setCurrentTime] = useState(new Date());

  useEffect(() => {
    if (isOpen) {
      const timer = setInterval(() => {
        setCurrentTime(new Date());
      }, 1000);
      return () => clearInterval(timer);
    }
  }, [isOpen]);

  const formatDateTime = (date) => {
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    const hours = String(date.getHours()).padStart(2, '0');
    const minutes = String(date.getMinutes()).padStart(2, '0');
    return `${year}-${month}-${day} ${hours}:${minutes}`;
  };

  // Dummy reservation data - 20 rows
  const reservations = [
    { time: '08:00', agency: 'Skyline Tours', passenger: 'John Smith', service: 'Hotel + Transfer', destination: 'Antalya', checkIn: '2025-01-15', checkOut: '2025-01-22', nights: 7, room: 'Deluxe', board: 'All Inclusive', pax: 2, status: 'CONFIRMED', note: 'Airport pickup required' },
    { time: '08:30', agency: 'Blue Wave Travel', passenger: 'Emma Johnson', service: 'Hotel Only', destination: 'Bodrum', checkIn: '2025-01-16', checkOut: '2025-01-20', nights: 4, room: 'Standard', board: 'Half Board', pax: 4, status: 'OPTION', note: 'Special diet request' },
    { time: '09:00', agency: 'Golden Tours', passenger: 'Michael Brown', service: 'Full Package', destination: 'İstanbul', checkIn: '2025-01-18', checkOut: '2025-01-25', nights: 7, room: 'Suite', board: 'Breakfast', pax: 2, status: 'CONFIRMED', note: 'Anniversary celebration' },
    { time: '09:15', agency: 'Sunrise Travel', passenger: 'Sarah Davis', service: 'Hotel + Transfer', destination: 'Fethiye', checkIn: '2025-01-20', checkOut: '2025-01-27', nights: 7, room: 'Family Room', board: 'All Inclusive', pax: 5, status: 'CONFIRMED', note: '' },
    { time: '09:45', agency: 'Dream Holidays', passenger: 'David Wilson', service: 'Hotel Only', destination: 'Marmaris', checkIn: '2025-01-17', checkOut: '2025-01-24', nights: 7, room: 'Standard', board: 'Full Board', pax: 2, status: 'CANCELLED', note: 'Customer cancelled' },
    { time: '10:00', agency: 'Paradise Tours', passenger: 'Lisa Anderson', service: 'Full Package', destination: 'Kaş', checkIn: '2025-01-19', checkOut: '2025-01-23', nights: 4, room: 'Deluxe', board: 'All Inclusive', pax: 3, status: 'CONFIRMED', note: 'Honeymoon package' },
    { time: '10:30', agency: 'Ocean View Travel', passenger: 'Robert Taylor', service: 'Hotel + Transfer', destination: 'Çeşme', checkIn: '2025-01-21', checkOut: '2025-01-28', nights: 7, room: 'Superior', board: 'Half Board', pax: 2, status: 'OPTION', note: 'Waiting for confirmation' },
    { time: '11:00', agency: 'Sunny Days Tours', passenger: 'Jennifer Martinez', service: 'Hotel Only', destination: 'Alanya', checkIn: '2025-01-16', checkOut: '2025-01-30', nights: 14, room: 'Standard', board: 'All Inclusive', pax: 6, status: 'CONFIRMED', note: 'Large family group' },
    { time: '11:30', agency: 'Crystal Travel', passenger: 'William Garcia', service: 'Full Package', destination: 'Kuşadası', checkIn: '2025-01-22', checkOut: '2025-01-26', nights: 4, room: 'Suite', board: 'Breakfast', pax: 2, status: 'CONFIRMED', note: 'VIP treatment requested' },
    { time: '12:00', agency: 'Elite Holidays', passenger: 'Mary Rodriguez', service: 'Hotel + Transfer', destination: 'Side', checkIn: '2025-01-18', checkOut: '2025-01-25', nights: 7, room: 'Deluxe', board: 'Full Board', pax: 4, status: 'OPTION', note: 'Price negotiation pending' },
    { time: '12:30', agency: 'Adventure Travel', passenger: 'James Lee', service: 'Hotel Only', destination: 'Kalkan', checkIn: '2025-01-20', checkOut: '2025-01-24', nights: 4, room: 'Standard', board: 'Half Board', pax: 2, status: 'CONFIRMED', note: '' },
    { time: '13:00', agency: 'Royal Tours', passenger: 'Patricia White', service: 'Full Package', destination: 'Göcek', checkIn: '2025-01-23', checkOut: '2025-01-30', nights: 7, room: 'Villa', board: 'All Inclusive', pax: 8, status: 'CONFIRMED', note: 'Corporate group booking' },
    { time: '13:30', agency: 'Magic Travel', passenger: 'Christopher Harris', service: 'Hotel + Transfer', destination: 'Belek', checkIn: '2025-01-17', checkOut: '2025-01-21', nights: 4, room: 'Superior', board: 'All Inclusive', pax: 3, status: 'CANCELLED', note: 'Medical reasons' },
    { time: '14:00', agency: 'Horizon Tours', passenger: 'Barbara Martin', service: 'Hotel Only', destination: 'Didim', checkIn: '2025-01-19', checkOut: '2025-01-26', nights: 7, room: 'Deluxe', board: 'Full Board', pax: 2, status: 'CONFIRMED', note: 'Wheelchair accessible room' },
    { time: '14:30', agency: 'Prestige Travel', passenger: 'Daniel Thompson', service: 'Full Package', destination: 'Kemer', checkIn: '2025-01-24', checkOut: '2025-01-31', nights: 7, room: 'Suite', board: 'All Inclusive', pax: 2, status: 'OPTION', note: 'Payment pending' },
    { time: '15:00', agency: 'Pearl Holidays', passenger: 'Nancy Martinez', service: 'Hotel + Transfer', destination: 'Ölüdeniz', checkIn: '2025-01-21', checkOut: '2025-01-28', nights: 7, room: 'Family Room', board: 'Half Board', pax: 5, status: 'CONFIRMED', note: 'Kids club required' },
    { time: '15:30', agency: 'Diamond Tours', passenger: 'Paul Jackson', service: 'Hotel Only', destination: 'Dalyan', checkIn: '2025-01-18', checkOut: '2025-01-22', nights: 4, room: 'Standard', board: 'Breakfast', pax: 2, status: 'CONFIRMED', note: '' },
    { time: '16:00', agency: 'Sapphire Travel', passenger: 'Karen White', service: 'Full Package', destination: 'Turgutreis', checkIn: '2025-01-25', checkOut: '2025-02-01', nights: 7, room: 'Deluxe', board: 'All Inclusive', pax: 4, status: 'CONFIRMED', note: 'Spa package included' },
    { time: '16:30', agency: 'Emerald Tours', passenger: 'Mark Lewis', service: 'Hotel + Transfer', destination: 'Çıralı', checkIn: '2025-01-20', checkOut: '2025-01-27', nights: 7, room: 'Superior', board: 'Full Board', pax: 3, status: 'OPTION', note: 'Upgrade consideration' },
    { time: '17:00', agency: 'Ruby Holidays', passenger: 'Betty Walker', service: 'Hotel Only', destination: 'Patara', checkIn: '2025-01-22', checkOut: '2025-01-29', nights: 7, room: 'Villa', board: 'All Inclusive', pax: 6, status: 'CONFIRMED', note: 'Beach front villa' },
  ];

  const getStatusBadge = (status) => {
    const statusStyles = {
      CONFIRMED: 'bg-green-500 text-white',
      OPTION: 'bg-yellow-500 text-white',
      CANCELLED: 'bg-red-500 text-white',
    };
    return statusStyles[status] || 'bg-gray-500 text-white';
  };

  if (!isOpen) return null;

  return (
    <div 
      className="fixed inset-0 z-50 flex items-center justify-center p-4"
      style={{ backgroundColor: 'rgba(0, 0, 0, 0.75)' }}
      onClick={onClose}
    >
      {/* Modal Container */}
      <div 
        className="bg-slate-100 rounded-2xl shadow-2xl w-full max-w-[95vw] max-h-[95vh] flex flex-col"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header Bar */}
        <div className="bg-gradient-to-r from-slate-700 to-slate-800 text-white px-8 py-6 rounded-t-2xl flex items-center justify-between">
          <div className="flex items-center gap-4">
            <h1 className="text-3xl font-bold tracking-wide">RESERVATION MONITOR</h1>
          </div>
          
          <div className="flex items-center gap-6">
            <div className="text-xl font-semibold bg-slate-600 px-6 py-3 rounded-lg">
              {formatDateTime(currentTime)}
            </div>
            
            <button
              onClick={onClose}
              className="hover:bg-slate-600 rounded-full p-2 transition-colors"
              aria-label="Close"
            >
              <X className="w-8 h-8" />
            </button>
          </div>
        </div>

        {/* Table Container */}
        <div className="flex-1 overflow-auto bg-white m-4 rounded-xl shadow-inner">
          <table className="w-full">
            <thead className="sticky top-0 bg-gradient-to-r from-cyan-600 to-teal-600 text-white shadow-md z-10">
              <tr>
                <th className="px-4 py-4 text-left text-base font-semibold">Time</th>
                <th className="px-4 py-4 text-left text-base font-semibold">Agency</th>
                <th className="px-4 py-4 text-left text-base font-semibold">Passenger</th>
                <th className="px-4 py-4 text-left text-base font-semibold">Service</th>
                <th className="px-4 py-4 text-left text-base font-semibold">Destination</th>
                <th className="px-4 py-4 text-left text-base font-semibold">Check-in</th>
                <th className="px-4 py-4 text-left text-base font-semibold">Check-out</th>
                <th className="px-4 py-4 text-center text-base font-semibold">Nights</th>
                <th className="px-4 py-4 text-left text-base font-semibold">Room</th>
                <th className="px-4 py-4 text-left text-base font-semibold">Board</th>
                <th className="px-4 py-4 text-center text-base font-semibold">Pax</th>
                <th className="px-4 py-4 text-center text-base font-semibold">Status</th>
                <th className="px-4 py-4 text-left text-base font-semibold">Note</th>
              </tr>
            </thead>
            <tbody>
              {reservations.map((reservation, index) => (
                <tr 
                  key={index}
                  className={`border-b border-slate-200 hover:bg-cyan-50 transition-colors ${
                    index % 2 === 0 ? 'bg-white' : 'bg-slate-50'
                  }`}
                >
                  <td className="px-4 py-4 text-base font-semibold text-slate-700">{reservation.time}</td>
                  <td className="px-4 py-4 text-base text-slate-700">{reservation.agency}</td>
                  <td className="px-4 py-4 text-base font-medium text-slate-800">{reservation.passenger}</td>
                  <td className="px-4 py-4 text-base text-slate-600">{reservation.service}</td>
                  <td className="px-4 py-4 text-base font-medium text-cyan-700">{reservation.destination}</td>
                  <td className="px-4 py-4 text-base text-slate-600">{reservation.checkIn}</td>
                  <td className="px-4 py-4 text-base text-slate-600">{reservation.checkOut}</td>
                  <td className="px-4 py-4 text-base text-center font-semibold text-slate-700">{reservation.nights}</td>
                  <td className="px-4 py-4 text-base text-slate-600">{reservation.room}</td>
                  <td className="px-4 py-4 text-base text-slate-600">{reservation.board}</td>
                  <td className="px-4 py-4 text-base text-center font-semibold text-slate-700">{reservation.pax}</td>
                  <td className="px-4 py-4 text-center">
                    <span className={`px-4 py-2 rounded-full text-sm font-bold ${getStatusBadge(reservation.status)}`}>
                      {reservation.status}
                    </span>
                  </td>
                  <td className="px-4 py-4 text-base text-slate-500 italic">{reservation.note || '-'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default ReservationMonitor;
