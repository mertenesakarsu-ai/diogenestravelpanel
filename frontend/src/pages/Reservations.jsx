import React, { useState } from "react";
import { Search, Filter, Users, Calendar, Hotel } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { mockReservations } from "@/lib/mockReservationData";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";

const Reservations = () => {
  const [searchTerm, setSearchTerm] = useState("");
  const [filterStatus, setFilterStatus] = useState("all");

  const filteredReservations = mockReservations.filter(reservation => {
    const matchesSearch = 
      reservation.voucherNo.toLowerCase().includes(searchTerm.toLowerCase()) ||
      reservation.leader.name.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesStatus = filterStatus === "all" || reservation.status === filterStatus;
    return matchesSearch && matchesStatus;
  });

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
              <p className="text-3xl font-bold text-slate-800">{mockReservations.length}</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-xl p-6 border border-slate-200 shadow-sm">
          <div className="flex items-center gap-4">
            <div className="w-14 h-14 rounded-xl bg-gradient-to-br from-green-500 to-green-600 flex items-center justify-center shadow-lg">
              <Users className="w-7 h-7 text-white" />
            </div>
            <div>
              <p className="text-sm text-slate-500">Onaylı</p>
              <p className="text-3xl font-bold text-slate-800">
                {mockReservations.filter(r => r.status === 'confirmed').length}
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
              <p className="text-sm text-slate-500">Bekleyen</p>
              <p className="text-3xl font-bold text-slate-800">
                {mockReservations.filter(r => r.status === 'pending').length}
              </p>
            </div>
          </div>
        </div>
      </div>

      <div className="bg-white rounded-2xl border border-slate-200 shadow-lg p-6">
        <div className="flex flex-col lg:flex-row gap-4 items-start lg:items-center justify-between mb-6">
          <h3 className="text-lg font-bold text-slate-800">Rezervasyon Listesi</h3>
          
          <div className="flex flex-col sm:flex-row gap-3 w-full lg:w-auto">
            <div className="relative flex-1 lg:w-64">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
              <Input
                placeholder="Voucher veya isim ara..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10"
                data-testid="reservation-search"
              />
            </div>
            
            <Select value={filterStatus} onValueChange={setFilterStatus}>
              <SelectTrigger className="w-full sm:w-48" data-testid="status-filter">
                <Filter className="w-4 h-4 mr-2" />
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">Tüm Rezervasyonlar</SelectItem>
                <SelectItem value="confirmed">Onaylı</SelectItem>
                <SelectItem value="pending">Bekleyen</SelectItem>
              </SelectContent>
            </Select>
          </div>
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