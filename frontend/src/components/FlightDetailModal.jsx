import React, { useState, useEffect } from "react";
import { X, Plane, Clock, MapPin, AlertCircle, CheckCircle, Info, Navigation, Gauge, Activity } from "lucide-react";
import api from "@/utils/api";

const FlightDetailModal = ({ isOpen, onClose, flightCode, airportCode = "IST" }) => {
  const [flightData, setFlightData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (isOpen && flightCode) {
      fetchFlightDetails();
    }
  }, [isOpen, flightCode]);

  const fetchFlightDetails = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await api.get(`/api/operations/flight-details/${flightCode}`, {
        params: { airport_code: airportCode }
      });
      setFlightData(response.data);
    } catch (err) {
      setError(err.response?.data?.detail || "Uçuş bilgileri yüklenirken hata oluştu");
      console.error("Flight details fetch error:", err);
    } finally {
      setLoading(false);
    }
  };

  if (!isOpen) return null;

  const getStatusColor = (status) => {
    const statusLower = status?.toLowerCase() || "";
    if (statusLower.includes("landed") || statusLower.includes("arrived")) return "bg-green-100 text-green-800";
    if (statusLower.includes("departed") || statusLower.includes("en-route")) return "bg-blue-100 text-blue-800";
    if (statusLower.includes("delayed")) return "bg-red-100 text-red-800";
    if (statusLower.includes("cancelled")) return "bg-gray-100 text-gray-800";
    if (statusLower.includes("scheduled")) return "bg-orange-100 text-orange-800";
    return "bg-slate-100 text-slate-800";
  };

  const getStatusText = (status) => {
    const statusLower = status?.toLowerCase() || "";
    if (statusLower.includes("landed") || statusLower.includes("arrived")) return "İniş Yapıldı";
    if (statusLower.includes("departed")) return "Kalkış Yaptı";
    if (statusLower.includes("en-route") || statusLower.includes("enroute")) return "Yolda";
    if (statusLower.includes("boarding")) return "Biniş Yapılıyor";
    if (statusLower.includes("delayed")) return "Rötarlı";
    if (statusLower.includes("cancelled")) return "İptal Edildi";
    if (statusLower.includes("scheduled")) return "Planlandı";
    if (statusLower.includes("taxiing")) return "Pistde";
    if (statusLower.includes("final approach")) return "İniş Yaklaşımında";
    
    // Diğer tüm İngilizce durumları Türkçe'ye çevir
    const translations = {
      "expected": "Bekleniyor",
      "airborne": "Havada",
      "diverted": "Yönlendirildi",
      "unknown": "Bilinmiyor",
      "gate arrival": "Kapıya Ulaştı",
      "gate departure": "Kapıdan Ayrıldı"
    };
    
    for (const [eng, tr] of Object.entries(translations)) {
      if (statusLower.includes(eng)) return tr;
    }
    
    return status || "Bilinmiyor";
  };

  const formatTime = (timeStr) => {
    if (!timeStr) return "-";
    try {
      const date = new Date(timeStr);
      return date.toLocaleTimeString("tr-TR", { hour: '2-digit', minute: '2-digit' });
    } catch {
      return timeStr;
    }
  };

  const formatDelay = (delay) => {
    if (!delay || delay === 0) return "Zamanında";
    return `${delay} dk rötar`;
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4">
      <div className="bg-white rounded-2xl shadow-2xl max-w-5xl w-full max-h-[90vh] overflow-hidden">
        {/* Header */}
        <div className="bg-gradient-to-r from-blue-600 to-cyan-600 text-white p-6 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <div className="w-14 h-14 rounded-xl bg-white/20 flex items-center justify-center">
              <Plane className="w-8 h-8" />
            </div>
            <div>
              <h2 className="text-2xl font-bold">Uçuş Detayları</h2>
              <p className="text-blue-100 text-sm">Gerçek Zamanlı Uçuş Bilgileri</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="w-10 h-10 rounded-lg bg-white/20 hover:bg-white/30 flex items-center justify-center transition-colors"
          >
            <X className="w-6 h-6" />
          </button>
        </div>

        {/* Content */}
        <div className="p-6 overflow-y-auto max-h-[calc(90vh-120px)]">
          {loading && (
            <div className="flex flex-col items-center justify-center py-12">
              <div className="w-16 h-16 border-4 border-blue-200 border-t-blue-600 rounded-full animate-spin mb-4"></div>
              <p className="text-slate-600 font-medium">Uçuş bilgileri yükleniyor...</p>
            </div>
          )}

          {error && (
            <div className="bg-red-50 border-2 border-red-200 rounded-xl p-6 flex items-start gap-4">
              <AlertCircle className="w-6 h-6 text-red-600 flex-shrink-0 mt-1" />
              <div>
                <h3 className="font-bold text-red-900 mb-1">Hata</h3>
                <p className="text-red-700">{error}</p>
              </div>
            </div>
          )}

          {!loading && !error && flightData && (
            <div className="space-y-6">
              {/* Flight Identity */}
              <div className="bg-gradient-to-br from-blue-50 to-cyan-50 rounded-xl p-6 border border-blue-200">
                <h3 className="text-lg font-bold text-slate-800 mb-4 flex items-center gap-2">
                  <Info className="w-5 h-5 text-blue-600" />
                  Uçuş Kimliği
                </h3>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  <div>
                    <div className="text-xs text-slate-500 mb-1">Uçuş Numarası (IATA)</div>
                    <div className="text-xl font-bold text-slate-900">{flightData.flight_number || flightCode}</div>
                  </div>
                  <div>
                    <div className="text-xs text-slate-500 mb-1">Callsign</div>
                    <div className="font-semibold text-slate-800">{flightData.callsign || "-"}</div>
                  </div>
                  <div>
                    <div className="text-xs text-slate-500 mb-1">Havayolu</div>
                    <div className="font-semibold text-slate-800">{flightData.airline?.name || "-"}</div>
                  </div>
                  <div>
                    <div className="text-xs text-slate-500 mb-1">Durum</div>
                    <span className={`inline-block px-3 py-1 rounded-full text-xs font-medium ${getStatusColor(flightData.status)}`}>
                      {getStatusText(flightData.status)}
                    </span>
                  </div>
                </div>
              </div>

              {/* Aircraft Info */}
              {flightData.aircraft && (
                <div className="bg-slate-50 rounded-xl p-6 border border-slate-200">
                  <h3 className="text-lg font-bold text-slate-800 mb-4 flex items-center gap-2">
                    <Plane className="w-5 h-5 text-slate-600" />
                    Uçak Bilgileri
                  </h3>
                  <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                    <div>
                      <div className="text-xs text-slate-500 mb-1">Uçak Tipi</div>
                      <div className="font-semibold text-slate-800">{flightData.aircraft.model || "-"}</div>
                    </div>
                    <div>
                      <div className="text-xs text-slate-500 mb-1">Kayıt Numarası</div>
                      <div className="font-semibold text-slate-800">{flightData.aircraft.registration || "-"}</div>
                    </div>
                    <div>
                      <div className="text-xs text-slate-500 mb-1">IATA / ICAO</div>
                      <div className="font-semibold text-slate-800">
                        {flightData.airline?.iata || "-"} / {flightData.airline?.icao || "-"}
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {/* Departure Info */}
              <div className="bg-gradient-to-br from-orange-50 to-red-50 rounded-xl p-6 border border-orange-200">
                <h3 className="text-lg font-bold text-slate-800 mb-4 flex items-center gap-2">
                  <MapPin className="w-5 h-5 text-orange-600" />
                  Kalkış Bilgileri (DEPARTURE)
                </h3>
                <div className="space-y-4">
                  <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                    <div className="col-span-2 md:col-span-1">
                      <div className="text-xs text-slate-500 mb-1">Havalimanı</div>
                      <div className="font-bold text-slate-900">{flightData.departure?.airport || "-"}</div>
                      <div className="text-sm text-slate-600">
                        {flightData.departure?.iata || "-"} / {flightData.departure?.icao || "-"}
                      </div>
                    </div>
                    <div>
                      <div className="text-xs text-slate-500 mb-1">Terminal</div>
                      <div className="font-semibold text-slate-800">{flightData.departure?.terminal || "-"}</div>
                    </div>
                    <div>
                      <div className="text-xs text-slate-500 mb-1">Gate</div>
                      <div className="font-semibold text-slate-800">{flightData.departure?.gate || "-"}</div>
                    </div>
                  </div>
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4 pt-4 border-t border-orange-200">
                    <div className="flex items-start gap-3">
                      <Clock className="w-5 h-5 text-orange-600 mt-1" />
                      <div>
                        <div className="text-xs text-slate-500">Planlanan Kalkış (STD)</div>
                        <div className="font-bold text-slate-900">{formatTime(flightData.departure?.scheduled_time)}</div>
                      </div>
                    </div>
                    <div className="flex items-start gap-3">
                      <Clock className="w-5 h-5 text-blue-600 mt-1" />
                      <div>
                        <div className="text-xs text-slate-500">Tahmini Kalkış (ETD)</div>
                        <div className="font-bold text-slate-900">{formatTime(flightData.departure?.estimated_time)}</div>
                      </div>
                    </div>
                    <div className="flex items-start gap-3">
                      <CheckCircle className="w-5 h-5 text-green-600 mt-1" />
                      <div>
                        <div className="text-xs text-slate-500">Gerçek Kalkış (ATD)</div>
                        <div className="font-bold text-slate-900">{formatTime(flightData.departure?.actual_time)}</div>
                      </div>
                    </div>
                  </div>
                  <div className="bg-white rounded-lg p-3 border border-orange-200">
                    <div className="text-xs text-slate-500">Rötar Durumu</div>
                    <div className={`font-bold ${flightData.departure?.delay > 0 ? 'text-red-600' : 'text-green-600'}`}>
                      {formatDelay(flightData.departure?.delay)}
                    </div>
                  </div>
                </div>
              </div>

              {/* Arrival Info */}
              <div className="bg-gradient-to-br from-green-50 to-emerald-50 rounded-xl p-6 border border-green-200">
                <h3 className="text-lg font-bold text-slate-800 mb-4 flex items-center gap-2">
                  <MapPin className="w-5 h-5 text-green-600" />
                  Varış Bilgileri (ARRIVAL)
                </h3>
                <div className="space-y-4">
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                    <div className="col-span-2 md:col-span-1">
                      <div className="text-xs text-slate-500 mb-1">Havalimanı</div>
                      <div className="font-bold text-slate-900">{flightData.arrival?.airport || "-"}</div>
                      <div className="text-sm text-slate-600">
                        {flightData.arrival?.iata || "-"} / {flightData.arrival?.icao || "-"}
                      </div>
                    </div>
                    <div>
                      <div className="text-xs text-slate-500 mb-1">Terminal</div>
                      <div className="font-semibold text-slate-800">{flightData.arrival?.terminal || "-"}</div>
                    </div>
                    <div>
                      <div className="text-xs text-slate-500 mb-1">Gate</div>
                      <div className="font-semibold text-slate-800">{flightData.arrival?.gate || "-"}</div>
                    </div>
                    <div>
                      <div className="text-xs text-slate-500 mb-1">Bagaj Bandı</div>
                      <div className="font-semibold text-slate-800">{flightData.arrival?.baggage || "-"}</div>
                    </div>
                  </div>
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4 pt-4 border-t border-green-200">
                    <div className="flex items-start gap-3">
                      <Clock className="w-5 h-5 text-green-600 mt-1" />
                      <div>
                        <div className="text-xs text-slate-500">Planlanan İniş (STA)</div>
                        <div className="font-bold text-slate-900">{formatTime(flightData.arrival?.scheduled_time)}</div>
                      </div>
                    </div>
                    <div className="flex items-start gap-3">
                      <Clock className="w-5 h-5 text-blue-600 mt-1" />
                      <div>
                        <div className="text-xs text-slate-500">Tahmini İniş (ETA)</div>
                        <div className="font-bold text-slate-900">{formatTime(flightData.arrival?.estimated_time)}</div>
                      </div>
                    </div>
                    <div className="flex items-start gap-3">
                      <CheckCircle className="w-5 h-5 text-green-600 mt-1" />
                      <div>
                        <div className="text-xs text-slate-500">Gerçek İniş (ATA)</div>
                        <div className="font-bold text-slate-900">{formatTime(flightData.arrival?.actual_time)}</div>
                      </div>
                    </div>
                  </div>
                  <div className="bg-white rounded-lg p-3 border border-green-200">
                    <div className="text-xs text-slate-500">Rötar Durumu</div>
                    <div className={`font-bold ${flightData.arrival?.delay > 0 ? 'text-red-600' : 'text-green-600'}`}>
                      {formatDelay(flightData.arrival?.delay)}
                    </div>
                  </div>
                </div>
              </div>

              {/* Flight Times & Distance */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="bg-blue-50 rounded-xl p-6 border border-blue-200">
                  <h4 className="text-sm font-bold text-slate-800 mb-3 flex items-center gap-2">
                    <Activity className="w-4 h-4 text-blue-600" />
                    Uçuş Süreleri
                  </h4>
                  <div>
                    <div className="text-xs text-slate-500">Planlanan Süre</div>
                    <div className="text-2xl font-bold text-slate-900">
                      {flightData.duration ? `${Math.floor(flightData.duration / 60)}s ${flightData.duration % 60}dk` : "-"}
                    </div>
                  </div>
                </div>
                <div className="bg-purple-50 rounded-xl p-6 border border-purple-200">
                  <h4 className="text-sm font-bold text-slate-800 mb-3 flex items-center gap-2">
                    <Navigation className="w-4 h-4 text-purple-600" />
                    Mesafe Bilgisi
                  </h4>
                  <div>
                    <div className="text-xs text-slate-500">Uçuş Mesafesi</div>
                    <div className="text-2xl font-bold text-slate-900">
                      {flightData.distance ? `${flightData.distance} km` : "-"}
                    </div>
                  </div>
                </div>
              </div>

              {/* Last Updated */}
              <div className="text-center text-xs text-slate-500 pt-4 border-t border-slate-200">
                Son Güncelleme: {flightData.last_updated ? new Date(flightData.last_updated).toLocaleString("tr-TR") : "-"}
              </div>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="border-t border-slate-200 p-4 bg-slate-50 flex justify-end">
          <button
            onClick={onClose}
            className="px-6 py-2 bg-gradient-to-r from-blue-600 to-cyan-600 hover:from-blue-700 hover:to-cyan-700 text-white rounded-lg font-semibold transition-all"
          >
            Kapat
          </button>
        </div>
      </div>
    </div>
  );
};

export default FlightDetailModal;
