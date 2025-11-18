import React, { useState, useEffect } from "react";
import { Upload, AlertCircle, CheckCircle, XCircle, FileSpreadsheet, Search, Filter, X } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { mockFlights } from "@/lib/mockFlightData";
import api from "@/utils/api";
import { useAuth } from "@/context/AuthContext";

const Flights = () => {
  const { user } = useAuth();
  const [searchTerm, setSearchTerm] = useState("");
  const [filterPNR, setFilterPNR] = useState("all");
  const [uploadFile, setUploadFile] = useState(null);
  const [compareResult, setCompareResult] = useState(null);
  const [isComparing, setIsComparing] = useState(false);
  const [compareError, setCompareError] = useState(null);
  const [flights, setFlights] = useState([]);

  useEffect(() => {
    fetchFlights();
  }, []);

  const fetchFlights = async () => {
    try {
      const response = await api.get('/api/flights');
      setFlights(response.data.length > 0 ? response.data : mockFlights);
    } catch (error) {
      console.error("Failed to fetch flights:", error);
      setFlights(mockFlights);
    }
  };

  const filteredFlights = flights.filter(flight => {
    const matchesSearch = flight.flightCode.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesPNR = filterPNR === "all" || 
                      (filterPNR === "with" && flight.hasPNR) ||
                      (filterPNR === "without" && !flight.hasPNR);
    return matchesSearch && matchesPNR;
  });

  const pendingTickets = flights.filter(f => !f.hasPNR && f.daysUntilFlight <= 7);

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      setUploadFile(file);
      setCompareError(null);
      setCompareResult(null);
    }
  };

  const handleCompare = async () => {
    if (!uploadFile) {
      setCompareError("Lütfen bir Excel dosyası seçin");
      return;
    }

    const formData = new FormData();
    formData.append("file", uploadFile);

    try {
      setIsComparing(true);
      setCompareError(null);

      const response = await api.post(
        '/api/flights/compare',
        formData,
        {
          headers: {
            "Content-Type": "multipart/form-data",
          },
        }
      );

      setCompareResult(response.data);
    } catch (error) {
      setCompareError(error.response?.data?.detail || "Karşılaştırma başarısız oldu");
    } finally {
      setIsComparing(false);
    }
  };

  const resetCompare = () => {
    setUploadFile(null);
    setCompareResult(null);
    setCompareError(null);
    const fileInput = document.getElementById("compare-file-upload");
    if (fileInput) fileInput.value = "";
  };

  return (
    <div className="space-y-6" data-testid="flights-page">
      {/* Warning Panel */}
      {pendingTickets.length > 0 && (
        <div className="bg-red-50 border-l-4 border-red-500 p-6 rounded-xl" data-testid="warning-panel">
          <div className="flex items-start gap-4">
            <div className="w-10 h-10 rounded-lg bg-red-500 flex items-center justify-center flex-shrink-0">
              <AlertCircle className="w-6 h-6 text-white" />
            </div>
            <div className="flex-1">
              <h3 className="text-lg font-bold text-red-800 mb-2">Acil Uyarı!</h3>
              <p className="text-red-700">
                <strong>{pendingTickets.length}</strong> adet uçuş için PNR eksik ve uçuşa 7 günden az kaldı!
              </p>
              <div className="mt-3 space-y-1">
                {pendingTickets.map(flight => (
                  <p key={flight.id} className="text-sm text-red-600">
                    • {flight.flightCode} - {flight.date} ({flight.daysUntilFlight} gün kaldı)
                  </p>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Stats */}
      <div className="grid grid-cols-1 sm:grid-cols-4 gap-4">
        <div className="bg-white rounded-xl p-6 border border-slate-200 shadow-sm">
          <div className="flex items-center gap-4">
            <div className="w-14 h-14 rounded-xl bg-gradient-to-br from-blue-500 to-blue-600 flex items-center justify-center shadow-lg">
              <FileSpreadsheet className="w-7 h-7 text-white" />
            </div>
            <div>
              <p className="text-sm text-slate-500">Toplam Uçuş</p>
              <p className="text-3xl font-bold text-slate-800">{mockFlights.length}</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-xl p-6 border border-slate-200 shadow-sm">
          <div className="flex items-center gap-4">
            <div className="w-14 h-14 rounded-xl bg-gradient-to-br from-green-500 to-green-600 flex items-center justify-center shadow-lg">
              <CheckCircle className="w-7 h-7 text-white" />
            </div>
            <div>
              <p className="text-sm text-slate-500">PNR Mevcut</p>
              <p className="text-3xl font-bold text-slate-800">
                {mockFlights.filter(f => f.hasPNR).length}
              </p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-xl p-6 border border-slate-200 shadow-sm">
          <div className="flex items-center gap-4">
            <div className="w-14 h-14 rounded-xl bg-gradient-to-br from-red-500 to-red-600 flex items-center justify-center shadow-lg">
              <XCircle className="w-7 h-7 text-white" />
            </div>
            <div>
              <p className="text-sm text-slate-500">PNR Eksik</p>
              <p className="text-3xl font-bold text-slate-800">
                {mockFlights.filter(f => !f.hasPNR).length}
              </p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-xl p-6 border border-slate-200 shadow-sm">
          <div className="flex items-center gap-4">
            <div className="w-14 h-14 rounded-xl bg-gradient-to-br from-orange-500 to-orange-600 flex items-center justify-center shadow-lg">
              <AlertCircle className="w-7 h-7 text-white" />
            </div>
            <div>
              <p className="text-sm text-slate-500">Kritik (7gün)</p>
              <p className="text-3xl font-bold text-slate-800">{pendingTickets.length}</p>
            </div>
          </div>
        </div>
      </div>

      {/* Excel Compare Section */}
      <div className="bg-white rounded-2xl border border-slate-200 shadow-lg p-6">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h3 className="text-lg font-bold text-slate-800">Excel Karşılaştırma</h3>
            <p className="text-sm text-slate-500 mt-1">Excel dosyasını veritabanı ile karşılaştırın</p>
          </div>
          {compareResult && (
            <Button 
              onClick={resetCompare}
              variant="outline"
              size="sm"
              data-testid="reset-compare-btn"
            >
              <X className="w-4 h-4 mr-2" />
              Sıfırla
            </Button>
          )}
        </div>

        {!compareResult ? (
          <div>
            <div className="border-2 border-dashed border-slate-300 rounded-xl p-8 text-center hover:border-cyan-400 transition-colors">
              <div className="flex flex-col items-center gap-4">
                <div className="w-16 h-16 rounded-full bg-purple-100 flex items-center justify-center">
                  <FileSpreadsheet className="w-8 h-8 text-purple-600" />
                </div>
                
                <div>
                  <label htmlFor="compare-file-upload" className="cursor-pointer">
                    <span className="text-purple-600 hover:text-purple-700 font-semibold">
                      Excel dosyası seçin
                    </span>
                    <span className="text-slate-600"> veya sürükleyin</span>
                  </label>
                  <input
                    id="compare-file-upload"
                    type="file"
                    accept=".xlsx,.xls"
                    onChange={handleFileChange}
                    className="hidden"
                  />
                  <p className="text-sm text-slate-500 mt-2">Excel dosyası (.xlsx, .xls)</p>
                </div>

                {uploadFile && (
                  <div className="flex items-center gap-3 px-4 py-2 bg-slate-100 rounded-lg">
                    <FileSpreadsheet className="w-5 h-5 text-slate-600" />
                    <span className="font-medium text-slate-800">{uploadFile.name}</span>
                  </div>
                )}

                <Button
                  onClick={handleCompare}
                  disabled={!uploadFile || isComparing}
                  className="bg-gradient-to-r from-purple-500 to-purple-600 hover:from-purple-600 hover:to-purple-700 text-white px-8"
                >
                  {isComparing ? "Karşılaştırılıyor..." : "Karşılaştır"}
                </Button>
              </div>
            </div>

            {compareError && (
              <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-lg flex items-start gap-3">
                <AlertCircle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
                <div>
                  <p className="font-semibold text-red-800">Hata!</p>
                  <p className="text-sm text-red-700">{compareError}</p>
                </div>
              </div>
            )}
          </div>
        ) : (
          <div className="space-y-6">
            {/* Summary Cards */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="p-4 bg-green-50 border border-green-200 rounded-lg">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-green-600 mb-1">Yeni Kayıtlar</p>
                    <p className="text-3xl font-bold text-green-800">{compareResult.summary.new}</p>
                  </div>
                  <div className="w-12 h-12 rounded-lg bg-green-200 flex items-center justify-center">
                    <CheckCircle className="w-6 h-6 text-green-700" />
                  </div>
                </div>
                <p className="text-xs text-green-600 mt-2">Veritabanında yok</p>
              </div>

              <div className="p-4 bg-blue-50 border border-blue-200 rounded-lg">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-blue-600 mb-1">Güncellenen</p>
                    <p className="text-3xl font-bold text-blue-800">{compareResult.summary.updated}</p>
                  </div>
                  <div className="w-12 h-12 rounded-lg bg-blue-200 flex items-center justify-center">
                    <AlertCircle className="w-6 h-6 text-blue-700" />
                  </div>
                </div>
                <p className="text-xs text-blue-600 mt-2">Farklılık var</p>
              </div>

              <div className="p-4 bg-orange-50 border border-orange-200 rounded-lg">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-orange-600 mb-1">Eksik Kayıtlar</p>
                    <p className="text-3xl font-bold text-orange-800">{compareResult.summary.missing}</p>
                  </div>
                  <div className="w-12 h-12 rounded-lg bg-orange-200 flex items-center justify-center">
                    <XCircle className="w-6 h-6 text-orange-700" />
                  </div>
                </div>
                <p className="text-xs text-orange-600 mt-2">Excel'de yok</p>
              </div>
            </div>

            {/* New Flights */}
            {compareResult.new_flights && compareResult.new_flights.length > 0 && (
              <div className="border border-green-200 rounded-lg overflow-hidden">
                <div className="bg-green-50 px-4 py-3 border-b border-green-200">
                  <h4 className="font-bold text-green-900">Yeni Uçuşlar (Veritabanında Yok)</h4>
                </div>
                <div className="divide-y divide-green-100">
                  {compareResult.new_flights.map((flight, idx) => (
                    <div key={idx} className="p-4 hover:bg-green-50 transition-colors">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-4">
                          <span className="font-bold text-slate-800">{flight.flightCode}</span>
                          <span className="text-slate-600">{flight.from} → {flight.to}</span>
                          <span className="text-sm text-slate-500">{flight.date}</span>
                        </div>
                        <span className={`px-2.5 py-0.5 rounded-full text-xs font-medium ${
                          flight.hasPNR ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                        }`}>
                          {flight.hasPNR ? 'PNR Var' : 'PNR Yok'}
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Updated Flights */}
            {compareResult.updated_flights && compareResult.updated_flights.length > 0 && (
              <div className="border border-blue-200 rounded-lg overflow-hidden">
                <div className="bg-blue-50 px-4 py-3 border-b border-blue-200">
                  <h4 className="font-bold text-blue-900">Güncellenmiş Uçuşlar (PNR Farklı)</h4>
                </div>
                <div className="divide-y divide-blue-100">
                  {compareResult.updated_flights.map((flight, idx) => (
                    <div key={idx} className="p-4 hover:bg-blue-50 transition-colors">
                      <div className="flex items-center justify-between">
                        <div>
                          <div className="flex items-center gap-4 mb-2">
                            <span className="font-bold text-slate-800">{flight.flightCode}</span>
                            <span className="text-sm text-slate-500">{flight.date}</span>
                          </div>
                          <div className="flex items-center gap-4 text-sm">
                            <span className="text-red-600">Eski PNR: {flight.oldPNR || "Yok"}</span>
                            <span className="text-slate-400">→</span>
                            <span className="text-green-600">Yeni PNR: {flight.newPNR || "Yok"}</span>
                          </div>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Missing Flights */}
            {compareResult.missing_flights && compareResult.missing_flights.length > 0 && (
              <div className="border border-orange-200 rounded-lg overflow-hidden">
                <div className="bg-orange-50 px-4 py-3 border-b border-orange-200">
                  <h4 className="font-bold text-orange-900">Eksik Uçuşlar (Excel'de Yok)</h4>
                </div>
                <div className="divide-y divide-orange-100">
                  {compareResult.missing_flights.map((flight, idx) => (
                    <div key={idx} className="p-4 hover:bg-orange-50 transition-colors">
                      <div className="flex items-center gap-4">
                        <span className="font-bold text-slate-800">{flight.flightCode}</span>
                        <span className="text-slate-600">{flight.from} → {flight.to}</span>
                        <span className="text-sm text-slate-500">{flight.date}</span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Flights List */}
      <div className="bg-white rounded-2xl border border-slate-200 shadow-lg p-6">
        <div className="flex flex-col lg:flex-row gap-4 items-start lg:items-center justify-between mb-6">
          <h3 className="text-lg font-bold text-slate-800">Uçuş Listesi</h3>
          
          <div className="flex flex-col sm:flex-row gap-3 w-full lg:w-auto">
            <div className="relative flex-1 lg:w-64">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
              <Input
                placeholder="Uçuş kodu ara..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10"
                data-testid="flight-search"
              />
            </div>
            
            <Select value={filterPNR} onValueChange={setFilterPNR}>
              <SelectTrigger className="w-full sm:w-48" data-testid="pnr-filter">
                <Filter className="w-4 h-4 mr-2" />
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">Tüm Uçuşlar</SelectItem>
                <SelectItem value="with">PNR Mevcut</SelectItem>
                <SelectItem value="without">PNR Eksik</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full" data-testid="flights-table">
            <thead className="bg-slate-50 border-b border-slate-200">
              <tr>
                <th className="px-6 py-4 text-left text-xs font-semibold text-slate-600 uppercase">Uçuş Kodu</th>
                <th className="px-6 py-4 text-left text-xs font-semibold text-slate-600 uppercase">Güzergah</th>
                <th className="px-6 py-4 text-left text-xs font-semibold text-slate-600 uppercase">Tarih & Saat</th>
                <th className="px-6 py-4 text-left text-xs font-semibold text-slate-600 uppercase">Yön</th>
                <th className="px-6 py-4 text-left text-xs font-semibold text-slate-600 uppercase">Yolcu</th>
                <th className="px-6 py-4 text-left text-xs font-semibold text-slate-600 uppercase">PNR Durumu</th>
                <th className="px-6 py-4 text-left text-xs font-semibold text-slate-600 uppercase">Kalan Gün</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {filteredFlights.map((flight) => (
                <tr 
                  key={flight.id} 
                  className="hover:bg-slate-50 transition-colors"
                  data-testid={`flight-row-${flight.id}`}
                >
                  <td className="px-6 py-4">
                    <span className="font-semibold text-slate-800">{flight.flightCode}</span>
                  </td>
                  <td className="px-6 py-4 text-slate-700">
                    {flight.from} → {flight.to}
                  </td>
                  <td className="px-6 py-4 text-slate-700">
                    {flight.date} • {flight.time}
                  </td>
                  <td className="px-6 py-4">
                    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                      flight.direction === 'arrival' ? 'bg-green-100 text-green-800' : 'bg-orange-100 text-orange-800'
                    }`}>
                      {flight.direction === 'arrival' ? 'Geliş' : 'Gidiş'}
                    </span>
                  </td>
                  <td className="px-6 py-4 text-slate-700">{flight.passengers}</td>
                  <td className="px-6 py-4">
                    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                      flight.hasPNR ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                    }`}>
                      {flight.hasPNR ? 'Mevcut' : 'Eksik'}
                    </span>
                  </td>
                  <td className="px-6 py-4">
                    <span className={`font-semibold ${
                      flight.daysUntilFlight <= 3 ? 'text-red-600' :
                      flight.daysUntilFlight <= 7 ? 'text-orange-600' :
                      'text-slate-600'
                    }`}>
                      {flight.daysUntilFlight} gün
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

export default Flights;