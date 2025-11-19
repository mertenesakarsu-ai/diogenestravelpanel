import React, { useState, useEffect } from 'react';
import { X, Search, Filter, Calendar as CalendarIcon, ArrowUpDown, ArrowUp, ArrowDown } from 'lucide-react';
import JourneyTimeline from './JourneyTimeline';

const ReservationMonitor = ({ isOpen, onClose }) => {
  const [currentTime, setCurrentTime] = useState(new Date());
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState('ALL');
  const [destinationFilter, setDestinationFilter] = useState('ALL');
  const [agencyFilter, setAgencyFilter] = useState('ALL');
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');
  const [appliedStartDate, setAppliedStartDate] = useState('');
  const [appliedEndDate, setAppliedEndDate] = useState('');
  const [selectedPax, setSelectedPax] = useState(null);
  const [selectedReservationId, setSelectedReservationId] = useState(null);
  const [showJourneyTimeline, setShowJourneyTimeline] = useState(false);
  const [checkInSort, setCheckInSort] = useState('asc'); // 'asc', 'desc', or null
  const [checkOutSort, setCheckOutSort] = useState(null); // 'asc', 'desc', or null

  useEffect(() => {
    if (isOpen) {
      const timer = setInterval(() => {
        setCurrentTime(new Date());
      }, 1000);
      return () => clearInterval(timer);
    }
  }, [isOpen]);

  const formatDateTime = (date) => {
    const day = String(date.getDate()).padStart(2, '0');
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const year = date.getFullYear();
    const hours = String(date.getHours()).padStart(2, '0');
    const minutes = String(date.getMinutes()).padStart(2, '0');
    return `${day}.${month}.${year} ${hours}:${minutes}`;
  };

  const formatDate = (dateString) => {
    if (!dateString) return '';
    const date = new Date(dateString);
    const day = String(date.getDate()).padStart(2, '0');
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const year = date.getFullYear();
    return `${day}.${month}.${year}`;
  };

  // Source agencies
  const sourceAgencies = ['THV', 'EURO TOURS', 'SELECT HOLIDAYS', 'AZURO'];

  // Get agency badge color
  const getAgencyBadgeColor = (agency) => {
    const colors = {
      'THV': 'bg-blue-500 text-white',
      'EURO TOURS': 'bg-green-500 text-white',
      'SELECT HOLIDAYS': 'bg-purple-500 text-white',
      'AZURO': 'bg-orange-500 text-white'
    };
    return colors[agency] || 'bg-gray-500 text-white';
  };

  // Dummy reservation data - 20 rows with updated structure (including source agency and reservation IDs)
  const allReservations = [
    { id: 'res-001', date: '15.01.2025', sourceAgency: 'THV', agency: 'Skyline Tours', passenger: 'John Smith', hotel: 'Grand Seaside Hotel', stars: 5, destination: 'Antalya', checkIn: '2025-01-15', checkOut: '2025-01-22', nights: 7, room: 'Deluxe', board: 'All Inclusive', paxAdults: 2, paxChildren: 0, paxInfants: 0, status: 'CONFIRMED', note: 'Airport pickup required' },
    { id: 'res-002', date: '16.01.2025', sourceAgency: 'EURO TOURS', agency: 'Blue Wave Travel', passenger: 'Emma Johnson', hotel: 'Bodrum Paradise Resort', stars: 4, destination: 'Bodrum', checkIn: '2025-01-16', checkOut: '2025-01-20', nights: 4, room: 'Standard', board: 'Half Board', paxAdults: 2, paxChildren: 2, paxInfants: 0, status: 'OPTION', note: 'Special diet request' },
    { id: 'res-003', date: '18.01.2025', sourceAgency: 'SELECT HOLIDAYS', agency: 'Golden Tours', passenger: 'Michael Brown', hotel: 'Istanbul Palace Hotel', stars: 5, destination: 'İstanbul', checkIn: '2025-01-18', checkOut: '2025-01-25', nights: 7, room: 'Suite', board: 'Breakfast', paxAdults: 2, paxChildren: 0, paxInfants: 0, status: 'CONFIRMED', note: 'Anniversary celebration' },
    { id: 'res-004', date: '20.01.2025', sourceAgency: 'AZURO', agency: 'Sunrise Travel', passenger: 'Sarah Davis', hotel: 'Fethiye Beach Resort', stars: 4, destination: 'Fethiye', checkIn: '2025-01-20', checkOut: '2025-01-27', nights: 7, room: 'Family Room', board: 'All Inclusive', paxAdults: 2, paxChildren: 3, paxInfants: 0, status: 'CONFIRMED', note: '' },
    { id: 'res-005', date: '17.01.2025', sourceAgency: 'THV', agency: 'Dream Holidays', passenger: 'David Wilson', hotel: 'Marmaris Bay Hotel', stars: 3, destination: 'Marmaris', checkIn: '2025-01-17', checkOut: '2025-01-24', nights: 7, room: 'Standard', board: 'Full Board', paxAdults: 2, paxChildren: 0, paxInfants: 0, status: 'CANCELLED', note: 'Customer cancelled' },
    { id: 'res-006', date: '19.01.2025', sourceAgency: 'EURO TOURS', agency: 'Paradise Tours', passenger: 'Lisa Anderson', hotel: 'Kaş Boutique Hotel', stars: 4, destination: 'Kaş', checkIn: '2025-01-19', checkOut: '2025-01-23', nights: 4, room: 'Deluxe', board: 'All Inclusive', paxAdults: 2, paxChildren: 1, paxInfants: 0, status: 'CONFIRMED', note: 'Honeymoon package' },
    { id: 'res-007', date: '21.01.2025', sourceAgency: 'SELECT HOLIDAYS', agency: 'Ocean View Travel', passenger: 'Robert Taylor', hotel: 'Çeşme Grand Resort', stars: 5, destination: 'Çeşme', checkIn: '2025-01-21', checkOut: '2025-01-28', nights: 7, room: 'Superior', board: 'Half Board', paxAdults: 2, paxChildren: 0, paxInfants: 0, status: 'OPTION', note: 'Waiting for confirmation' },
    { id: 'res-008', date: '16.01.2025', sourceAgency: 'AZURO', agency: 'Sunny Days Tours', passenger: 'Jennifer Martinez', hotel: 'Alanya Beach Club', stars: 4, destination: 'Alanya', checkIn: '2025-01-16', checkOut: '2025-01-30', nights: 14, room: 'Standard', board: 'All Inclusive', paxAdults: 2, paxChildren: 3, paxInfants: 1, status: 'CONFIRMED', note: 'Large family group' },
    { id: 'res-009', date: '22.01.2025', sourceAgency: 'THV', agency: 'Crystal Travel', passenger: 'William Garcia', hotel: 'Kuşadası Premium Hotel', stars: 5, destination: 'Kuşadası', checkIn: '2025-01-22', checkOut: '2025-01-26', nights: 4, room: 'Suite', board: 'Breakfast', paxAdults: 2, paxChildren: 0, paxInfants: 0, status: 'CONFIRMED', note: 'VIP treatment requested' },
    { id: 'res-010', date: '18.01.2025', sourceAgency: 'EURO TOURS', agency: 'Elite Holidays', passenger: 'Mary Rodriguez', hotel: 'Side Star Resort', stars: 4, destination: 'Side', checkIn: '2025-01-18', checkOut: '2025-01-25', nights: 7, room: 'Deluxe', board: 'Full Board', paxAdults: 2, paxChildren: 2, paxInfants: 0, status: 'OPTION', note: 'Price negotiation pending' },
    { id: 'res-011', date: '20.01.2025', sourceAgency: 'SELECT HOLIDAYS', agency: 'Adventure Travel', passenger: 'James Lee', hotel: 'Kalkan View Hotel', stars: 3, destination: 'Kalkan', checkIn: '2025-01-20', checkOut: '2025-01-24', nights: 4, room: 'Standard', board: 'Half Board', paxAdults: 2, paxChildren: 0, paxInfants: 0, status: 'CONFIRMED', note: '' },
    { id: 'res-012', date: '23.01.2025', sourceAgency: 'AZURO', agency: 'Royal Tours', passenger: 'Patricia White', hotel: 'Göcek Luxury Resort', stars: 5, destination: 'Göcek', checkIn: '2025-01-23', checkOut: '2025-01-30', nights: 7, room: 'Villa', board: 'All Inclusive', paxAdults: 4, paxChildren: 3, paxInfants: 1, status: 'CONFIRMED', note: 'Corporate group booking' },
    { id: 'res-013', date: '17.01.2025', sourceAgency: 'THV', agency: 'Magic Travel', passenger: 'Christopher Harris', hotel: 'Belek Golf Resort', stars: 5, destination: 'Belek', checkIn: '2025-01-17', checkOut: '2025-01-21', nights: 4, room: 'Superior', board: 'All Inclusive', paxAdults: 2, paxChildren: 1, paxInfants: 0, status: 'CANCELLED', note: 'Medical reasons' },
    { id: 'res-014', date: '19.01.2025', sourceAgency: 'EURO TOURS', agency: 'Horizon Tours', passenger: 'Barbara Martin', hotel: 'Didim Sunset Hotel', stars: 4, destination: 'Didim', checkIn: '2025-01-19', checkOut: '2025-01-26', nights: 7, room: 'Deluxe', board: 'Full Board', paxAdults: 2, paxChildren: 0, paxInfants: 0, status: 'CONFIRMED', note: 'Wheelchair accessible room' },
    { id: 'res-015', date: '24.01.2025', sourceAgency: 'SELECT HOLIDAYS', agency: 'Prestige Travel', passenger: 'Daniel Thompson', hotel: 'Kemer Marina Resort', stars: 5, destination: 'Kemer', checkIn: '2025-01-24', checkOut: '2025-01-31', nights: 7, room: 'Suite', board: 'All Inclusive', paxAdults: 2, paxChildren: 0, paxInfants: 0, status: 'OPTION', note: 'Payment pending' },
    { id: 'res-016', date: '21.01.2025', sourceAgency: 'AZURO', agency: 'Pearl Holidays', passenger: 'Nancy Martinez', hotel: 'Ölüdeniz Beach Hotel', stars: 4, destination: 'Ölüdeniz', checkIn: '2025-01-21', checkOut: '2025-01-28', nights: 7, room: 'Family Room', board: 'Half Board', paxAdults: 2, paxChildren: 3, paxInfants: 0, status: 'CONFIRMED', note: 'Kids club required' },
    { id: 'res-017', date: '18.01.2025', sourceAgency: 'THV', agency: 'Diamond Tours', passenger: 'Paul Jackson', hotel: 'Dalyan Riverside Hotel', stars: 3, destination: 'Dalyan', checkIn: '2025-01-18', checkOut: '2025-01-22', nights: 4, room: 'Standard', board: 'Breakfast', paxAdults: 2, paxChildren: 0, paxInfants: 0, status: 'CONFIRMED', note: '' },
    { id: 'res-018', date: '25.01.2025', sourceAgency: 'EURO TOURS', agency: 'Sapphire Travel', passenger: 'Karen White', hotel: 'Turgutreis Spa Resort', stars: 5, destination: 'Turgutreis', checkIn: '2025-01-25', checkOut: '2025-02-01', nights: 7, room: 'Deluxe', board: 'All Inclusive', paxAdults: 2, paxChildren: 2, paxInfants: 0, status: 'CONFIRMED', note: 'Spa package included' },
    { id: 'res-019', date: '20.01.2025', sourceAgency: 'SELECT HOLIDAYS', agency: 'Emerald Tours', passenger: 'Mark Lewis', hotel: 'Çıralı Eco Resort', stars: 4, destination: 'Çıralı', checkIn: '2025-01-20', checkOut: '2025-01-27', nights: 7, room: 'Superior', board: 'Full Board', paxAdults: 2, paxChildren: 1, paxInfants: 0, status: 'OPTION', note: 'Upgrade consideration' },
    { id: 'res-020', date: '22.01.2025', sourceAgency: 'AZURO', agency: 'Ruby Holidays', passenger: 'Betty Walker', hotel: 'Patara Beach Villa', stars: 5, destination: 'Patara', checkIn: '2025-01-22', checkOut: '2025-01-29', nights: 7, room: 'Villa', board: 'All Inclusive', paxAdults: 3, paxChildren: 2, paxInfants: 1, status: 'CONFIRMED', note: 'Beach front villa' },
  ];

  // Get unique destinations for filter
  const uniqueDestinations = [...new Set(allReservations.map(r => r.destination))];

  // Filter reservations based on search, status, destination, agency, and date range
  const filteredReservations = allReservations.filter(reservation => {
    // Search filter
    const searchLower = searchQuery.toLowerCase();
    const matchesSearch = !searchQuery || 
      reservation.passenger.toLowerCase().includes(searchLower) ||
      reservation.agency.toLowerCase().includes(searchLower) ||
      reservation.hotel.toLowerCase().includes(searchLower) ||
      reservation.destination.toLowerCase().includes(searchLower) ||
      reservation.sourceAgency.toLowerCase().includes(searchLower) ||
      reservation.note.toLowerCase().includes(searchLower);

    // Status filter
    const matchesStatus = statusFilter === 'ALL' || reservation.status === statusFilter;

    // Destination filter
    const matchesDestination = destinationFilter === 'ALL' || reservation.destination === destinationFilter;

    // Source Agency filter
    const matchesAgency = agencyFilter === 'ALL' || reservation.sourceAgency === agencyFilter;

    // Date range filter - using applied dates
    const reservationCheckIn = new Date(reservation.checkIn);
    const start = appliedStartDate ? new Date(appliedStartDate) : null;
    const end = appliedEndDate ? new Date(appliedEndDate) : null;
    const matchesDateRange = (!start || reservationCheckIn >= start) && (!end || reservationCheckIn <= end);

    return matchesSearch && matchesStatus && matchesDestination && matchesAgency && matchesDateRange;
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

  const handleApplyFilters = () => {
    setAppliedStartDate(startDate);
    setAppliedEndDate(endDate);
  };

  const handleClearFilters = () => {
    setSearchQuery('');
    setStatusFilter('ALL');
    setDestinationFilter('ALL');
    setAgencyFilter('ALL');
    setStartDate('');
    setEndDate('');
    setAppliedStartDate('');
    setAppliedEndDate('');
  };

  const handleReservationClick = (reservationId) => {
    setSelectedReservationId(reservationId);
    setShowJourneyTimeline(true);
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
            <span className="text-sm bg-slate-600 px-4 py-2 rounded-lg">
              {filteredReservations.length} Rezervasyon
            </span>
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

        {/* Filters Section */}
        <div className="bg-white px-8 py-5 border-b border-slate-200">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-6 gap-4">
            {/* Search */}
            <div className="lg:col-span-2">
              <label className="block text-sm font-medium text-slate-700 mb-2">
                <Search className="w-4 h-4 inline mr-2" />
                Arama
              </label>
              <input
                type="text"
                placeholder="Yolcu, acente, otel, destinasyon..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full px-4 py-2.5 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-cyan-500 text-base"
              />
            </div>

            {/* Date Range */}
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-2">
                <CalendarIcon className="w-4 h-4 inline mr-2" />
                Giriş Tarihi
              </label>
              <input
                type="date"
                value={startDate}
                onChange={(e) => setStartDate(e.target.value)}
                className="w-full px-4 py-2.5 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-cyan-500 text-base"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-slate-700 mb-2">
                <CalendarIcon className="w-4 h-4 inline mr-2" />
                Çıkış Tarihi
              </label>
              <input
                type="date"
                value={endDate}
                onChange={(e) => setEndDate(e.target.value)}
                min={startDate}
                className="w-full px-4 py-2.5 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-cyan-500 text-base"
              />
            </div>

            {/* Status Filter */}
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-2">
                <Filter className="w-4 h-4 inline mr-2" />
                Durum
              </label>
              <select
                value={statusFilter}
                onChange={(e) => setStatusFilter(e.target.value)}
                className="w-full px-4 py-2.5 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-cyan-500 text-base bg-white"
              >
                <option value="ALL">Tümü</option>
                <option value="CONFIRMED">Onaylı</option>
                <option value="OPTION">Opsiyon</option>
                <option value="CANCELLED">İptal</option>
              </select>
            </div>

            {/* Source Agency Filter */}
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-2">
                <Filter className="w-4 h-4 inline mr-2" />
                Kaynak Acenta
              </label>
              <select
                value={agencyFilter}
                onChange={(e) => setAgencyFilter(e.target.value)}
                className="w-full px-4 py-2.5 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-cyan-500 text-base bg-white"
              >
                <option value="ALL">Tüm Acentalar</option>
                {sourceAgencies.map(agency => (
                  <option key={agency} value={agency}>{agency}</option>
                ))}
              </select>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-4">
            {/* Destination Filter */}
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-2">
                Destinasyon
              </label>
              <select
                value={destinationFilter}
                onChange={(e) => setDestinationFilter(e.target.value)}
                className="w-full px-4 py-2.5 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-cyan-500 text-base bg-white"
              >
                <option value="ALL">Tüm Destinasyonlar</option>
                {uniqueDestinations.map(dest => (
                  <option key={dest} value={dest}>{dest}</option>
                ))}
              </select>
            </div>

            {/* Action Buttons */}
            <div className="flex items-end gap-3 md:col-span-2">
              <button
                onClick={handleApplyFilters}
                className="px-6 py-2.5 bg-gradient-to-r from-cyan-500 to-teal-500 hover:from-cyan-600 hover:to-teal-600 text-white rounded-lg transition-all text-base font-medium shadow-md"
              >
                Filtre Uygula
              </button>
              <button
                onClick={handleClearFilters}
                className="px-6 py-2.5 bg-slate-200 hover:bg-slate-300 text-slate-700 rounded-lg transition-colors text-base font-medium"
              >
                Filtreleri Temizle
              </button>
            </div>
          </div>
        </div>

        {/* Table Container */}
        <div className="flex-1 overflow-auto bg-white m-4 rounded-xl shadow-inner">
          <table className="w-full">
            <thead className="sticky top-0 bg-gradient-to-r from-cyan-600 to-teal-600 text-white shadow-md z-10">
              <tr>
                <th className="px-3 py-4 text-left text-base font-semibold">Tarih</th>
                <th className="px-3 py-4 text-left text-base font-semibold">Kaynak Acenta</th>
                <th className="px-3 py-4 text-left text-base font-semibold">Acente</th>
                <th className="px-3 py-4 text-left text-base font-semibold">Yolcu</th>
                <th className="px-3 py-4 text-left text-base font-semibold">Otel</th>
                <th className="px-3 py-4 text-center text-base font-semibold">⭐</th>
                <th className="px-3 py-4 text-left text-base font-semibold">Destinasyon</th>
                <th className="px-3 py-4 text-left text-base font-semibold">Giriş</th>
                <th className="px-3 py-4 text-left text-base font-semibold">Çıkış</th>
                <th className="px-3 py-4 text-center text-base font-semibold">Gece</th>
                <th className="px-3 py-4 text-left text-base font-semibold">Oda</th>
                <th className="px-3 py-4 text-left text-base font-semibold">Pansiyon</th>
                <th className="px-3 py-4 text-center text-base font-semibold">Kişi</th>
                <th className="px-3 py-4 text-center text-base font-semibold">Durum</th>
                <th className="px-3 py-4 text-left text-base font-semibold">Not</th>
              </tr>
            </thead>
            <tbody>
              {filteredReservations.length === 0 ? (
                <tr>
                  <td colSpan="15" className="px-4 py-12 text-center text-slate-500 text-lg">
                    Filtrelere uygun rezervasyon bulunamadı
                  </td>
                </tr>
              ) : (
                filteredReservations.map((reservation, index) => (
                  <tr 
                    key={index}
                    onClick={() => handleReservationClick(reservation.id)}
                    className={`border-b border-slate-200 hover:bg-cyan-100 transition-colors cursor-pointer ${
                      index % 2 === 0 ? 'bg-white' : 'bg-slate-50'
                    }`}
                    title="Yolcu yolculuğunu görüntülemek için tıklayın"
                  >
                    <td className="px-3 py-4 text-base font-semibold text-slate-700">{reservation.date}</td>
                    <td className="px-3 py-4">
                      <span className={`px-3 py-1.5 rounded-full text-sm font-bold ${getAgencyBadgeColor(reservation.sourceAgency)}`}>
                        {reservation.sourceAgency}
                      </span>
                    </td>
                    <td className="px-3 py-4 text-base text-slate-700">{reservation.agency}</td>
                    <td className="px-3 py-4 text-base font-medium text-slate-800">{reservation.passenger}</td>
                    <td className="px-3 py-4 text-base text-slate-700">{reservation.hotel}</td>
                    <td className="px-3 py-4 text-center text-lg">{renderStars(reservation.stars)}</td>
                    <td className="px-3 py-4 text-base font-medium text-cyan-700">{reservation.destination}</td>
                    <td className="px-3 py-4 text-base text-slate-600">{formatDate(reservation.checkIn)}</td>
                    <td className="px-3 py-4 text-base text-slate-600">{formatDate(reservation.checkOut)}</td>
                    <td className="px-3 py-4 text-base text-center font-semibold text-slate-700">{reservation.nights}</td>
                    <td className="px-3 py-4 text-base text-slate-600">{reservation.room}</td>
                    <td className="px-3 py-4 text-base text-slate-600">{reservation.board}</td>
                    <td 
                      className="px-3 py-4 text-center cursor-help"
                      title={`${reservation.paxAdults} Yetişkin, ${reservation.paxChildren} Çocuk, ${reservation.paxInfants} Bebek`}
                      onClick={(e) => {
                        e.stopPropagation();
                        setSelectedPax(reservation);
                      }}
                    >
                      <div className="text-base font-semibold text-slate-700">
                        {getTotalPax(reservation.paxAdults, reservation.paxChildren, reservation.paxInfants)}
                      </div>
                      <div className="text-xs text-slate-500 mt-1">
                        {formatPax(reservation.paxAdults, reservation.paxChildren, reservation.paxInfants)}
                      </div>
                    </td>
                    <td className="px-3 py-4 text-center">
                      <span className={`px-3 py-1.5 rounded-full text-sm font-bold ${getStatusBadge(reservation.status)}`}>
                        {reservation.status === 'CONFIRMED' ? 'ONAYLI' : reservation.status === 'OPTION' ? 'OPSİYON' : 'İPTAL'}
                      </span>
                    </td>
                    <td className="px-3 py-4 text-base text-slate-500 italic">{reservation.note || '-'}</td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Pax Detail Modal */}
      {selectedPax && (
        <div 
          className="fixed inset-0 z-50 flex items-center justify-center p-4"
          style={{ backgroundColor: 'rgba(0, 0, 0, 0.5)' }}
          onClick={() => setSelectedPax(null)}
        >
          <div 
            className="bg-white rounded-xl shadow-2xl p-6 max-w-md"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-xl font-bold text-slate-800">Kişi Detayları</h3>
              <button
                onClick={() => setSelectedPax(null)}
                className="text-slate-400 hover:text-slate-600"
              >
                <X className="w-6 h-6" />
              </button>
            </div>
            
            <div className="space-y-3">
              <div className="flex justify-between items-center p-3 bg-blue-50 rounded-lg">
                <span className="text-slate-700 font-medium">Yetişkin:</span>
                <span className="text-lg font-bold text-blue-700">{selectedPax.paxAdults}</span>
              </div>
              <div className="flex justify-between items-center p-3 bg-green-50 rounded-lg">
                <span className="text-slate-700 font-medium">Çocuk:</span>
                <span className="text-lg font-bold text-green-700">{selectedPax.paxChildren}</span>
              </div>
              <div className="flex justify-between items-center p-3 bg-purple-50 rounded-lg">
                <span className="text-slate-700 font-medium">Bebek:</span>
                <span className="text-lg font-bold text-purple-700">{selectedPax.paxInfants}</span>
              </div>
              <div className="flex justify-between items-center p-3 bg-slate-100 rounded-lg border-2 border-slate-300">
                <span className="text-slate-800 font-bold">Toplam:</span>
                <span className="text-xl font-bold text-slate-900">
                  {getTotalPax(selectedPax.paxAdults, selectedPax.paxChildren, selectedPax.paxInfants)}
                </span>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Journey Timeline Modal */}
      <JourneyTimeline 
        reservationId={selectedReservationId}
        isOpen={showJourneyTimeline}
        onClose={() => {
          setShowJourneyTimeline(false);
          setSelectedReservationId(null);
        }}
      />
    </div>
  );
};

export default ReservationMonitor;
