import React, { useState, useEffect } from 'react';
import { X, MapPin, Hotel, Calendar, Clock, CheckCircle, Circle, ArrowRight } from 'lucide-react';
import api from '@/utils/api';

const JourneyTimeline = ({ reservationId, isOpen, onClose }) => {
  const [loading, setLoading] = useState(false);
  const [journeyData, setJourneyData] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (isOpen && reservationId) {
      fetchJourneyData();
    }
  }, [isOpen, reservationId]);

  const fetchJourneyData = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await api.get(`/reservations/${reservationId}/journey`);
      setJourneyData(response.data);
    } catch (err) {
      console.error('Error fetching journey:', err);
      setError('Yolcu yolculuğu yüklenemedi');
    } finally {
      setLoading(false);
    }
  };

  const getStatusBadge = (status) => {
    const statusStyles = {
      completed: { bg: 'bg-green-500', text: 'text-white', label: 'Tamamlandı' },
      in_progress: { bg: 'bg-blue-500', text: 'text-white', label: 'Devam Ediyor' },
      pending: { bg: 'bg-gray-400', text: 'text-white', label: 'Bekliyor' },
      confirmed: { bg: 'bg-green-500', text: 'text-white', label: 'Onaylandı' }
    };
    return statusStyles[status] || statusStyles.pending;
  };

  const getLegIcon = (legType) => {
    switch(legType) {
      case 'hotel':
      case 'accommodation':
        return <Hotel className="w-6 h-6" />;
      case 'transfer':
        return <ArrowRight className="w-6 h-6" />;
      case 'airport_pickup':
      case 'airport_dropoff':
        return <MapPin className="w-6 h-6" />;
      default:
        return <Circle className="w-6 h-6" />;
    }
  };

  const getLegTypeLabel = (legType) => {
    const labels = {
      hotel: 'Otel Konaklaması',
      accommodation: 'Konaklama',
      transfer: 'Transfer',
      airport_pickup: 'Havalimanı Karşılama',
      airport_dropoff: 'Havalimanı Uğurlama'
    };
    return labels[legType] || legType;
  };

  if (!isOpen) return null;

  return (
    <div 
      className="fixed inset-0 z-50 flex items-center justify-center p-4"
      style={{ backgroundColor: 'rgba(0, 0, 0, 0.75)' }}
      onClick={onClose}
    >
      <div 
        className="bg-white rounded-2xl shadow-2xl w-full max-w-4xl max-h-[90vh] flex flex-col"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="bg-gradient-to-r from-indigo-600 to-purple-600 text-white px-8 py-6 rounded-t-2xl flex items-center justify-between">
          <div>
            <h2 className="text-2xl font-bold">Yolcu Yolculuk Planı</h2>
            {journeyData?.reservation && (
              <p className="text-sm text-indigo-100 mt-1">
                {journeyData.reservation.leader_name} - Voucher: {journeyData.reservation.voucherNo}
              </p>
            )}
          </div>
          <button
            onClick={onClose}
            className="hover:bg-white/20 rounded-full p-2 transition-colors"
          >
            <X className="w-7 h-7" />
          </button>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-auto p-8">
          {loading && (
            <div className="flex items-center justify-center py-12">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
            </div>
          )}

          {error && (
            <div className="bg-red-50 border border-red-200 rounded-lg p-4 text-red-700">
              {error}
            </div>
          )}

          {journeyData && !loading && (
            <div>
              {/* Package Info */}
              {journeyData.package && (
                <div className="bg-gradient-to-r from-indigo-50 to-purple-50 border border-indigo-200 rounded-xl p-6 mb-8">
                  <div className="flex items-center justify-between">
                    <div>
                      <h3 className="text-xl font-bold text-indigo-900">
                        Paket: {journeyData.package.package_code}
                      </h3>
                      <p className="text-indigo-700 mt-1">{journeyData.package.name}</p>
                      {journeyData.package.description && (
                        <p className="text-sm text-indigo-600 mt-2">{journeyData.package.description}</p>
                      )}
                    </div>
                    <div className="text-right">
                      <div className="text-3xl font-bold text-indigo-600">
                        {journeyData.package.total_nights}
                      </div>
                      <div className="text-sm text-indigo-700">Gece</div>
                    </div>
                  </div>
                </div>
              )}

              {/* Reservation Details */}
              <div className="bg-slate-50 rounded-lg p-6 mb-8">
                <h4 className="font-semibold text-slate-800 mb-4">Rezervasyon Bilgileri</h4>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  <div>
                    <p className="text-sm text-slate-600">Yolcu Sayısı</p>
                    <p className="font-semibold text-slate-800">{journeyData.reservation.pax} Kişi</p>
                  </div>
                  <div>
                    <p className="text-sm text-slate-600">Kaynak Acenta</p>
                    <p className="font-semibold text-slate-800">{journeyData.reservation.source_agency}</p>
                  </div>
                  <div>
                    <p className="text-sm text-slate-600">Durum</p>
                    <p className="font-semibold text-slate-800 capitalize">{journeyData.reservation.status}</p>
                  </div>
                  <div>
                    <p className="text-sm text-slate-600">Ürün Kodu</p>
                    <p className="font-semibold text-slate-800">{journeyData.reservation.product_code}</p>
                  </div>
                </div>
              </div>

              {/* Journey Timeline */}
              <div>
                <h4 className="font-semibold text-slate-800 mb-6 text-lg">Yolculuk Zaman Çizelgesi</h4>
                
                <div className="relative">
                  {/* Timeline Line */}
                  <div className="absolute left-8 top-0 bottom-0 w-1 bg-gradient-to-b from-indigo-200 via-purple-200 to-indigo-200"></div>
                  
                  {/* Timeline Items */}
                  <div className="space-y-6">
                    {journeyData.journey.map((leg, index) => {
                      const statusStyle = getStatusBadge(leg.status);
                      
                      return (
                        <div key={index} className="relative pl-20">
                          {/* Step Number Circle */}
                          <div className="absolute left-0 flex items-center justify-center">
                            <div className={`w-16 h-16 rounded-full ${statusStyle.bg} ${statusStyle.text} flex flex-col items-center justify-center shadow-lg`}>
                              <div className="text-xs font-medium">Adım</div>
                              <div className="text-xl font-bold">{leg.step_number}</div>
                            </div>
                          </div>

                          {/* Leg Card */}
                          <div className="bg-white border-2 border-slate-200 rounded-xl p-5 shadow-md hover:shadow-lg transition-shadow">
                            <div className="flex items-start justify-between mb-3">
                              <div className="flex items-center gap-3">
                                <div className={`${statusStyle.bg} ${statusStyle.text} p-2 rounded-lg`}>
                                  {getLegIcon(leg.leg_type)}
                                </div>
                                <div>
                                  <h5 className="font-bold text-slate-900 text-lg">
                                    {getLegTypeLabel(leg.leg_type)}
                                  </h5>
                                  <p className="text-sm text-slate-600">{leg.location}</p>
                                </div>
                              </div>
                              <span className={`px-3 py-1 rounded-full text-xs font-semibold ${statusStyle.bg} ${statusStyle.text}`}>
                                {statusStyle.label}
                              </span>
                            </div>

                            {/* Leg Details */}
                            <div className="space-y-2">
                              {leg.hotel_name && (
                                <div className="flex items-center gap-2 text-slate-700">
                                  <Hotel className="w-4 h-4 text-slate-500" />
                                  <span className="font-medium">{leg.hotel_name}</span>
                                  {leg.hotel_stars && (
                                    <span className="text-yellow-500 ml-1">{'⭐'.repeat(leg.hotel_stars)}</span>
                                  )}
                                </div>
                              )}
                              
                              {leg.check_in_date && (
                                <div className="flex items-center gap-2 text-slate-600">
                                  <Calendar className="w-4 h-4 text-slate-500" />
                                  <span>Giriş: <strong>{leg.check_in_date}</strong></span>
                                  {leg.check_out_date && (
                                    <span className="ml-4">
                                      Çıkış: <strong>{leg.check_out_date}</strong>
                                    </span>
                                  )}
                                </div>
                              )}

                              {leg.duration_nights > 0 && (
                                <div className="flex items-center gap-2 text-slate-600">
                                  <Clock className="w-4 h-4 text-slate-500" />
                                  <span>{leg.duration_nights} Gece Konaklama</span>
                                </div>
                              )}

                              {(leg.room_type || leg.board_type) && (
                                <div className="flex items-center gap-4 text-sm text-slate-600 mt-2">
                                  {leg.room_type && (
                                    <span className="bg-slate-100 px-3 py-1 rounded-full">
                                      Oda: {leg.room_type}
                                    </span>
                                  )}
                                  {leg.board_type && (
                                    <span className="bg-slate-100 px-3 py-1 rounded-full">
                                      Pansiyon: {leg.board_type}
                                    </span>
                                  )}
                                </div>
                              )}

                              {leg.notes && (
                                <div className="mt-3 p-3 bg-yellow-50 border border-yellow-200 rounded-lg">
                                  <p className="text-sm text-yellow-800">
                                    <strong>Not:</strong> {leg.notes}
                                  </p>
                                </div>
                              )}
                            </div>
                          </div>
                        </div>
                      );
                    })}
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="border-t border-slate-200 px-8 py-4 bg-slate-50 rounded-b-2xl">
          <button
            onClick={onClose}
            className="px-6 py-2 bg-slate-600 hover:bg-slate-700 text-white rounded-lg transition-colors font-medium"
          >
            Kapat
          </button>
        </div>
      </div>
    </div>
  );
};

export default JourneyTimeline;
