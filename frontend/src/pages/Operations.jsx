import React, { useState, useEffect } from "react";
import { Calendar, Users, MapPin, Plane, Clock, Hotel, FileText, Filter, ArrowRight, ChevronDown } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import axios from "axios";

const Operations = () => {
  const [selectedDate, setSelectedDate] = useState(new Date().toISOString().split('T')[0]);
  const [filterType, setFilterType] = useState("all"); // all, arrival, departure
  const [operations, setOperations] = useState([]);
  const [loading, setLoading] = useState(false);
  const [expandedOperation, setExpandedOperation] = useState(null);

  useEffect(() => {
    fetchOperations();
  }, [selectedDate, filterType]);

  const fetchOperations = async () => {
    setLoading(true);
    try {
      const response = await axios.get(`${process.env.REACT_APP_BACKEND_URL}/api/operations`, {
        params: { date: selectedDate, type: filterType }
      });
      setOperations(response.data || []);
    } catch (error) {
      console.error("Operations fetch error:", error);
      // Mock data for development
      setOperations([
        {
          id: 1,
          flightCode: "OS840",
          type: "arrival",
          from: "VIE",
          to: "AYT",
          date: selectedDate,
          time: "14:30",
          passengers: 156,
          hotel: "Rixos Premium Belek",
          transferTime: "16:00",
          notes: "Grup transferi, lüks araç gerekli",
          status: "scheduled",
          pickupLocation: "Antalya Havalimanı",
          dropoffLocation: "Rixos Premium Belek - Belek"
        },
        {
          id: 2,
          flightCode: "TK1990",
          type: "departure",
          from: "AYT",
          to: "IST",
          date: selectedDate,
          time: "08:45",
          passengers: 98,
          hotel: "Granada Luxury Resort",
          transferTime: "06:00",
          notes: "Erken sabah transferi",
          status: "completed",
          pickupLocation: "Granada Luxury Resort - Kemer",
          dropoffLocation: "Antalya Havalimanı"
        },
        {
          id: 3,
          flightCode: "XQ105",
          type: "arrival",
          from: "DUS",
          to: "AYT",
          date: selectedDate,
          time: "18:15",
          passengers: 189,
          hotel: "Club Hotel Falcon",
          transferTime: "19:45",
          notes: "2 otobüs gerekli",
          status: "in_progress",
          pickupLocation: "Antalya Havalimanı",
          dropoffLocation: "Club Hotel Falcon - Antalya"
        }
      ]);
    } finally {
      setLoading(false);
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

  const arrivalCount = operations.filter(op => op.type === 'arrival').length;
  const departureCount = operations.filter(op => op.type === 'departure').length;

  return (
    <div className="space-y-6" data-testid="operations-page">
      {/* Header with Stats */}
      <div className="bg-white rounded-2xl border border-slate-200 shadow-lg p-6">
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center gap-4">
            <div className="w-14 h-14 rounded-xl bg-gradient-to-br from-orange-500 to-red-500 flex items-center justify-center shadow-lg">
              <Plane className="w-7 h-7 text-white" />
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
        <div className="flex flex-wrap gap-4">
          <div className="flex-1 min-w-[200px]">
            <label className="block text-sm font-medium text-slate-700 mb-2">Tarih Seçin</label>
            <Input
              type="date"
              value={selectedDate}
              onChange={(e) => setSelectedDate(e.target.value)}
              className="h-10"
              data-testid="date-picker"
            />
          </div>

          <div className="flex-1 min-w-[200px]">
            <label className="block text-sm font-medium text-slate-700 mb-2">Filtre</label>
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

          <div className="flex items-end">
            <Button
              onClick={fetchOperations}
              disabled={loading}
              className="bg-gradient-to-r from-orange-500 to-red-500 hover:from-orange-600 hover:to-red-600 text-white h-10"
            >
              <Filter className="w-4 h-4 mr-2" />
              {loading ? "Yükleniyor..." : "Uygula"}
            </Button>
          </div>
        </div>
      </div>

      {/* Operations List */}
      <div className="space-y-4">
        {operations.length === 0 ? (
          <div className="bg-white rounded-2xl border border-slate-200 shadow-lg p-12 text-center">
            <Plane className="w-16 h-16 text-slate-300 mx-auto mb-4" />
            <h3 className="text-xl font-bold text-slate-800 mb-2">Operasyon Bulunamadı</h3>
            <p className="text-slate-600">Seçili tarih için henüz operasyon planlanmamış.</p>
          </div>
        ) : (
          operations.map((operation) => (
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
                    {/* Flight Info */}
                    <div className="flex items-center gap-3">
                      <div className={`w-12 h-12 rounded-lg flex items-center justify-center ${
                        operation.type === 'arrival' ? 'bg-green-100' : 'bg-orange-100'
                      }`}>
                        <Plane className={`w-6 h-6 ${
                          operation.type === 'arrival' ? 'text-green-600' : 'text-orange-600'
                        }`} />
                      </div>
                      <div>
                        <div className="flex items-center gap-2">
                          <span className="text-xl font-bold text-slate-800">{operation.flightCode}</span>
                          <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                            operation.type === 'arrival' ? 'bg-green-100 text-green-700' : 'bg-orange-100 text-orange-700'
                          }`}>
                            {operation.type === 'arrival' ? 'Geliş' : 'Dönüş'}
                          </span>
                        </div>
                        <div className="flex items-center gap-2 text-sm text-slate-600 mt-1">
                          <span className="font-semibold">{operation.from}</span>
                          <ArrowRight className="w-4 h-4" />
                          <span className="font-semibold">{operation.to}</span>
                        </div>
                      </div>
                    </div>

                    {/* Time Info */}
                    <div className="flex gap-6">
                      <div>
                        <div className="text-xs text-slate-500 mb-1">Uçuş Saati</div>
                        <div className="flex items-center gap-2">
                          <Clock className="w-4 h-4 text-slate-400" />
                          <span className="font-semibold text-slate-800">{operation.time}</span>
                        </div>
                      </div>
                      <div>
                        <div className="text-xs text-slate-500 mb-1">Transfer Saati</div>
                        <div className="flex items-center gap-2">
                          <Clock className="w-4 h-4 text-slate-400" />
                          <span className="font-semibold text-slate-800">{operation.transferTime}</span>
                        </div>
                      </div>
                    </div>

                    {/* Hotel */}
                    <div>
                      <div className="text-xs text-slate-500 mb-1">Otel</div>
                      <div className="flex items-center gap-2">
                        <Hotel className="w-4 h-4 text-slate-400" />
                        <span className="font-semibold text-slate-800">{operation.hotel}</span>
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
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    {/* Transfer Route */}
                    <div>
                      <h4 className="text-sm font-bold text-slate-800 mb-3 flex items-center gap-2">
                        <MapPin className="w-4 h-4 text-blue-600" />
                        Transfer Güzergahı
                      </h4>
                      <div className="space-y-2">
                        <div className="flex items-start gap-3">
                          <div className="w-2 h-2 rounded-full bg-green-500 mt-1.5"></div>
                          <div>
                            <div className="text-xs text-slate-500">Alınış Noktası</div>
                            <div className="font-semibold text-slate-800">{operation.pickupLocation}</div>
                          </div>
                        </div>
                        <div className="h-8 border-l-2 border-dashed border-slate-300 ml-1"></div>
                        <div className="flex items-start gap-3">
                          <div className="w-2 h-2 rounded-full bg-red-500 mt-1.5"></div>
                          <div>
                            <div className="text-xs text-slate-500">Bırakılış Noktası</div>
                            <div className="font-semibold text-slate-800">{operation.dropoffLocation}</div>
                          </div>
                        </div>
                      </div>
                    </div>

                    {/* Notes */}
                    <div>
                      <h4 className="text-sm font-bold text-slate-800 mb-3 flex items-center gap-2">
                        <FileText className="w-4 h-4 text-orange-600" />
                        Operasyon Notları
                      </h4>
                      <div className="p-3 bg-white rounded-lg border border-slate-200">
                        <p className="text-sm text-slate-700">{operation.notes}</p>
                      </div>

                      {/* Action Buttons */}
                      <div className="flex gap-3 mt-4">
                        <Button
                          size="sm"
                          variant="outline"
                          className="flex-1"
                        >
                          Düzenle
                        </Button>
                        <Button
                          size="sm"
                          className="flex-1 bg-gradient-to-r from-orange-500 to-red-500 hover:from-orange-600 hover:to-red-600"
                        >
                          Tamamlandı İşaretle
                        </Button>
                      </div>
                    </div>
                  </div>
                </div>
              )}
            </div>
          ))
        )}
      </div>
    </div>
  );
};

export default Operations;
