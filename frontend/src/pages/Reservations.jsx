import React, { useState, useEffect } from "react";
import { Search, Filter, Users, Calendar, Hotel, Loader2, RefreshCw } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { useAuth } from "@/context/AuthContext";

const Reservations = () => {
  const { user } = useAuth();
  const [searchTerm, setSearchTerm] = useState("");
  const [dateFrom, setDateFrom] = useState("");
  const [dateTo, setDateTo] = useState("");
  const [reservations, setReservations] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [pagination, setPagination] = useState({
    total: 0,
    limit: 50,
    offset: 0
  });

  // Fetch reservations from DIOGENESSEJOUR database
  const fetchReservations = async () => {
    if (!user?.id) return;
    
    setLoading(true);
    setError(null);
    
    try {
      const backendUrl = import.meta.env.VITE_REACT_APP_BACKEND_URL || process.env.REACT_APP_BACKEND_URL;
      const params = new URLSearchParams({
        limit: pagination.limit.toString(),
        offset: pagination.offset.toString()
      });
      
      if (searchTerm) params.append('search', searchTerm);
      if (dateFrom) params.append('date_from', dateFrom);
      if (dateTo) params.append('date_to', dateTo);
      
      const response = await fetch(`${backendUrl}/diogenes/reservations?${params}`, {
        headers: {
          'x-user-id': user.id
        }
      });
      
      if (!response.ok) {
        throw new Error('Failed to fetch reservations');
      }
      
      const data = await response.json();
      setReservations(data.reservations || []);
      setPagination(prev => ({
        ...prev,
        total: data.total || 0
      }));
    } catch (err) {
      console.error('Error fetching reservations:', err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  // Initial fetch
  useEffect(() => {
    fetchReservations();
  }, [user?.id, pagination.offset]);

  // Apply filters
  const handleApplyFilters = () => {
    setPagination(prev => ({ ...prev, offset: 0 }));
    fetchReservations();
  };

  // Clear filters
  const handleClearFilters = () => {
    setSearchTerm("");
    setDateFrom("");
    setDateTo("");
    setPagination(prev => ({ ...prev, offset: 0 }));
    fetchReservations();
  };

  const filteredReservations = reservations;

  return (
    <div className="space-y-6" data-testid="reservations-page">
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <div className="bg-white rounded-xl p-6 border border-slate-200 shadow-sm">
          <div className="flex items-center gap-4">
            <div className="w-14 h-14 rounded-xl bg-gradient-to-br from-blue-500 to-blue-600 flex items-center justify-center shadow-lg">
              <Calendar className="w-7 h-7 text-white" />
            </div>
            <div>
              <p className="text-sm text-slate-500">Toplam Rezervasyon</p>
              <p className="text-3xl font-bold text-slate-800">{pagination.total}</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-xl p-6 border border-slate-200 shadow-sm">
          <div className="flex items-center gap-4">
            <div className="w-14 h-14 rounded-xl bg-gradient-to-br from-green-500 to-green-600 flex items-center justify-center shadow-lg">
              <Users className="w-7 h-7 text-white" />
            </div>
            <div>
              <p className="text-sm text-slate-500">Gösterilen</p>
              <p className="text-3xl font-bold text-slate-800">
                {reservations.length}
              </p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-xl p-6 border border-slate-200 shadow-sm">
          <div className="flex items-center gap-4">
            <div className="w-14 h-14 rounded-xl bg-gradient-to-br from-orange-500 to-orange-600 flex items-center justify-center shadow-lg">
              <Hotel className="w-7 h-7 text-white" />
            </div>
            <div>
              <p className="text-sm text-slate-500">Sayfa</p>
              <p className="text-3xl font-bold text-slate-800">
                {Math.floor(pagination.offset / pagination.limit) + 1}
              </p>
            </div>
          </div>
        </div>
      </div>

      <div className="bg-white rounded-2xl border border-slate-200 shadow-lg p-6">
        <div className="flex flex-col gap-4 mb-6">
          <div className="flex items-center justify-between">
            <h3 className="text-lg font-bold text-slate-800">Rezervasyon Listesi</h3>
            <Button 
              onClick={fetchReservations}
              variant="outline"
              size="sm"
              disabled={loading}
            >
              <RefreshCw className={`w-4 h-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
              Yenile
            </Button>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-3">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
              <Input
                placeholder="Voucher ara..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10"
                data-testid="reservation-search"
              />
            </div>
            
            <Input
              type="date"
              placeholder="Başlangıç Tarihi"
              value={dateFrom}
              onChange={(e) => setDateFrom(e.target.value)}
              data-testid="date-from"
            />
            
            <Input
              type="date"
              placeholder="Bitiş Tarihi"
              value={dateTo}
              onChange={(e) => setDateTo(e.target.value)}
              data-testid="date-to"
            />
            
            <div className="flex gap-2">
              <Button 
                onClick={handleApplyFilters}
                disabled={loading}
                className="flex-1"
              >
                <Filter className="w-4 h-4 mr-2" />
                Filtrele
              </Button>
              <Button 
                onClick={handleClearFilters}
                variant="outline"
                disabled={loading}
              >
                Temizle
              </Button>
            </div>
          </div>
          
          {error && (
            <div className="bg-red-50 border border-red-200 rounded-lg p-3 text-red-700 text-sm">
              {error}
            </div>
          )}
        </div>

        <div className="overflow-x-auto">
          <table className="w-full" data-testid="reservations-table">
            <thead className="bg-slate-50 border-b border-slate-200">
              <tr>
                <th className="px-6 py-4 text-left text-xs font-semibold text-slate-600 uppercase">Voucher No</th>
                <th className="px-6 py-4 text-left text-xs font-semibold text-slate-600 uppercase">Grup Lideri</th>
                <th className="px-6 py-4 text-left text-xs font-semibold text-slate-600 uppercase">Ürün</th>
                <th className="px-6 py-4 text-left text-xs font-semibold text-slate-600 uppercase">Otel</th>
                <th className="px-6 py-4 text-left text-xs font-semibold text-slate-600 uppercase">Tarihler</th>
                <th className="px-6 py-4 text-left text-xs font-semibold text-slate-600 uppercase">Pax</th>
                <th className="px-6 py-4 text-left text-xs font-semibold text-slate-600 uppercase">Durum</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {filteredReservations.map((reservation) => (
                <tr 
                  key={reservation.id} 
                  className="hover:bg-slate-50 transition-colors"
                  data-testid={`reservation-row-${reservation.id}`}
                >
                  <td className="px-6 py-4">
                    <span className="font-semibold text-slate-800">{reservation.voucherNo}</span>
                  </td>
                  <td className="px-6 py-4">
                    <div>
                      <p className="font-medium text-slate-800">{reservation.leader.name}</p>
                      <p className="text-xs text-slate-500">{reservation.leader.passport}</p>
                    </div>
                  </td>
                  <td className="px-6 py-4">
                    <div>
                      <p className="font-medium text-slate-800">{reservation.product.code}</p>
                      <p className="text-xs text-slate-500">{reservation.product.name}</p>
                    </div>
                  </td>
                  <td className="px-6 py-4 text-slate-700">{reservation.hotel}</td>
                  <td className="px-6 py-4 text-slate-700">
                    {reservation.arrivalDate} - {reservation.departureDate}
                  </td>
                  <td className="px-6 py-4 text-slate-700">{reservation.pax}</td>
                  <td className="px-6 py-4">
                    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                      reservation.status === 'confirmed' ? 'bg-green-100 text-green-800' : 'bg-orange-100 text-orange-800'
                    }`}>
                      {reservation.status === 'confirmed' ? 'Onaylı' : 'Bekleyen'}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default Reservations;