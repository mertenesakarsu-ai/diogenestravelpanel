import React, { useState, useEffect } from "react";
import { Calendar, Users, MapPin, Bus, Clock, Hotel, FileText, Filter, ArrowRight, ChevronDown, Info, CheckCircle2, Ticket, Plane, Search, X } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import api from "@/utils/api";
import { useAuth } from "@/context/AuthContext";
import FlightDetailModal from "@/components/FlightDetailModal";

const Operations = () => {
  const [selectedDate, setSelectedDate] = useState(new Date().toISOString().split('T')[0]);
  const [startDate, setStartDate] = useState("");
  const [endDate, setEndDate] = useState("");
  const [appliedStartDate, setAppliedStartDate] = useState("");
  const [appliedEndDate, setAppliedEndDate] = useState("");
  const [filterType, setFilterType] = useState("all"); // all, arrival, departure
  const [searchQuery, setSearchQuery] = useState("");
  const [appliedSearchQuery, setAppliedSearchQuery] = useState("");
  const [operations, setOperations] = useState([]);
  const [loading, setLoading] = useState(false);
  const [expandedOperation, setExpandedOperation] = useState(null);
  const [flightDetailModal, setFlightDetailModal] = useState({ isOpen: false, flightCode: null, airportCode: "IST" });

  useEffect(() => {
    fetchOperations();
  }, [selectedDate, filterType, appliedStartDate, appliedEndDate, appliedSearchQuery]);

  const applyFilters = () => {
    setAppliedStartDate(startDate);
    setAppliedEndDate(endDate);
    setAppliedSearchQuery(searchQuery);
  };

  const clearFilters = () => {
    setStartDate("");
    setEndDate("");
    setAppliedStartDate("");
    setAppliedEndDate("");
    setSearchQuery("");
    setAppliedSearchQuery("");
    setSelectedDate(new Date().toISOString().split('T')[0]);
    setFilterType("all");
  };

  const fetchOperations = async () => {
    setLoading(true);
    try {
      const params = { type: filterType };
      
      // Eğer tarih aralığı uygulandıysa onu kullan, yoksa tek tarih kullan
      if (appliedStartDate && appliedEndDate) {
        params.start_date = appliedStartDate;
        params.end_date = appliedEndDate;
      } else {
        params.date = selectedDate;
      }
      
      const response = await api.get('/api/operations', { params });
      
      // If API returns empty data, use mock data for development
      if (!response.data || response.data.length === 0) {
        console.log("No operations from API, using mock data for development");
        // Mock data for development - Comprehensive operation data
        setOperations([
        {
          id: 0,
          voucherNo: "TK-TEST-2412",
          reservationId: "res-test-001",
          arrivalFlight: {
            flightCode: "TK2412",
            date: "2025-11-19",
            time: "12:20",
            from: "IST",
            to: "AYT",
            airline: "Turkish Airlines"
          },
          returnFlight: {
            flightCode: "TK2413",
            date: "2025-11-26",
            time: "14:45",
            from: "AYT",
            to: "IST",
            airline: "Turkish Airlines"
          },
          currentHotel: "Lara Beach Hotel",
          hotelCheckIn: "2025-11-19 15:00",
          hotelCheckOut: "2025-11-26 12:00",
          passengers: 2,
          passengerNames: [
            { firstName: "Ahmet", lastName: "Yılmaz" },
            { firstName: "Ayşe", lastName: "Yılmaz" }
          ],
          type: "arrival",
          transferTime: "14:00",
          notes: "GERÇEK UÇUŞ TESTİ - TK2412 şu an havada, API gerçek veri çekiyor",
          status: "in_progress"
        },
        {
          id: 1,
          voucherNo: "THV-2025-001",
          reservationId: "res-001",
          arrivalFlight: {
            flightCode: "OS840",
            date: selectedDate,
            time: "14:30",
            from: "VIE",
            to: "AYT",
            airline: "Austrian Airlines"
          },
          returnFlight: {
            flightCode: "OS841",
            date: "2025-01-20",
            time: "16:45",
            from: "AYT",
            to: "VIE",
            airline: "Austrian Airlines"
          },
          currentHotel: "Rixos Premium Belek",
          hotelCheckIn: selectedDate + " 15:00",
          hotelCheckOut: "2025-01-20 12:00",
          passengers: 4,
          passengerNames: [
            { firstName: "Mehmet", lastName: "Demir" },
            { firstName: "Fatma", lastName: "Demir" },
            { firstName: "Can", lastName: "Demir" },
            { firstName: "Zeynep", lastName: "Demir" }
          ],
          type: "arrival",
          transferTime: "16:00",
          notes: "Grup transferi, lüks araç gerekli",
          status: "scheduled"
        },
        {
          id: 2,
          voucherNo: "EUR-2025-142",
          reservationId: "res-002",
          arrivalFlight: {
            flightCode: "TK1990",
            date: selectedDate,
            time: "08:45",
            from: "IST",
            to: "AYT",
            airline: "Turkish Airlines"
          },
          transferFlight: {
            flightCode: "TK1991",
            date: selectedDate,
            time: "12:30",
            from: "AYT",
            to: "DLM",
            airline: "Turkish Airlines"
          },
          returnFlight: {
            flightCode: "TK1992",
            date: "2025-01-18",
            time: "18:15",
            from: "DLM",
            to: "IST",
            airline: "Turkish Airlines"
          },
          currentHotel: "Granada Luxury Resort - Kemer",
          hotelCheckIn: selectedDate + " 10:00",
          hotelCheckOut: "2025-01-18 17:00",
          passengers: 2,
          passengerNames: [
            { firstName: "Hans", lastName: "Schmidt" },
            { firstName: "Anna", lastName: "Schmidt" }
          ],
          type: "arrival",
          transferTime: "06:00",
          notes: "Aktarmalı uçuş, Dalaman'dan otele transfer",
          status: "in_progress"
        },
        {
          id: 3,
          voucherNo: "SEL-2025-078",
          reservationId: "res-003",
          arrivalFlight: {
            flightCode: "XQ105",
            date: "2025-01-10",
            time: "18:15",
            from: "DUS",
            to: "AYT",
            airline: "SunExpress"
          },
          returnFlight: {
            flightCode: "XQ106",
            date: "2025-01-25",
            time: "21:30",
            from: "AYT",
            to: "DUS",
            airline: "SunExpress"
          },
          currentHotel: "Club Hotel Falcon - Antalya",
          hotelCheckIn: "2025-01-10 19:45",
          hotelCheckOut: "2025-01-25 19:00",
          passengers: 6,
          passengerNames: [
            { firstName: "Michael", lastName: "Müller" },
            { firstName: "Sarah", lastName: "Müller" },
            { firstName: "Emma", lastName: "Müller" },
            { firstName: "Sophie", lastName: "Müller" },
            { firstName: "Max", lastName: "Müller" },
            { firstName: "Lena", lastName: "Müller" }
          ],
          type: "departure",
          transferTime: "19:45",
          notes: "2 otobüs gerekli, büyük aile",
          status: "completed"
        },
        {
          id: 4,
          voucherNo: "PEG-2025-456",
          reservationId: "res-004",
          arrivalFlight: {
            flightCode: "PC2012",
            date: selectedDate,
            time: "16:50",
            from: "SAW",
            to: "AYT",
            airline: "Pegasus Airlines"
          },
          returnFlight: {
            flightCode: "PC2013",
            date: "2025-01-22",
            time: "19:15",
            from: "AYT",
            to: "SAW",
            airline: "Pegasus Airlines"
          },
          currentHotel: "Delphin Imperial Hotel - Lara",
          hotelCheckIn: selectedDate + " 18:30",
          hotelCheckOut: "2025-01-22 17:00",
          passengers: 3,
          passengerNames: [
            { firstName: "Elif", lastName: "Kaya" },
            { firstName: "Burak", lastName: "Kaya" },
            { firstName: "Deniz", lastName: "Kaya" }
          ],
          type: "arrival",
          transferTime: "18:00",
          notes: "Sabiha Gökçen'den geliş, ailece tatil",
          status: "scheduled"
        }
        ]);
      } else {
        setOperations(response.data);
      }
    } catch (error) {
      console.error("Error fetching operations:", error);
      setOperations([]);
    } finally {
      setLoading(false);
    }
  };

  // Client-side search filtering
  const filteredOperations = operations.filter(operation => {
    if (!appliedSearchQuery) return true;
    
    const query = appliedSearchQuery.toLowerCase();
    return (
      (operation.voucherNo && operation.voucherNo.toLowerCase().includes(query)) ||
      (operation.currentHotel && operation.currentHotel.toLowerCase().includes(query)) ||
      (operation.hotel && operation.hotel.toLowerCase().includes(query)) ||
      (operation.arrivalFlight?.flightCode && operation.arrivalFlight.flightCode.toLowerCase().includes(query)) ||
      (operation.returnFlight?.flightCode && operation.returnFlight.flightCode.toLowerCase().includes(query)) ||
      (operation.transferFlight?.flightCode && operation.transferFlight.flightCode.toLowerCase().includes(query)) ||
      (operation.notes && operation.notes.toLowerCase().includes(query))
    );
  });

  // Check if flight detail button should be active (24 hours before flight)
  const isFlightDetailActive = (flightDate, flightTime) => {
    if (!flightDate || !flightTime) return false;
    
    try {
      const flightDateTime = new Date(`${flightDate}T${flightTime}`);
      const now = new Date();
      const hoursUntilFlight = (flightDateTime - now) / (1000 * 60 * 60);
      
      // Active if flight is within 24 hours (before or after)
      return hoursUntilFlight <= 24 && hoursUntilFlight >= -6;
    } catch (e) {
      return false;
    }
  };

  // Calculate hotel status
  const getHotelStatus = (checkIn, checkOut) => {
    if (!checkIn || !checkOut) return { status: 'unknown', text: 'Bilgi yok', color: 'text-slate-500' };
    
    try {
      const now = new Date();
      const checkInDate = new Date(checkIn);
      const checkOutDate = new Date(checkOut);
      
      if (now < checkInDate) {
        return { status: 'not_checked_in', text: 'Henüz giriş yapmadı', color: 'text-orange-600' };
      } else if (now >= checkInDate && now < checkOutDate) {
        const daysRemaining = Math.ceil((checkOutDate - now) / (1000 * 60 * 60 * 24));
        return { 
          status: 'at_hotel', 
          text: `Otelde (${daysRemaining} gün kaldı)`, 
          color: 'text-green-600',
          daysRemaining 
        };
      } else {
        return { status: 'checked_out', text: 'Çıkış yaptı', color: 'text-slate-500' };
      }
    } catch (e) {
      return { status: 'unknown', text: 'Bilgi yok', color: 'text-slate-500' };
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'completed': return 'bg-green-100 text-green-800';
      case 'in_progress': return 'bg-blue-100 text-blue-800';
      case 'scheduled': return 'bg-orange-100 text-orange-800';
      default: return 'bg-slate-100 text-slate-800';
    }
  };

  const getStatusText = (status) => {
    switch (status) {
      case 'completed': return 'Tamamlandı';
      case 'in_progress': return 'Devam Ediyor';
      case 'scheduled': return 'Planlandı';
      default: return 'Bilinmiyor';
    }
  };

  const formatDateTime = (dateTimeStr) => {
    if (!dateTimeStr) return '';
    try {
      const date = new Date(dateTimeStr);
      const day = String(date.getDate()).padStart(2, '0');
      const month = String(date.getMonth() + 1).padStart(2, '0');
      const year = date.getFullYear();
      const hours = String(date.getHours()).padStart(2, '0');
      const minutes = String(date.getMinutes()).padStart(2, '0');
      return `${day}.${month}.${year} ${hours}:${minutes}`;
    } catch (e) {
      return dateTimeStr;
    }
  };

  const formatDate = (dateString) => {
    if (!dateString) return '';
    try {
      const date = new Date(dateString);
      const day = String(date.getDate()).padStart(2, '0');
      const month = String(date.getMonth() + 1).padStart(2, '0');
      const year = date.getFullYear();
      return `${day}.${month}.${year}`;
    } catch (e) {
      return dateString;
    }
  };

  const arrivalCount = filteredOperations.filter(op => op.type === 'arrival' || op.arrivalFlight).length;
  const departureCount = filteredOperations.filter(op => op.type === 'departure' || op.returnFlight).length;

  return (
    <div className="space-y-6" data-testid="operations-page">
      {/* Header with Stats */}
      <div className="bg-white rounded-2xl border border-slate-200 shadow-lg p-6">
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center gap-4">
            <div className="w-14 h-14 rounded-xl bg-gradient-to-br from-orange-500 to-red-500 flex items-center justify-center shadow-lg">
              <Bus className="w-7 h-7 text-white" />
            </div>
            <div>
              <h2 className="text-2xl font-bold text-slate-800">Operasyon Departmanı</h2>
              <p className="text-sm text-slate-500">Günlük transfer ve operasyon yönetimi</p>
            </div>
          </div>

          <div className="flex items-center gap-3">
            <div className="text-center px-4 py-2 bg-green-50 rounded-lg">
              <div className="text-2xl font-bold text-green-700">{arrivalCount}</div>
              <div className="text-xs text-green-600">Geliş</div>
            </div>
            <div className="text-center px-4 py-2 bg-orange-50 rounded-lg">
              <div className="text-2xl font-bold text-orange-700">{departureCount}</div>
              <div className="text-xs text-orange-600">Dönüş</div>
            </div>
          </div>
        </div>

        {/* Filters */}
        <div className="space-y-4">
          {/* First Row - Date Filters */}
          <div className="flex flex-wrap gap-4">
            <div className="flex-1 min-w-[180px]">
              <label className="block text-sm font-medium text-slate-700 mb-2">Tek Tarih</label>
              <Input
                type="date"
                value={selectedDate}
                onChange={(e) => setSelectedDate(e.target.value)}
                className="h-10"
                data-testid="date-picker"
                disabled={appliedStartDate && appliedEndDate}
              />
            </div>

            <div className="flex-1 min-w-[180px]">
              <label className="block text-sm font-medium text-slate-700 mb-2">Başlangıç Tarihi</label>
              <Input
                type="date"
                value={startDate}
                onChange={(e) => setStartDate(e.target.value)}
                className="h-10"
                placeholder="Başlangıç"
              />
            </div>

            <div className="flex-1 min-w-[180px]">
              <label className="block text-sm font-medium text-slate-700 mb-2">Bitiş Tarihi</label>
              <Input
                type="date"
                value={endDate}
                onChange={(e) => setEndDate(e.target.value)}
                className="h-10"
                placeholder="Bitiş"
                min={startDate}
              />
            </div>

            <div className="flex-1 min-w-[180px]">
              <label className="block text-sm font-medium text-slate-700 mb-2">Filtre Tipi</label>
              <Select value={filterType} onValueChange={setFilterType}>
                <SelectTrigger className="h-10" data-testid="filter-select">
                  <SelectValue placeholder="Tümü" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">Tümü</SelectItem>
                  <SelectItem value="arrival">Sadece Geliş</SelectItem>
                  <SelectItem value="departure">Sadece Dönüş</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>

          {/* Second Row - Search and Actions */}
          <div className="flex flex-wrap gap-4">
            <div className="flex-1 min-w-[300px]">
              <label className="block text-sm font-medium text-slate-700 mb-2">Detaylı Arama</label>
              <Input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Voucher, otel, uçuş kodu veya not ile ara..."
                className="h-10"
              />
            </div>

            <div className="flex items-end gap-2">
              <Button
                onClick={applyFilters}
                disabled={loading}
                className="bg-gradient-to-r from-orange-500 to-red-500 hover:from-orange-600 hover:to-red-600 text-white h-10 px-6"
              >
                <Filter className="w-4 h-4 mr-2" />
                {loading ? "Yükleniyor..." : "Uygula"}
              </Button>
              <Button
                onClick={clearFilters}
                disabled={loading}
                variant="outline"
                className="h-10 px-6"
              >
                Temizle
              </Button>
            </div>
          </div>

          {/* Active Filters Display */}
          {(appliedStartDate || appliedEndDate || appliedSearchQuery) && (
            <div className="flex flex-wrap gap-2 items-center text-sm">
              <span className="text-slate-600 font-medium">Aktif Filtreler:</span>
              {appliedStartDate && appliedEndDate && (
                <span className="px-3 py-1 bg-blue-100 text-blue-700 rounded-full">
                  📅 {appliedStartDate} - {appliedEndDate}
                </span>
              )}
              {appliedSearchQuery && (
                <span className="px-3 py-1 bg-purple-100 text-purple-700 rounded-full">
                  🔍 "{appliedSearchQuery}"
                </span>
              )}
            </div>
          )}
        </div>
      </div>

      {/* Operations List */}
      <div className="space-y-4">
        {filteredOperations.length === 0 ? (
          <div className="bg-white rounded-2xl border border-slate-200 shadow-lg p-12 text-center">
            <Bus className="w-16 h-16 text-slate-300 mx-auto mb-4" />
            <h3 className="text-xl font-bold text-slate-800 mb-2">Operasyon Bulunamadı</h3>
            <p className="text-slate-600">
              {appliedSearchQuery 
                ? `"${appliedSearchQuery}" araması için sonuç bulunamadı.` 
                : "Seçili tarih için henüz operasyon planlanmamış."}
            </p>
          </div>
        ) : (
          filteredOperations.map((operation) => {
            const hotelStatus = getHotelStatus(operation.hotelCheckIn, operation.hotelCheckOut);
            const isArrivalActive = isFlightDetailActive(
              operation.arrivalFlight?.date, 
              operation.arrivalFlight?.time
            );
            const isReturnActive = isFlightDetailActive(
              operation.returnFlight?.date, 
              operation.returnFlight?.time
            );
            const isTransferActive = isFlightDetailActive(
              operation.transferFlight?.date, 
              operation.transferFlight?.time
            );

            return (
              <div
                key={operation.id}
                className="bg-white rounded-xl border border-slate-200 shadow-md hover:shadow-lg transition-all overflow-hidden"
              >
                {/* Operation Header */}
                <div
                  className="p-6 cursor-pointer"
                  onClick={() => setExpandedOperation(expandedOperation === operation.id ? null : operation.id)}
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-6 flex-1">
                      {/* Voucher & Flight Info */}
                      <div className="flex items-center gap-3">
                        <div className={`w-12 h-12 rounded-lg flex items-center justify-center ${
                          operation.type === 'arrival' ? 'bg-green-100' : 'bg-orange-100'
                        }`}>
                          <Ticket className={`w-6 h-6 ${
                            operation.type === 'arrival' ? 'text-green-600' : 'text-orange-600'
                          }`} />
                        </div>
                        <div>
                          <div className="flex items-center gap-2">
                            <span className="text-lg font-bold text-slate-800">{operation.voucherNo || 'N/A'}</span>
                          </div>
                          <div className="text-sm text-slate-600 mt-1">
                            {/* Uçak Kodları - Geliş, Transfer (varsa), Dönüş */}
                            <span className="font-semibold">
                              {operation.arrivalFlight?.flightCode}
                              {operation.transferFlight && ` - ${operation.transferFlight.flightCode}`}
                              {operation.returnFlight && ` - ${operation.returnFlight.flightCode}`}
                            </span>
                          </div>
                        </div>
                      </div>

                      {/* Geliş Tarihi ve Saati */}
                      {operation.arrivalFlight && (
                        <div>
                          <div className="text-xs text-slate-500 mb-1">Geliş</div>
                          <div className="font-semibold text-green-700 text-sm">
                            {formatDate(operation.arrivalFlight.date)} {operation.arrivalFlight.time}
                          </div>
                        </div>
                      )}

                      {/* Gidiş Tarihi ve Saati */}
                      {operation.returnFlight && (
                        <div>
                          <div className="text-xs text-slate-500 mb-1">Gidiş</div>
                          <div className="font-semibold text-orange-700 text-sm">
                            {formatDate(operation.returnFlight.date)} {operation.returnFlight.time}
                          </div>
                        </div>
                      )}

                      {/* Current Hotel */}
                      <div>
                        <div className="text-xs text-slate-500 mb-1">Otel</div>
                        <div className="font-semibold text-slate-800 text-sm">
                          {operation.currentHotel || operation.hotel || 'Belirtilmemiş'}
                        </div>
                      </div>

                      {/* Passengers */}
                      <div>
                        <div className="text-xs text-slate-500 mb-1">Yolcu Sayısı</div>
                        <div className="flex items-center gap-2">
                          <Users className="w-4 h-4 text-slate-400" />
                          <span className="font-semibold text-slate-800">{operation.passengers}</span>
                        </div>
                      </div>
                    </div>

                    {/* Status & Expand */}
                    <div className="flex items-center gap-3">
                      <span className={`px-3 py-1 rounded-full text-xs font-medium ${getStatusColor(operation.status)}`}>
                        {getStatusText(operation.status)}
                      </span>
                      <ChevronDown className={`w-5 h-5 text-slate-400 transition-transform ${
                        expandedOperation === operation.id ? 'rotate-180' : ''
                      }`} />
                    </div>
                  </div>
                </div>

                {/* Expanded Details */}
                {expandedOperation === operation.id && (
                  <div className="border-t border-slate-200 bg-slate-50 p-6">
                    <div className="space-y-6">
                      {/* Yolcu Bilgileri */}
                      <div>
                        <h4 className="text-sm font-bold text-slate-800 mb-3 flex items-center gap-2">
                          <Users className="w-4 h-4 text-blue-600" />
                          Yolcu Bilgileri
                        </h4>
                        <div className="space-y-4">
                          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                            <div className="bg-white p-3 rounded-lg border border-slate-200">
                              <div className="text-xs text-slate-500">Voucher No</div>
                              <div className="font-semibold text-slate-800">{operation.voucherNo || 'N/A'}</div>
                            </div>
                            <div className="bg-white p-3 rounded-lg border border-slate-200">
                              <div className="text-xs text-slate-500">Toplam Yolcu</div>
                              <div className="font-semibold text-slate-800">{operation.passengers} kişi</div>
                            </div>
                          </div>
                          
                          {/* Yolcu İsimleri */}
                          {operation.passengerNames && operation.passengerNames.length > 0 && (
                            <div className="bg-white p-4 rounded-lg border border-slate-200">
                              <div className="text-xs text-slate-500 mb-3 font-semibold">Yolcu Listesi</div>
                              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
                                {operation.passengerNames.map((passenger, index) => (
                                  <div key={index} className="flex items-center gap-2 p-2 bg-slate-50 rounded-lg">
                                    <div className="w-8 h-8 rounded-full bg-blue-100 flex items-center justify-center">
                                      <span className="text-blue-600 font-semibold text-sm">{index + 1}</span>
                                    </div>
                                    <div className="flex-1">
                                      <div className="font-semibold text-slate-800 text-sm">
                                        {passenger.firstName} {passenger.lastName}
                                      </div>
                                    </div>
                                  </div>
                                ))}
                              </div>
                            </div>
                          )}
                        </div>
                      </div>

                      {/* Uçuş Bilgileri */}
                      <div>
                        <h4 className="text-sm font-bold text-slate-800 mb-3 flex items-center gap-2">
                          <Plane className="w-4 h-4 text-orange-600" />
                          Uçuş Bilgileri
                        </h4>
                        <div className="space-y-3">
                          {/* Arrival Flight */}
                          {operation.arrivalFlight && (
                            <div className="bg-white p-4 rounded-lg border border-slate-200">
                              <div className="flex items-center justify-between">
                                <div className="flex-1">
                                  <div className="flex items-center gap-2 mb-2">
                                    <span className="px-2 py-1 bg-green-100 text-green-700 rounded text-xs font-medium">
                                      Geliş Uçuşu
                                    </span>
                                    <span className="font-bold text-slate-800">{operation.arrivalFlight.flightCode}</span>
                                  </div>
                                  <div className="grid grid-cols-3 gap-4 text-sm">
                                    <div>
                                      <div className="text-xs text-slate-500">Havayolu</div>
                                      <div className="font-semibold">{operation.arrivalFlight.airline || 'N/A'}</div>
                                    </div>
                                    <div>
                                      <div className="text-xs text-slate-500">Rota</div>
                                      <div className="font-semibold flex items-center gap-1">
                                        {operation.arrivalFlight.from} <ArrowRight className="w-3 h-3" /> {operation.arrivalFlight.to}
                                      </div>
                                    </div>
                                    <div>
                                      <div className="text-xs text-slate-500">Tarih & Saat</div>
                                      <div className="font-semibold">{formatDate(operation.arrivalFlight.date)} {operation.arrivalFlight.time}</div>
                                    </div>
                                  </div>
                                </div>
                                <Button
                                  size="sm"
                                  variant="outline"
                                  disabled={!isArrivalActive}
                                  onClick={() => setFlightDetailModal({ 
                                    isOpen: true, 
                                    flightCode: operation.arrivalFlight.flightCode,
                                    airportCode: operation.arrivalFlight.to
                                  })}
                                  className={!isArrivalActive ? 'opacity-50 cursor-not-allowed' : ''}
                                  title={!isArrivalActive ? 'Uçuş detayı 24 saat öncesinden görüntülenebilir' : 'Uçuş detayını görüntüle'}
                                >
                                  <Info className="w-4 h-4 mr-2" />
                                  Uçuş Detayı
                                </Button>
                              </div>
                            </div>
                          )}

                          {/* Transfer Flight */}
                          {operation.transferFlight && (
                            <div className="bg-white p-4 rounded-lg border border-slate-200">
                              <div className="flex items-center justify-between">
                                <div className="flex-1">
                                  <div className="flex items-center gap-2 mb-2">
                                    <span className="px-2 py-1 bg-blue-100 text-blue-700 rounded text-xs font-medium">
                                      Aktarma Uçuşu
                                    </span>
                                    <span className="font-bold text-slate-800">{operation.transferFlight.flightCode}</span>
                                  </div>
                                  <div className="grid grid-cols-3 gap-4 text-sm">
                                    <div>
                                      <div className="text-xs text-slate-500">Havayolu</div>
                                      <div className="font-semibold">{operation.transferFlight.airline || 'N/A'}</div>
                                    </div>
                                    <div>
                                      <div className="text-xs text-slate-500">Rota</div>
                                      <div className="font-semibold flex items-center gap-1">
                                        {operation.transferFlight.from} <ArrowRight className="w-3 h-3" /> {operation.transferFlight.to}
                                      </div>
                                    </div>
                                    <div>
                                      <div className="text-xs text-slate-500">Tarih & Saat</div>
                                      <div className="font-semibold">{formatDate(operation.transferFlight.date)} {operation.transferFlight.time}</div>
                                    </div>
                                  </div>
                                </div>
                                <Button
                                  size="sm"
                                  variant="outline"
                                  disabled={!isTransferActive}
                                  onClick={() => setFlightDetailModal({ 
                                    isOpen: true, 
                                    flightCode: operation.transferFlight.flightCode,
                                    airportCode: operation.transferFlight.from
                                  })}
                                  className={!isTransferActive ? 'opacity-50 cursor-not-allowed' : ''}
                                  title={!isTransferActive ? 'Uçuş detayı 24 saat öncesinden görüntülenebilir' : 'Uçuş detayını görüntüle'}
                                >
                                  <Info className="w-4 h-4 mr-2" />
                                  Uçuş Detayı
                                </Button>
                              </div>
                            </div>
                          )}

                          {/* Return Flight */}
                          {operation.returnFlight && (
                            <div className="bg-white p-4 rounded-lg border border-slate-200">
                              <div className="flex items-center justify-between">
                                <div className="flex-1">
                                  <div className="flex items-center gap-2 mb-2">
                                    <span className="px-2 py-1 bg-orange-100 text-orange-700 rounded text-xs font-medium">
                                      Dönüş Uçuşu
                                    </span>
                                    <span className="font-bold text-slate-800">{operation.returnFlight.flightCode}</span>
                                  </div>
                                  <div className="grid grid-cols-3 gap-4 text-sm">
                                    <div>
                                      <div className="text-xs text-slate-500">Havayolu</div>
                                      <div className="font-semibold">{operation.returnFlight.airline || 'N/A'}</div>
                                    </div>
                                    <div>
                                      <div className="text-xs text-slate-500">Rota</div>
                                      <div className="font-semibold flex items-center gap-1">
                                        {operation.returnFlight.from} <ArrowRight className="w-3 h-3" /> {operation.returnFlight.to}
                                      </div>
                                    </div>
                                    <div>
                                      <div className="text-xs text-slate-500">Tarih & Saat</div>
                                      <div className="font-semibold">{formatDate(operation.returnFlight.date)} {operation.returnFlight.time}</div>
                                    </div>
                                  </div>
                                </div>
                                <Button
                                  size="sm"
                                  variant="outline"
                                  disabled={!isReturnActive}
                                  onClick={() => setFlightDetailModal({ 
                                    isOpen: true, 
                                    flightCode: operation.returnFlight.flightCode,
                                    airportCode: operation.returnFlight.from
                                  })}
                                  className={!isReturnActive ? 'opacity-50 cursor-not-allowed' : ''}
                                  title={!isReturnActive ? 'Uçuş detayı 24 saat öncesinden görüntülenebilir' : 'Uçuş detayını görüntüle'}
                                >
                                  <Info className="w-4 h-4 mr-2" />
                                  Uçuş Detayı
                                </Button>
                              </div>
                            </div>
                          )}
                        </div>
                      </div>

                      {/* Otel Bilgileri */}
                      <div>
                        <h4 className="text-sm font-bold text-slate-800 mb-3 flex items-center gap-2">
                          <Hotel className="w-4 h-4 text-purple-600" />
                          Otel Bilgileri
                        </h4>
                        <div className="bg-white p-4 rounded-lg border border-slate-200">
                          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                            <div>
                              <div className="text-xs text-slate-500">Otel Adı</div>
                              <div className="font-semibold text-slate-800">{operation.currentHotel || operation.hotel}</div>
                            </div>
                            <div>
                              <div className="text-xs text-slate-500">Giriş Tarihi & Saati</div>
                              <div className="font-semibold text-green-700">
                                {formatDateTime(operation.hotelCheckIn)}
                              </div>
                            </div>
                            <div>
                              <div className="text-xs text-slate-500">Çıkış Tarihi & Saati</div>
                              <div className="font-semibold text-orange-700">
                                {formatDateTime(operation.hotelCheckOut)}
                              </div>
                            </div>
                          </div>
                          <div className="mt-3 pt-3 border-t border-slate-200">
                            <div className="flex items-center gap-2">
                              <CheckCircle2 className={`w-5 h-5 ${hotelStatus.color}`} />
                              <span className={`font-semibold ${hotelStatus.color}`}>
                                {hotelStatus.text}
                              </span>
                            </div>
                          </div>
                        </div>
                      </div>

                      {/* Operasyon Notları */}
                      {operation.notes && (
                        <div>
                          <h4 className="text-sm font-bold text-slate-800 mb-3 flex items-center gap-2">
                            <FileText className="w-4 h-4 text-slate-600" />
                            Operasyon Notları
                          </h4>
                          <div className="bg-white p-4 rounded-lg border border-slate-200">
                            <p className="text-sm text-slate-700">{operation.notes}</p>
                          </div>
                        </div>
                      )}
                    </div>
                  </div>
                )}
              </div>
            );
          })
        )}
      </div>

      {/* Flight Detail Modal */}
      <FlightDetailModal
        isOpen={flightDetailModal.isOpen}
        onClose={() => setFlightDetailModal({ isOpen: false, flightCode: null, airportCode: "IST" })}
        flightCode={flightDetailModal.flightCode}
        airportCode={flightDetailModal.airportCode}
      />
    </div>
  );
};

export default Operations;
