import React, { useState, useEffect } from "react";
import { Search, Filter, Hotel as HotelIcon, MapPin, Star, Plus, Edit, Trash2, Phone, Mail, Globe, ChevronDown, ChevronUp, Building } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { useAuth } from "@/context/AuthContext";
import api from "@/utils/api";

const Hotels = () => {
  const { hasPermission } = useAuth();
  const [hotels, setHotels] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState("");
  const [filterRegion, setFilterRegion] = useState("all");
  const [expandedHotel, setExpandedHotel] = useState(null);
  
  // Load hotels
  const loadHotels = async () => {
    try {
      setLoading(true);
      const response = await api.get('/api/hotels', {
        params: { active_only: false }
      });
      setHotels(response.data);
    } catch (error) {
      console.error("Failed to load hotels:", error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadHotels();
  }, []);

  // Get unique regions for filter
  const uniqueRegions = [...new Set(hotels.map(h => h.region).filter(r => r))].sort();

  // Filter hotels
  const filteredHotels = hotels.filter(hotel => {
    const matchesSearch = 
      hotel.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      hotel.code.toLowerCase().includes(searchTerm.toLowerCase()) ||
      hotel.region.toLowerCase().includes(searchTerm.toLowerCase()) ||
      hotel.city.toLowerCase().includes(searchTerm.toLowerCase());
    
    const matchesRegion = filterRegion === "all" || hotel.region === filterRegion;
    
    return matchesSearch && matchesRegion;
  });

  const toggleExpand = (hotelId) => {
    setExpandedHotel(expandedHotel === hotelId ? null : hotelId);
  };

  return (
    <div className="space-y-6">
      {/* Stats Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-4 gap-4">
        <div className="bg-white rounded-xl p-6 border border-slate-200 shadow-sm">
          <div className="flex items-center gap-4">
            <div className="w-14 h-14 rounded-xl bg-gradient-to-br from-blue-500 to-blue-600 flex items-center justify-center shadow-lg">
              <HotelIcon className="w-7 h-7 text-white" />
            </div>
            <div>
              <p className="text-sm text-slate-500">Toplam Otel</p>
              <p className="text-3xl font-bold text-slate-800">{hotels.length}</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-xl p-6 border border-slate-200 shadow-sm">
          <div className="flex items-center gap-4">
            <div className="w-14 h-14 rounded-xl bg-gradient-to-br from-green-500 to-green-600 flex items-center justify-center shadow-lg">
              <Building className="w-7 h-7 text-white" />
            </div>
            <div>
              <p className="text-sm text-slate-500">Aktif Otel</p>
              <p className="text-3xl font-bold text-slate-800">
                {hotels.filter(h => h.active).length}
              </p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-xl p-6 border border-slate-200 shadow-sm">
          <div className="flex items-center gap-4">
            <div className="w-14 h-14 rounded-xl bg-gradient-to-br from-purple-500 to-purple-600 flex items-center justify-center shadow-lg">
              <MapPin className="w-7 h-7 text-white" />
            </div>
            <div>
              <p className="text-sm text-slate-500">Bölge Sayısı</p>
              <p className="text-3xl font-bold text-slate-800">{uniqueRegions.length}</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-xl p-6 border border-slate-200 shadow-sm">
          <div className="flex items-center gap-4">
            <div className="w-14 h-14 rounded-xl bg-gradient-to-br from-orange-500 to-orange-600 flex items-center justify-center shadow-lg">
              <Star className="w-7 h-7 text-white" />
            </div>
            <div>
              <p className="text-sm text-slate-500">5 Yıldız</p>
              <p className="text-3xl font-bold text-slate-800">
                {hotels.filter(h => h.stars === 5).length}
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Hotels Table */}
      <div className="bg-white rounded-2xl border border-slate-200 shadow-lg p-6">
        <div className="flex flex-col lg:flex-row gap-4 items-start lg:items-center justify-between mb-6">
          <h3 className="text-lg font-bold text-slate-800">Otel Listesi</h3>
          
          <div className="flex flex-col sm:flex-row gap-3 w-full lg:w-auto">
            <div className="relative flex-1 lg:w-64">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
              <Input
                placeholder="Otel ara..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10"
              />
            </div>
            
            <select
              value={filterRegion}
              onChange={(e) => setFilterRegion(e.target.value)}
              className="px-4 py-2 border border-slate-300 rounded-lg bg-white text-slate-700 focus:outline-none focus:ring-2 focus:ring-cyan-500"
            >
              <option value="all">Tüm Bölgeler</option>
              {uniqueRegions.map(region => (
                <option key={region} value={region}>{region}</option>
              ))}
            </select>
          </div>
        </div>

        {loading ? (
          <div className="text-center py-12">
            <div className="inline-block w-8 h-8 border-4 border-cyan-500 border-t-transparent rounded-full animate-spin"></div>
            <p className="mt-4 text-slate-600">Oteller yükleniyor...</p>
          </div>
        ) : filteredHotels.length === 0 ? (
          <div className="text-center py-12">
            <HotelIcon className="w-16 h-16 text-slate-300 mx-auto mb-4" />
            <p className="text-slate-600">Otel bulunamadı</p>
          </div>
        ) : (
          <div className="space-y-2">
            {filteredHotels.map((hotel) => (
              <div 
                key={hotel.id} 
                className="border border-slate-200 rounded-lg hover:shadow-md transition-shadow"
              >
                {/* Main Row */}
                <div className="p-4 flex items-center justify-between cursor-pointer" onClick={() => toggleExpand(hotel.id)}>
                  <div className="flex-1 grid grid-cols-1 md:grid-cols-5 gap-4">
                    {/* Hotel Name & Code */}
                    <div className="md:col-span-2">
                      <h4 className="font-semibold text-slate-800 text-sm">{hotel.name}</h4>
                      <p className="text-xs text-slate-500 mt-1">Kod: {hotel.code}</p>
                    </div>
                    
                    {/* Region */}
                    <div className="flex items-center gap-2">
                      <MapPin className="w-4 h-4 text-slate-400" />
                      <div>
                        <p className="text-sm text-slate-700">{hotel.region}</p>
                        <p className="text-xs text-slate-500">{hotel.city || 'N/A'}</p>
                      </div>
                    </div>
                    
                    {/* Category & Stars */}
                    <div>
                      <p className="text-sm text-slate-700">{hotel.category}</p>
                      <div className="flex items-center gap-1 mt-1">
                        {hotel.stars > 0 && (
                          <>
                            {[...Array(hotel.stars)].map((_, i) => (
                              <Star key={i} className="w-3 h-3 fill-yellow-400 text-yellow-400" />
                            ))}
                          </>
                        )}
                      </div>
                    </div>
                    
                    {/* Status */}
                    <div className="flex items-center justify-between">
                      <span className={`px-3 py-1 rounded-full text-xs font-medium ${
                        hotel.active 
                          ? 'bg-green-100 text-green-700' 
                          : 'bg-red-100 text-red-700'
                      }`}>
                        {hotel.active ? 'Aktif' : 'Pasif'}
                      </span>
                      
                      {expandedHotel === hotel.id ? (
                        <ChevronUp className="w-5 h-5 text-slate-400" />
                      ) : (
                        <ChevronDown className="w-5 h-5 text-slate-400" />
                      )}
                    </div>
                  </div>
                </div>

                {/* Expanded Details */}
                {expandedHotel === hotel.id && (
                  <div className="px-4 pb-4 pt-2 border-t border-slate-200 bg-slate-50">
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                      {/* Contact Info */}
                      <div className="space-y-2">
                        <h5 className="font-semibold text-slate-700 text-xs uppercase">İletişim Bilgileri</h5>
                        {hotel.phone1 && (
                          <div className="flex items-center gap-2 text-sm">
                            <Phone className="w-4 h-4 text-slate-400" />
                            <span className="text-slate-600">{hotel.phone1}</span>
                          </div>
                        )}
                        {hotel.phone2 && (
                          <div className="flex items-center gap-2 text-sm">
                            <Phone className="w-4 h-4 text-slate-400" />
                            <span className="text-slate-600">{hotel.phone2}</span>
                          </div>
                        )}
                        {hotel.email && (
                          <div className="flex items-center gap-2 text-sm">
                            <Mail className="w-4 h-4 text-slate-400" />
                            <span className="text-slate-600">{hotel.email}</span>
                          </div>
                        )}
                        {hotel.website && (
                          <div className="flex items-center gap-2 text-sm">
                            <Globe className="w-4 h-4 text-slate-400" />
                            <a href={hotel.website} target="_blank" rel="noopener noreferrer" className="text-cyan-600 hover:underline">
                              Web Sitesi
                            </a>
                          </div>
                        )}
                      </div>

                      {/* Address Info */}
                      <div className="space-y-2">
                        <h5 className="font-semibold text-slate-700 text-xs uppercase">Adres Bilgileri</h5>
                        {hotel.address && (
                          <p className="text-sm text-slate-600">{hotel.address}</p>
                        )}
                        {hotel.city && (
                          <p className="text-sm text-slate-600">{hotel.city}, {hotel.country || 'N/A'}</p>
                        )}
                        {hotel.postal_code && (
                          <p className="text-sm text-slate-600">Posta Kodu: {hotel.postal_code}</p>
                        )}
                      </div>

                      {/* Additional Info */}
                      <div className="space-y-2">
                        <h5 className="font-semibold text-slate-700 text-xs uppercase">Diğer Bilgiler</h5>
                        <p className="text-sm text-slate-600">Transfer Bölgesi: {hotel.transfer_region || 'N/A'}</p>
                        <p className="text-sm text-slate-600">Servis Türü: {hotel.service_type}</p>
                        {hotel.manager && (
                          <p className="text-sm text-slate-600">Yönetici: {hotel.manager}</p>
                        )}
                        {hotel.notes && (
                          <p className="text-sm text-slate-600 mt-2 italic">Not: {hotel.notes}</p>
                        )}
                      </div>
                    </div>

                    {/* Actions (if has permission) */}
                    {hasPermission('hotels', 'update') && (
                      <div className="mt-4 pt-4 border-t border-slate-200 flex gap-2">
                        <Button 
                          size="sm" 
                          variant="outline"
                          className="text-cyan-600 border-cyan-300 hover:bg-cyan-50"
                        >
                          <Edit className="w-4 h-4 mr-2" />
                          Düzenle
                        </Button>
                        {hasPermission('hotels', 'delete') && (
                          <Button 
                            size="sm" 
                            variant="outline"
                            className="text-red-600 border-red-300 hover:bg-red-50"
                          >
                            <Trash2 className="w-4 h-4 mr-2" />
                            Sil
                          </Button>
                        )}
                      </div>
                    )}
                  </div>
                )}
              </div>
            ))}
          </div>
        )}

        {/* Pagination Info */}
        {filteredHotels.length > 0 && (
          <div className="mt-6 text-center text-sm text-slate-600">
            Toplam {filteredHotels.length} otel gösteriliyor
          </div>
        )}
      </div>
    </div>
  );
};

export default Hotels;
