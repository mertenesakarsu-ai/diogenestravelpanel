import React, { useState, useEffect } from "react";
import { Search, Users, Calendar, Plane, Hotel, MapPin, Clock } from "lucide-react";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import api from "@/utils/api";

const Management = () => {
  const [searchQuery, setSearchQuery] = useState("");
  const [searchResults, setSearchResults] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleSearch = async () => {
    if (searchQuery.length < 2) return;
    
    setLoading(true);
    try {
      const response = await api.get(`/api/search?query=${searchQuery}`);
      setSearchResults(response.data);
    } catch (error) {
      console.error("Search error:", error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6" data-testid="management-page">
      {/* Header */}
      <div className="bg-white rounded-2xl border border-slate-200 shadow-lg p-6">
        <div className="flex items-center gap-4 mb-6">
          <div className="w-14 h-14 rounded-xl bg-gradient-to-br from-cyan-500 to-teal-500 flex items-center justify-center shadow-lg">
            <Users className="w-7 h-7 text-white" />
          </div>
          <div>
            <h2 className="text-2xl font-bold text-slate-800">Yönetim Departmanı</h2>
            <p className="text-sm text-slate-500">Tüm sistemlerde yolcu arama ve takip</p>
          </div>
        </div>

        {/* Search Bar */}
        <div className="flex gap-3">
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400" />
            <Input
              placeholder="Yolcu adı, pasaport numarası, voucher no veya PNR ara..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
              className="pl-10 h-12 text-lg"
              data-testid="search-input"
            />
          </div>
          <Button 
            onClick={handleSearch}
            disabled={loading || searchQuery.length < 2}
            className="bg-gradient-to-r from-cyan-500 to-teal-500 hover:from-cyan-600 hover:to-teal-600 text-white px-8 h-12"
          >
            {loading ? "Aranıyor..." : "Ara"}
          </Button>
        </div>
      </div>

      {/* Search Results */}
      {searchResults && (
        <div className="space-y-6">
          {/* Reservations Results */}
          {searchResults.reservations && searchResults.reservations.length > 0 && (
            <div className="bg-white rounded-2xl border border-slate-200 shadow-lg p-6">
              <div className="flex items-center gap-3 mb-4">
                <Calendar className="w-6 h-6 text-blue-600" />
                <h3 className="text-lg font-bold text-slate-800">Rezervasyonlar ({searchResults.reservations.length})</h3>
              </div>
              <div className="space-y-3">
                {searchResults.reservations.map((reservation) => (
                  <div key={reservation.id} className="p-4 border border-slate-200 rounded-lg hover:bg-slate-50 transition-colors">
                    <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                      <div>
                        <p className="text-xs text-slate-500 mb-1">Voucher No</p>
                        <p className="font-bold text-slate-800">{reservation.voucherNo}</p>
                      </div>
                      <div>
                        <p className="text-xs text-slate-500 mb-1">Grup Lideri</p>
                        <p className="font-semibold text-slate-800">{reservation.leader_name}</p>
                        <p className="text-xs text-slate-600">{reservation.leader_passport}</p>
                      </div>
                      <div>
                        <p className="text-xs text-slate-500 mb-1">Otel</p>
                        <p className="font-semibold text-slate-800">{reservation.hotel}</p>
                      </div>
                      <div>
                        <p className="text-xs text-slate-500 mb-1">Durum</p>
                        <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                          reservation.status === 'confirmed' ? 'bg-green-100 text-green-800' : 'bg-orange-100 text-orange-800'
                        }`}>
                          {reservation.status === 'confirmed' ? 'Onaylı' : 'Bekleyen'}
                        </span>
                      </div>
                    </div>
                    <div className="mt-3 pt-3 border-t border-slate-200 grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                      <div className="flex items-center gap-2">
                        <Calendar className="w-4 h-4 text-slate-400" />
                        <span className="text-slate-600">{reservation.arrivalDate} - {reservation.departureDate}</span>
                      </div>
                      <div className="flex items-center gap-2">
                        <Users className="w-4 h-4 text-slate-400" />
                        <span className="text-slate-600">{reservation.pax} kişi</span>
                      </div>
                      <div className="flex items-center gap-2">
                        <MapPin className="w-4 h-4 text-slate-400" />
                        <span className="text-slate-600">{reservation.product_code}</span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Flights Results */}
          {searchResults.flights && searchResults.flights.length > 0 && (
            <div className="bg-white rounded-2xl border border-slate-200 shadow-lg p-6">
              <div className="flex items-center gap-3 mb-4">
                <Plane className="w-6 h-6 text-purple-600" />
                <h3 className="text-lg font-bold text-slate-800">Uçuşlar ({searchResults.flights.length})</h3>
              </div>
              <div className="space-y-3">
                {searchResults.flights.map((flight) => (
                  <div key={flight.id} className="p-4 border border-slate-200 rounded-lg hover:bg-slate-50 transition-colors">
                    <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                      <div>
                        <p className="text-xs text-slate-500 mb-1">Uçuş Kodu</p>
                        <p className="font-bold text-slate-800">{flight.flightCode}</p>
                      </div>
                      <div>
                        <p className="text-xs text-slate-500 mb-1">Güzergah</p>
                        <p className="font-semibold text-slate-800">{flight.from} → {flight.to}</p>
                      </div>
                      <div>
                        <p className="text-xs text-slate-500 mb-1">Tarih & Saat</p>
                        <p className="font-semibold text-slate-800">{flight.date} {flight.time}</p>
                      </div>
                      <div>
                        <p className="text-xs text-slate-500 mb-1">PNR</p>
                        {flight.hasPNR ? (
                          <p className="font-semibold text-green-700">{flight.pnr}</p>
                        ) : (
                          <span className="text-red-600 font-semibold">Eksik</span>
                        )}
                      </div>
                    </div>
                    <div className="mt-3 pt-3 border-t border-slate-200 flex items-center gap-4 text-sm">
                      <div className="flex items-center gap-2">
                        <Users className="w-4 h-4 text-slate-400" />
                        <span className="text-slate-600">{flight.passengers} yolcu</span>
                      </div>
                      <div className="flex items-center gap-2">
                        <Clock className="w-4 h-4 text-slate-400" />
                        <span className="text-slate-600">{flight.daysUntilFlight} gün kaldı</span>
                      </div>
                      <span className={`px-2.5 py-0.5 rounded-full text-xs font-medium ${
                        flight.direction === 'arrival' ? 'bg-green-100 text-green-800' : 'bg-orange-100 text-orange-800'
                      }`}>
                        {flight.direction === 'arrival' ? 'Geliş' : 'Gidiş'}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* No Results */}
          {searchResults.reservations.length === 0 && searchResults.flights.length === 0 && (
            <div className="bg-white rounded-2xl border border-slate-200 shadow-lg p-12 text-center">
              <Search className="w-16 h-16 text-slate-300 mx-auto mb-4" />
              <h3 className="text-xl font-bold text-slate-800 mb-2">Sonuç Bulunamadı</h3>
              <p className="text-slate-600">'{searchQuery}' için hiçbir kayıt bulunamadı.</p>
            </div>
          )}
        </div>
      )}

      {/* Info Cards When No Search */}
      {!searchResults && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="bg-white rounded-xl p-6 border border-slate-200 shadow-sm">
            <div className="w-12 h-12 rounded-lg bg-blue-100 flex items-center justify-center mb-4">
              <Calendar className="w-6 h-6 text-blue-600" />
            </div>
            <h3 className="text-lg font-bold text-slate-800 mb-2">Rezervasyon Takibi</h3>
            <p className="text-sm text-slate-600">Yolcu bilgileri, voucher numarası veya otel adı ile arama yapın.</p>
          </div>

          <div className="bg-white rounded-xl p-6 border border-slate-200 shadow-sm">
            <div className="w-12 h-12 rounded-lg bg-purple-100 flex items-center justify-center mb-4">
              <Plane className="w-6 h-6 text-purple-600" />
            </div>
            <h3 className="text-lg font-bold text-slate-800 mb-2">Uçuş Bilgileri</h3>
            <p className="text-sm text-slate-600">PNR kodu veya uçuş numarası ile uçuş detaylarına ulaşın.</p>
          </div>

          <div className="bg-white rounded-xl p-6 border border-slate-200 shadow-sm">
            <div className="w-12 h-12 rounded-lg bg-green-100 flex items-center justify-center mb-4">
              <Users className="w-6 h-6 text-green-600" />
            </div>
            <h3 className="text-lg font-bold text-slate-800 mb-2">Merkezi Kontrol</h3>
            <p className="text-sm text-slate-600">Tüm departmanların verilerine tek noktadan erişim.</p>
          </div>
        </div>
      )}
    </div>
  );
};

export default Management;