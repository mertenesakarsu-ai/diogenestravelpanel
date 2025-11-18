import React, { useState, useEffect } from 'react';
import { Package, Plus, Edit, Trash2, Save, X, Hotel, MapPin, ArrowRight } from 'lucide-react';
import { Button } from "@/components/ui/button";
import api from '@/utils/api';

const PackageManagement = () => {
  const [packages, setPackages] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [editingPackage, setEditingPackage] = useState(null);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);

  const [packageForm, setPackageForm] = useState({
    package_code: '',
    name: '',
    description: '',
    total_nights: 0,
    is_active: true,
    legs: []
  });

  const [legForm, setLegForm] = useState({
    step_number: 1,
    leg_type: 'hotel',
    location: '',
    hotel_name: '',
    hotel_stars: 5,
    duration_nights: 1,
    room_type: '',
    board_type: '',
    notes: ''
  });

  useEffect(() => {
    fetchPackages();
  }, []);

  const fetchPackages = async () => {
    try {
      setLoading(true);
      const response = await api.get('/packages');
      setPackages(response.data);
    } catch (err) {
      console.error('Error fetching packages:', err);
      setError('Paketler yüklenemedi');
    } finally {
      setLoading(false);
    }
  };

  const handleOpenModal = (pkg = null) => {
    if (pkg) {
      setEditingPackage(pkg);
      setPackageForm({
        package_code: pkg.package_code,
        name: pkg.name,
        description: pkg.description || '',
        total_nights: pkg.total_nights,
        is_active: pkg.is_active,
        legs: pkg.legs || []
      });
    } else {
      setEditingPackage(null);
      setPackageForm({
        package_code: '',
        name: '',
        description: '',
        total_nights: 0,
        is_active: true,
        legs: []
      });
    }
    setShowModal(true);
    setError(null);
    setSuccess(null);
  };

  const handleCloseModal = () => {
    setShowModal(false);
    setEditingPackage(null);
    setPackageForm({
      package_code: '',
      name: '',
      description: '',
      total_nights: 0,
      is_active: true,
      legs: []
    });
    setLegForm({
      step_number: 1,
      leg_type: 'hotel',
      location: '',
      hotel_name: '',
      hotel_stars: 5,
      duration_nights: 1,
      room_type: '',
      board_type: '',
      notes: ''
    });
  };

  const handleAddLeg = () => {
    const newLeg = {
      ...legForm,
      step_number: packageForm.legs.length + 1
    };
    setPackageForm({
      ...packageForm,
      legs: [...packageForm.legs, newLeg],
      total_nights: packageForm.total_nights + (legForm.leg_type === 'hotel' ? legForm.duration_nights : 0)
    });
    // Reset leg form
    setLegForm({
      step_number: packageForm.legs.length + 2,
      leg_type: 'hotel',
      location: '',
      hotel_name: '',
      hotel_stars: 5,
      duration_nights: 1,
      room_type: '',
      board_type: '',
      notes: ''
    });
  };

  const handleRemoveLeg = (index) => {
    const removedLeg = packageForm.legs[index];
    const updatedLegs = packageForm.legs.filter((_, i) => i !== index);
    // Renumber steps
    const renumberedLegs = updatedLegs.map((leg, i) => ({
      ...leg,
      step_number: i + 1
    }));
    
    const nightsReduction = removedLeg.leg_type === 'hotel' ? removedLeg.duration_nights : 0;
    
    setPackageForm({
      ...packageForm,
      legs: renumberedLegs,
      total_nights: Math.max(0, packageForm.total_nights - nightsReduction)
    });
  };

  const handleSavePackage = async () => {
    try {
      setError(null);
      setSuccess(null);

      if (!packageForm.package_code || !packageForm.name) {
        setError('Paket kodu ve adı zorunludur');
        return;
      }

      if (packageForm.legs.length === 0) {
        setError('En az bir adım (leg) eklemelisiniz');
        return;
      }

      if (editingPackage) {
        // Update existing package
        await api.put(`/packages/${editingPackage.id}`, packageForm);
        setSuccess('Paket başarıyla güncellendi');
      } else {
        // Create new package
        await api.post('/packages', packageForm);
        setSuccess('Paket başarıyla oluşturuldu');
      }

      setTimeout(() => {
        handleCloseModal();
        fetchPackages();
      }, 1500);
    } catch (err) {
      console.error('Error saving package:', err);
      setError(err.response?.data?.detail || 'Paket kaydedilemedi');
    }
  };

  const handleDeletePackage = async (packageId) => {
    if (!window.confirm('Bu paketi silmek istediğinizden emin misiniz?')) {
      return;
    }

    try {
      await api.delete(`/packages/${packageId}`);
      setSuccess('Paket başarıyla silindi');
      fetchPackages();
      setTimeout(() => setSuccess(null), 3000);
    } catch (err) {
      console.error('Error deleting package:', err);
      setError('Paket silinemedi');
      setTimeout(() => setError(null), 3000);
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

  const getLegTypeIcon = (legType) => {
    switch(legType) {
      case 'hotel':
      case 'accommodation':
        return <Hotel className="w-4 h-4" />;
      case 'transfer':
        return <ArrowRight className="w-4 h-4" />;
      case 'airport_pickup':
      case 'airport_dropoff':
        return <MapPin className="w-4 h-4" />;
      default:
        return <Package className="w-4 h-4" />;
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h3 className="text-lg font-bold text-slate-800">Paket Tur Yönetimi</h3>
          <p className="text-sm text-slate-600">Çok ayaklı paket turları oluşturun ve yönetin</p>
        </div>
        <Button onClick={() => handleOpenModal()} className="bg-gradient-to-r from-indigo-500 to-purple-600 hover:from-indigo-600 hover:to-purple-700">
          <Plus className="w-4 h-4 mr-2" />
          Yeni Paket Ekle
        </Button>
      </div>

      {/* Messages */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 text-red-700">
          {error}
        </div>
      )}
      {success && (
        <div className="bg-green-50 border border-green-200 rounded-lg p-4 text-green-700">
          {success}
        </div>
      )}

      {/* Packages List */}
      {loading ? (
        <div className="flex justify-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
        </div>
      ) : packages.length === 0 ? (
        <div className="bg-slate-50 border border-slate-200 rounded-lg p-12 text-center">
          <Package className="w-16 h-16 text-slate-400 mx-auto mb-4" />
          <p className="text-slate-600">Henüz hiç paket oluşturulmamış</p>
          <p className="text-sm text-slate-500 mt-1">Yeni bir paket eklemek için "Yeni Paket Ekle" butonuna tıklayın</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {packages.map((pkg) => (
            <div key={pkg.id} className="bg-white border border-slate-200 rounded-xl p-6 shadow-sm hover:shadow-md transition-shadow">
              <div className="flex justify-between items-start mb-4">
                <div>
                  <div className="flex items-center gap-2 mb-1">
                    <span className="px-3 py-1 bg-indigo-100 text-indigo-700 rounded-full text-sm font-bold">
                      {pkg.package_code}
                    </span>
                    {pkg.is_active ? (
                      <span className="px-2 py-0.5 bg-green-100 text-green-700 rounded text-xs font-medium">
                        Aktif
                      </span>
                    ) : (
                      <span className="px-2 py-0.5 bg-gray-100 text-gray-700 rounded text-xs font-medium">
                        Pasif
                      </span>
                    )}
                  </div>
                  <h4 className="text-lg font-bold text-slate-800">{pkg.name}</h4>
                  {pkg.description && (
                    <p className="text-sm text-slate-600 mt-1">{pkg.description}</p>
                  )}
                </div>
                <div className="flex gap-2">
                  <button
                    onClick={() => handleOpenModal(pkg)}
                    className="p-2 hover:bg-slate-100 rounded-lg transition-colors"
                    title="Düzenle"
                  >
                    <Edit className="w-4 h-4 text-slate-600" />
                  </button>
                  <button
                    onClick={() => handleDeletePackage(pkg.id)}
                    className="p-2 hover:bg-red-50 rounded-lg transition-colors"
                    title="Sil"
                  >
                    <Trash2 className="w-4 h-4 text-red-600" />
                  </button>
                </div>
              </div>

              {/* Package Stats */}
              <div className="grid grid-cols-2 gap-4 mb-4">
                <div className="bg-slate-50 rounded-lg p-3">
                  <p className="text-xs text-slate-600 mb-1">Toplam Gece</p>
                  <p className="text-2xl font-bold text-slate-800">{pkg.total_nights}</p>
                </div>
                <div className="bg-slate-50 rounded-lg p-3">
                  <p className="text-xs text-slate-600 mb-1">Adım Sayısı</p>
                  <p className="text-2xl font-bold text-slate-800">{pkg.legs?.length || 0}</p>
                </div>
              </div>

              {/* Legs Summary */}
              <div className="space-y-2">
                <p className="text-xs font-medium text-slate-600 mb-2">Rota Adımları:</p>
                {pkg.legs?.slice(0, 3).map((leg, index) => (
                  <div key={index} className="flex items-center gap-2 text-sm">
                    <span className="flex items-center justify-center w-6 h-6 rounded-full bg-indigo-100 text-indigo-700 text-xs font-bold">
                      {leg.step_number}
                    </span>
                    <div className="flex items-center gap-2 text-slate-700">
                      {getLegTypeIcon(leg.leg_type)}
                      <span>{leg.location}</span>
                      {leg.hotel_name && <span className="text-slate-500">• {leg.hotel_name}</span>}
                    </div>
                  </div>
                ))}
                {pkg.legs?.length > 3 && (
                  <p className="text-xs text-slate-500 ml-8">+{pkg.legs.length - 3} adım daha...</p>
                )}
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Package Modal */}
      {showModal && (
        <div 
          className="fixed inset-0 z-50 flex items-center justify-center p-4"
          style={{ backgroundColor: 'rgba(0, 0, 0, 0.75)' }}
          onClick={handleCloseModal}
        >
          <div 
            className="bg-white rounded-2xl shadow-2xl w-full max-w-4xl max-h-[90vh] flex flex-col"
            onClick={(e) => e.stopPropagation()}
          >
            {/* Modal Header */}
            <div className="bg-gradient-to-r from-indigo-600 to-purple-600 text-white px-6 py-4 rounded-t-2xl flex items-center justify-between">
              <h3 className="text-xl font-bold">
                {editingPackage ? 'Paket Düzenle' : 'Yeni Paket Oluştur'}
              </h3>
              <button onClick={handleCloseModal} className="hover:bg-white/20 rounded-full p-2">
                <X className="w-6 h-6" />
              </button>
            </div>

            {/* Modal Content */}
            <div className="flex-1 overflow-auto p-6 space-y-6">
              {/* Package Info */}
              <div className="space-y-4">
                <h4 className="font-semibold text-slate-800">Paket Bilgileri</h4>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-slate-700 mb-1">Paket Kodu *</label>
                    <input
                      type="text"
                      value={packageForm.package_code}
                      onChange={(e) => setPackageForm({...packageForm, package_code: e.target.value.toUpperCase()})}
                      placeholder="EISK7"
                      className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-slate-700 mb-1">Paket Adı *</label>
                    <input
                      type="text"
                      value={packageForm.name}
                      onChange={(e) => setPackageForm({...packageForm, name: e.target.value})}
                      placeholder="Istanbul-Cappadocia 7 Days Tour"
                      className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
                    />
                  </div>
                </div>
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-1">Açıklama</label>
                  <textarea
                    value={packageForm.description}
                    onChange={(e) => setPackageForm({...packageForm, description: e.target.value})}
                    placeholder="Paket açıklaması..."
                    rows={2}
                    className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
                  />
                </div>
                <div className="flex items-center gap-3">
                  <input
                    type="checkbox"
                    id="is_active"
                    checked={packageForm.is_active}
                    onChange={(e) => setPackageForm({...packageForm, is_active: e.target.checked})}
                    className="w-4 h-4 text-indigo-600 rounded"
                  />
                  <label htmlFor="is_active" className="text-sm font-medium text-slate-700">
                    Paket Aktif
                  </label>
                </div>
                <div className="bg-indigo-50 rounded-lg p-3">
                  <p className="text-sm text-indigo-700">
                    <strong>Toplam Gece:</strong> {packageForm.total_nights} gece
                  </p>
                </div>
              </div>

              {/* Legs */}
              <div className="space-y-4">
                <h4 className="font-semibold text-slate-800">Rota Adımları ({packageForm.legs.length})</h4>
                
                {/* Existing Legs */}
                {packageForm.legs.map((leg, index) => (
                  <div key={index} className="bg-slate-50 border border-slate-200 rounded-lg p-4">
                    <div className="flex justify-between items-start mb-2">
                      <div className="flex items-center gap-2">
                        <span className="flex items-center justify-center w-8 h-8 rounded-full bg-indigo-500 text-white text-sm font-bold">
                          {leg.step_number}
                        </span>
                        <div>
                          <p className="font-medium text-slate-800">{getLegTypeLabel(leg.leg_type)}</p>
                          <p className="text-sm text-slate-600">{leg.location}</p>
                        </div>
                      </div>
                      <button
                        onClick={() => handleRemoveLeg(index)}
                        className="p-1.5 hover:bg-red-50 rounded-lg transition-colors"
                      >
                        <Trash2 className="w-4 h-4 text-red-600" />
                      </button>
                    </div>
                    {leg.hotel_name && (
                      <p className="text-sm text-slate-600 ml-10">
                        <Hotel className="w-3 h-3 inline mr-1" />
                        {leg.hotel_name} {'⭐'.repeat(leg.hotel_stars || 0)}
                        {leg.duration_nights > 0 && ` • ${leg.duration_nights} gece`}
                      </p>
                    )}
                  </div>
                ))}

                {/* Add New Leg Form */}
                <div className="bg-gradient-to-br from-indigo-50 to-purple-50 border-2 border-dashed border-indigo-300 rounded-lg p-4 space-y-3">
                  <h5 className="font-medium text-indigo-900">Yeni Adım Ekle</h5>
                  
                  <div className="grid grid-cols-2 gap-3">
                    <div>
                      <label className="block text-xs font-medium text-slate-700 mb-1">Adım Tipi</label>
                      <select
                        value={legForm.leg_type}
                        onChange={(e) => setLegForm({...legForm, leg_type: e.target.value})}
                        className="w-full px-2 py-1.5 text-sm border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
                      >
                        <option value="hotel">Otel Konaklaması</option>
                        <option value="transfer">Transfer</option>
                        <option value="airport_pickup">Havalimanı Karşılama</option>
                        <option value="airport_dropoff">Havalimanı Uğurlama</option>
                      </select>
                    </div>
                    <div>
                      <label className="block text-xs font-medium text-slate-700 mb-1">Lokasyon</label>
                      <input
                        type="text"
                        value={legForm.location}
                        onChange={(e) => setLegForm({...legForm, location: e.target.value})}
                        placeholder="İstanbul"
                        className="w-full px-2 py-1.5 text-sm border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
                      />
                    </div>
                  </div>

                  {legForm.leg_type === 'hotel' && (
                    <>
                      <div className="grid grid-cols-2 gap-3">
                        <div>
                          <label className="block text-xs font-medium text-slate-700 mb-1">Otel Adı</label>
                          <input
                            type="text"
                            value={legForm.hotel_name}
                            onChange={(e) => setLegForm({...legForm, hotel_name: e.target.value})}
                            placeholder="Grand Hotel"
                            className="w-full px-2 py-1.5 text-sm border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
                          />
                        </div>
                        <div>
                          <label className="block text-xs font-medium text-slate-700 mb-1">Yıldız</label>
                          <select
                            value={legForm.hotel_stars}
                            onChange={(e) => setLegForm({...legForm, hotel_stars: parseInt(e.target.value)})}
                            className="w-full px-2 py-1.5 text-sm border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
                          >
                            {[3,4,5].map(stars => (
                              <option key={stars} value={stars}>{stars} Yıldız</option>
                            ))}
                          </select>
                        </div>
                      </div>
                      <div className="grid grid-cols-3 gap-3">
                        <div>
                          <label className="block text-xs font-medium text-slate-700 mb-1">Gece Sayısı</label>
                          <input
                            type="number"
                            value={legForm.duration_nights}
                            onChange={(e) => setLegForm({...legForm, duration_nights: parseInt(e.target.value)})}
                            min="1"
                            className="w-full px-2 py-1.5 text-sm border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
                          />
                        </div>
                        <div>
                          <label className="block text-xs font-medium text-slate-700 mb-1">Oda Tipi</label>
                          <input
                            type="text"
                            value={legForm.room_type}
                            onChange={(e) => setLegForm({...legForm, room_type: e.target.value})}
                            placeholder="Deluxe"
                            className="w-full px-2 py-1.5 text-sm border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
                          />
                        </div>
                        <div>
                          <label className="block text-xs font-medium text-slate-700 mb-1">Pansiyon</label>
                          <input
                            type="text"
                            value={legForm.board_type}
                            onChange={(e) => setLegForm({...legForm, board_type: e.target.value})}
                            placeholder="All Inclusive"
                            className="w-full px-2 py-1.5 text-sm border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
                          />
                        </div>
                      </div>
                    </>
                  )}

                  <div>
                    <label className="block text-xs font-medium text-slate-700 mb-1">Notlar</label>
                    <input
                      type="text"
                      value={legForm.notes}
                      onChange={(e) => setLegForm({...legForm, notes: e.target.value})}
                      placeholder="Ek bilgiler..."
                      className="w-full px-2 py-1.5 text-sm border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
                    />
                  </div>

                  <button
                    onClick={handleAddLeg}
                    disabled={!legForm.location}
                    className="w-full py-2 bg-indigo-600 hover:bg-indigo-700 disabled:bg-slate-300 text-white rounded-lg font-medium transition-colors"
                  >
                    <Plus className="w-4 h-4 inline mr-1" />
                    Adım Ekle
                  </button>
                </div>
              </div>

              {error && (
                <div className="bg-red-50 border border-red-200 rounded-lg p-3 text-red-700 text-sm">
                  {error}
                </div>
              )}
              {success && (
                <div className="bg-green-50 border border-green-200 rounded-lg p-3 text-green-700 text-sm">
                  {success}
                </div>
              )}
            </div>

            {/* Modal Footer */}
            <div className="border-t border-slate-200 px-6 py-4 bg-slate-50 rounded-b-2xl flex justify-end gap-3">
              <Button
                onClick={handleCloseModal}
                variant="outline"
                className="border-slate-300 hover:bg-slate-100"
              >
                İptal
              </Button>
              <Button
                onClick={handleSavePackage}
                className="bg-gradient-to-r from-indigo-500 to-purple-600 hover:from-indigo-600 hover:to-purple-700"
              >
                <Save className="w-4 h-4 mr-2" />
                {editingPackage ? 'Güncelle' : 'Oluştur'}
              </Button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default PackageManagement;
