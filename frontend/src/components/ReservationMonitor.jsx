import React, { useState, useEffect } from 'react';
import { X, Search, Filter, Calendar as CalendarIcon } from 'lucide-react';

const ReservationMonitor = ({ isOpen, onClose }) => {
  const [currentTime, setCurrentTime] = useState(new Date());
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState('ALL');
  const [destinationFilter, setDestinationFilter] = useState('ALL');
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');
  const [selectedPax, setSelectedPax] = useState(null);

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

  // Dummy reservation data - 20 rows with updated structure
  const allReservations = [
    { date: '2025-01-15', agency: 'Skyline Tours', passenger: 'John Smith', hotel: 'Grand Seaside Hotel', stars: 5, destination: 'Antalya', checkIn: '2025-01-15', checkOut: '2025-01-22', nights: 7, room: 'Deluxe', board: 'All Inclusive', paxAdults: 2, paxChildren: 0, paxInfants: 0, status: 'CONFIRMED', note: 'Airport pickup required' },
    { date: '2025-01-16', agency: 'Blue Wave Travel', passenger: 'Emma Johnson', hotel: 'Bodrum Paradise Resort', stars: 4, destination: 'Bodrum', checkIn: '2025-01-16', checkOut: '2025-01-20', nights: 4, room: 'Standard', board: 'Half Board', paxAdults: 2, paxChildren: 2, paxInfants: 0, status: 'OPTION', note: 'Special diet request' },
    { date: '2025-01-18', agency: 'Golden Tours', passenger: 'Michael Brown', hotel: 'Istanbul Palace Hotel', stars: 5, destination: 'İstanbul', checkIn: '2025-01-18', checkOut: '2025-01-25', nights: 7, room: 'Suite', board: 'Breakfast', paxAdults: 2, paxChildren: 0, paxInfants: 0, status: 'CONFIRMED', note: 'Anniversary celebration' },
    { date: '2025-01-20', agency: 'Sunrise Travel', passenger: 'Sarah Davis', hotel: 'Fethiye Beach Resort', stars: 4, destination: 'Fethiye', checkIn: '2025-01-20', checkOut: '2025-01-27', nights: 7, room: 'Family Room', board: 'All Inclusive', paxAdults: 2, paxChildren: 3, paxInfants: 0, status: 'CONFIRMED', note: '' },
    { date: '2025-01-17', agency: 'Dream Holidays', passenger: 'David Wilson', hotel: 'Marmaris Bay Hotel', stars: 3, destination: 'Marmaris', checkIn: '2025-01-17', checkOut: '2025-01-24', nights: 7, room: 'Standard', board: 'Full Board', paxAdults: 2, paxChildren: 0, paxInfants: 0, status: 'CANCELLED', note: 'Customer cancelled' },
    { date: '2025-01-19', agency: 'Paradise Tours', passenger: 'Lisa Anderson', hotel: 'Kaş Boutique Hotel', stars: 4, destination: 'Kaş', checkIn: '2025-01-19', checkOut: '2025-01-23', nights: 4, room: 'Deluxe', board: 'All Inclusive', paxAdults: 2, paxChildren: 1, paxInfants: 0, status: 'CONFIRMED', note: 'Honeymoon package' },
    { date: '2025-01-21', agency: 'Ocean View Travel', passenger: 'Robert Taylor', hotel: 'Çeşme Grand Resort', stars: 5, destination: 'Çeşme', checkIn: '2025-01-21', checkOut: '2025-01-28', nights: 7, room: 'Superior', board: 'Half Board', paxAdults: 2, paxChildren: 0, paxInfants: 0, status: 'OPTION', note: 'Waiting for confirmation' },
    { date: '2025-01-16', agency: 'Sunny Days Tours', passenger: 'Jennifer Martinez', hotel: 'Alanya Beach Club', stars: 4, destination: 'Alanya', checkIn: '2025-01-16', checkOut: '2025-01-30', nights: 14, room: 'Standard', board: 'All Inclusive', paxAdults: 2, paxChildren: 3, paxInfants: 1, status: 'CONFIRMED', note: 'Large family group' },
    { date: '2025-01-22', agency: 'Crystal Travel', passenger: 'William Garcia', hotel: 'Kuşadası Premium Hotel', stars: 5, destination: 'Kuşadası', checkIn: '2025-01-22', checkOut: '2025-01-26', nights: 4, room: 'Suite', board: 'Breakfast', paxAdults: 2, paxChildren: 0, paxInfants: 0, status: 'CONFIRMED', note: 'VIP treatment requested' },
    { date: '2025-01-18', agency: 'Elite Holidays', passenger: 'Mary Rodriguez', hotel: 'Side Star Resort', stars: 4, destination: 'Side', checkIn: '2025-01-18', checkOut: '2025-01-25', nights: 7, room: 'Deluxe', board: 'Full Board', paxAdults: 2, paxChildren: 2, paxInfants: 0, status: 'OPTION', note: 'Price negotiation pending' },
    { date: '2025-01-20', agency: 'Adventure Travel', passenger: 'James Lee', hotel: 'Kalkan View Hotel', stars: 3, destination: 'Kalkan', checkIn: '2025-01-20', checkOut: '2025-01-24', nights: 4, room: 'Standard', board: 'Half Board', paxAdults: 2, paxChildren: 0, paxInfants: 0, status: 'CONFIRMED', note: '' },
    { date: '2025-01-23', agency: 'Royal Tours', passenger: 'Patricia White', hotel: 'Göcek Luxury Resort', stars: 5, destination: 'Göcek', checkIn: '2025-01-23', checkOut: '2025-01-30', nights: 7, room: 'Villa', board: 'All Inclusive', paxAdults: 4, paxChildren: 3, paxInfants: 1, status: 'CONFIRMED', note: 'Corporate group booking' },
    { date: '2025-01-17', agency: 'Magic Travel', passenger: 'Christopher Harris', hotel: 'Belek Golf Resort', stars: 5, destination: 'Belek', checkIn: '2025-01-17', checkOut: '2025-01-21', nights: 4, room: 'Superior', board: 'All Inclusive', paxAdults: 2, paxChildren: 1, paxInfants: 0, status: 'CANCELLED', note: 'Medical reasons' },
    { date: '2025-01-19', agency: 'Horizon Tours', passenger: 'Barbara Martin', hotel: 'Didim Sunset Hotel', stars: 4, destination: 'Didim', checkIn: '2025-01-19', checkOut: '2025-01-26', nights: 7, room: 'Deluxe', board: 'Full Board', paxAdults: 2, paxChildren: 0, paxInfants: 0, status: 'CONFIRMED', note: 'Wheelchair accessible room' },
    { date: '2025-01-24', agency: 'Prestige Travel', passenger: 'Daniel Thompson', hotel: 'Kemer Marina Resort', stars: 5, destination: 'Kemer', checkIn: '2025-01-24', checkOut: '2025-01-31', nights: 7, room: 'Suite', board: 'All Inclusive', paxAdults: 2, paxChildren: 0, paxInfants: 0, status: 'OPTION', note: 'Payment pending' },
    { date: '2025-01-21', agency: 'Pearl Holidays', passenger: 'Nancy Martinez', hotel: 'Ölüdeniz Beach Hotel', stars: 4, destination: 'Ölüdeniz', checkIn: '2025-01-21', checkOut: '2025-01-28', nights: 7, room: 'Family Room', board: 'Half Board', paxAdults: 2, paxChildren: 3, paxInfants: 0, status: 'CONFIRMED', note: 'Kids club required' },
    { date: '2025-01-18', agency: 'Diamond Tours', passenger: 'Paul Jackson', hotel: 'Dalyan Riverside Hotel', stars: 3, destination: 'Dalyan', checkIn: '2025-01-18', checkOut: '2025-01-22', nights: 4, room: 'Standard', board: 'Breakfast', paxAdults: 2, paxChildren: 0, paxInfants: 0, status: 'CONFIRMED', note: '' },
    { date: '2025-01-25', agency: 'Sapphire Travel', passenger: 'Karen White', hotel: 'Turgutreis Spa Resort', stars: 5, destination: 'Turgutreis', checkIn: '2025-01-25', checkOut: '2025-02-01', nights: 7, room: 'Deluxe', board: 'All Inclusive', paxAdults: 2, paxChildren: 2, paxInfants: 0, status: 'CONFIRMED', note: 'Spa package included' },
    { date: '2025-01-20', agency: 'Emerald Tours', passenger: 'Mark Lewis', hotel: 'Çıralı Eco Resort', stars: 4, destination: 'Çıralı', checkIn: '2025-01-20', checkOut: '2025-01-27', nights: 7, room: 'Superior', board: 'Full Board', paxAdults: 2, paxChildren: 1, paxInfants: 0, status: 'OPTION', note: 'Upgrade consideration' },
    { date: '2025-01-22', agency: 'Ruby Holidays', passenger: 'Betty Walker', hotel: 'Patara Beach Villa', stars: 5, destination: 'Patara', checkIn: '2025-01-22', checkOut: '2025-01-29', nights: 7, room: 'Villa', board: 'All Inclusive', paxAdults: 3, paxChildren: 2, paxInfants: 1, status: 'CONFIRMED', note: 'Beach front villa' },
  ];

  // Get unique destinations for filter
  const uniqueDestinations = [...new Set(allReservations.map(r => r.destination))];

  // Filter reservations based on search, status, destination, and date range
  const filteredReservations = allReservations.filter(reservation => {
    // Search filter
    const searchLower = searchQuery.toLowerCase();
    const matchesSearch = !searchQuery || 
      reservation.passenger.toLowerCase().includes(searchLower) ||
      reservation.agency.toLowerCase().includes(searchLower) ||
      reservation.hotel.toLowerCase().includes(searchLower) ||
      reservation.destination.toLowerCase().includes(searchLower) ||
      reservation.note.toLowerCase().includes(searchLower);

    // Status filter
    const matchesStatus = statusFilter === 'ALL' || reservation.status === statusFilter;

    // Destination filter
    const matchesDestination = destinationFilter === 'ALL' || reservation.destination === destinationFilter;

    // Date range filter
    const reservationDate = new Date(reservation.checkIn);
    const start = startDate ? new Date(startDate) : null;
    const end = endDate ? new Date(endDate) : null;
    const matchesDateRange = (!start || reservationDate >= start) && (!end || reservationDate <= end);

    return matchesSearch && matchesStatus && matchesDestination && matchesDateRange;
  });

  const getStatusBadge = (status) => {
    const statusStyles = {
      CONFIRMED: 'bg-green-500 text-white',
      OPTION: 'bg-yellow-500 text-white',
      CANCELLED: 'bg-red-500 text-white',
    };
    return statusStyles[status] || 'bg-gray-500 text-white';
  };

  const formatPax = (adults, children, infants) => {
    const parts = [];
    if (adults > 0) parts.push(`${adults}A`);
    if (children > 0) parts.push(`${children}C`);
    if (infants > 0) parts.push(`${infants}I`);
    return parts.join(' + ');
  };

  const getTotalPax = (adults, children, infants) => {
    return adults + children + infants;
  };

  const renderStars = (count) => {
    return '⭐'.repeat(count);
  };

  const handleClearFilters = () => {
    setSearchQuery('');
    setStatusFilter('ALL');
    setDestinationFilter('ALL');
    setStartDate('');
    setEndDate('');
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
