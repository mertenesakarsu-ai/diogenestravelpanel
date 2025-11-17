import React from "react";
import { Calendar, Clock, MapPin, Users } from "lucide-react";

const Operations = () => {
  return (
    <div className="space-y-6" data-testid="operations-page">
      <div className="bg-white rounded-2xl border border-slate-200 shadow-lg p-6">
        <div className="flex items-center gap-4 mb-6">
          <div className="w-14 h-14 rounded-xl bg-gradient-to-br from-cyan-500 to-teal-500 flex items-center justify-center shadow-lg">
            <Calendar className="w-7 h-7 text-white" />
          </div>
          <div>
            <h2 className="text-2xl font-bold text-slate-800">Operasyon Yönetimi</h2>
            <p className="text-sm text-slate-500">Günlük operasyon takibi ve planlama</p>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <div className="bg-gradient-to-br from-blue-50 to-blue-100 rounded-xl p-6 border border-blue-200">
            <div className="flex items-center gap-3 mb-3">
              <Calendar className="w-6 h-6 text-blue-600" />
              <h3 className="font-bold text-blue-800">Bugünün Programı</h3>
            </div>
            <p className="text-3xl font-bold text-blue-900">8</p>
            <p className="text-sm text-blue-600 mt-1">Aktif Transfer</p>
          </div>

          <div className="bg-gradient-to-br from-green-50 to-green-100 rounded-xl p-6 border border-green-200">
            <div className="flex items-center gap-3 mb-3">
              <Users className="w-6 h-6 text-green-600" />
              <h3 className="font-bold text-green-800">Toplam Yolcu</h3>
            </div>
            <p className="text-3xl font-bold text-green-900">45</p>
            <p className="text-sm text-green-600 mt-1">Bugün</p>
          </div>

          <div className="bg-gradient-to-br from-orange-50 to-orange-100 rounded-xl p-6 border border-orange-200">
            <div className="flex items-center gap-3 mb-3">
              <MapPin className="w-6 h-6 text-orange-600" />
              <h3 className="font-bold text-orange-800">Aktif Lokasyon</h3>
            </div>
            <p className="text-3xl font-bold text-orange-900">12</p>
            <p className="text-sm text-orange-600 mt-1">Transfer Noktası</p>
          </div>

          <div className="bg-gradient-to-br from-purple-50 to-purple-100 rounded-xl p-6 border border-purple-200">
            <div className="flex items-center gap-3 mb-3">
              <Clock className="w-6 h-6 text-purple-600" />
              <h3 className="font-bold text-purple-800">Bekleyen</h3>
            </div>
            <p className="text-3xl font-bold text-purple-900">3</p>
            <p className="text-sm text-purple-600 mt-1">İşlem</p>
          </div>
        </div>

        <div className="mt-8">
          <h3 className="text-lg font-bold text-slate-800 mb-4">Günlük Operasyon Detayları</h3>
          <p className="text-slate-600">Operasyon detayları burada gösterilecek...</p>
        </div>
      </div>
    </div>
  );
};

export default Operations;