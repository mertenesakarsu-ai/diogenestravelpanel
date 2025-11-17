import React, { useState } from "react";
import { Database, Users, FileText, Settings, CheckCircle, XCircle, Activity } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";

const Admin = () => {
  const [dbStatus] = useState({
    postgresql: { connected: false, records: 0 },
    mongodb: { connected: true, records: 1247 }
  });

  const mockUsers = [
    { id: 1, name: "Admin User", email: "admin@diogenes.com", role: "admin", status: "active" },
    { id: 2, name: "Rezervasyon Manager", email: "reservation@diogenes.com", role: "reservation", status: "active" },
    { id: 3, name: "Operasyon Manager", email: "operation@diogenes.com", role: "operation", status: "active" },
    { id: 4, name: "Uçak Manager", email: "flight@diogenes.com", role: "flight", status: "active" },
  ];

  const mockLogs = [
    { id: 1, user: "admin@diogenes.com", action: "CREATE", entity: "reservations", entityId: "DG2024-005", time: "2024-12-15 14:30" },
    { id: 2, user: "operation@diogenes.com", action: "UPDATE", entity: "flights", entityId: "TK1234", time: "2024-12-15 13:15" },
    { id: 3, user: "flight@diogenes.com", action: "IMPORT_EXCEL", entity: "flights", entityId: "batch_001", time: "2024-12-15 11:45" },
    { id: 4, user: "reservation@diogenes.com", action: "UPDATE", entity: "reservations", entityId: "DG2024-003", time: "2024-12-15 10:20" },
  ];

  return (
    <div className="space-y-6" data-testid="admin-page">
      {/* Database Status */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-2xl border border-slate-200 shadow-lg p-6">
          <div className="flex items-center gap-3 mb-6">
            <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-red-500 to-red-600 flex items-center justify-center shadow-lg">
              <Database className="w-6 h-6 text-white" />
            </div>
            <div>
              <h3 className="text-lg font-bold text-slate-800">PostgreSQL</h3>
              <p className="text-sm text-slate-500">İlişkisel Veritabanı</p>
            </div>
          </div>
          
          <div className="flex items-center justify-between mb-4">
            <span className="text-slate-600">Bağlantı Durumu</span>
            <div className="flex items-center gap-2">
              <XCircle className="w-5 h-5 text-red-500" />
              <span className="font-semibold text-red-600">Bağlı Değil</span>
            </div>
          </div>

          <div className="p-4 bg-red-50 border border-red-200 rounded-lg">
            <p className="text-sm text-red-700">
              PostgreSQL desteği henüz mevcut değil. Veritabanı entegrasyonu beklemede.
            </p>
          </div>
        </div>

        <div className="bg-white rounded-2xl border border-slate-200 shadow-lg p-6">
          <div className="flex items-center gap-3 mb-6">
            <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-green-500 to-green-600 flex items-center justify-center shadow-lg">
              <Database className="w-6 h-6 text-white" />
            </div>
            <div>
              <h3 className="text-lg font-bold text-slate-800">MongoDB</h3>
              <p className="text-sm text-slate-500">Doküman Veritabanı</p>
            </div>
          </div>
          
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <span className="text-slate-600">Bağlantı Durumu</span>
              <div className="flex items-center gap-2">
                <CheckCircle className="w-5 h-5 text-green-500" />
                <span className="font-semibold text-green-600">Bağlı</span>
              </div>
            </div>

            <div className="flex items-center justify-between">
              <span className="text-slate-600">Toplam Kayıt</span>
              <span className="font-bold text-slate-800">{dbStatus.mongodb.records}</span>
            </div>
          </div>

          <div className="mt-4 p-4 bg-green-50 border border-green-200 rounded-lg">
            <p className="text-sm text-green-700">
              Sistem şu anda MongoDB ile çalışıyor. Log kayıtları için kullanılıyor.
            </p>
          </div>
        </div>
      </div>

      {/* Admin Tabs */}
      <div className="bg-white rounded-2xl border border-slate-200 shadow-lg p-6">
        <Tabs defaultValue="users" className="w-full">
          <TabsList className="grid w-full max-w-2xl grid-cols-3 mb-6">
            <TabsTrigger value="users" data-testid="users-tab">
              <Users className="w-4 h-4 mr-2" />
              Kullanıcılar
            </TabsTrigger>
            <TabsTrigger value="logs" data-testid="logs-tab">
              <FileText className="w-4 h-4 mr-2" />
              Loglar
            </TabsTrigger>
            <TabsTrigger value="settings" data-testid="settings-tab">
              <Settings className="w-4 h-4 mr-2" />
              Ayarlar
            </TabsTrigger>
          </TabsList>

          {/* Users Tab */}
          <TabsContent value="users" className="space-y-4">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-lg font-bold text-slate-800">Kullanıcı Yönetimi</h3>
              <Button className="bg-gradient-to-r from-cyan-500 to-teal-500 hover:from-cyan-600 hover:to-teal-600 text-white">
                Yeni Kullanıcı Ekle
              </Button>
            </div>

            <div className="overflow-x-auto">
              <table className="w-full" data-testid="users-table">
                <thead className="bg-slate-50 border-b border-slate-200">
                  <tr>
                    <th className="px-6 py-4 text-left text-xs font-semibold text-slate-600 uppercase">Ad Soyad</th>
                    <th className="px-6 py-4 text-left text-xs font-semibold text-slate-600 uppercase">Email</th>
                    <th className="px-6 py-4 text-left text-xs font-semibold text-slate-600 uppercase">Rol</th>
                    <th className="px-6 py-4 text-left text-xs font-semibold text-slate-600 uppercase">Durum</th>
                    <th className="px-6 py-4 text-left text-xs font-semibold text-slate-600 uppercase"></th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {mockUsers.map((user) => (
                    <tr key={user.id} className="hover:bg-slate-50 transition-colors">
                      <td className="px-6 py-4">
                        <span className="font-semibold text-slate-800">{user.name}</span>
                      </td>
                      <td className="px-6 py-4 text-slate-700">{user.email}</td>
                      <td className="px-6 py-4">
                        <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                          {user.role}
                        </span>
                      </td>
                      <td className="px-6 py-4">
                        <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                          Aktif
                        </span>
                      </td>
                      <td className="px-6 py-4">
                        <Button variant="ghost" size="sm">Düzenle</Button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </TabsContent>

          {/* Logs Tab */}
          <TabsContent value="logs" className="space-y-4">
            <h3 className="text-lg font-bold text-slate-800 mb-4">Sistem Logları</h3>
            
            <div className="space-y-3">
              {mockLogs.map((log) => (
                <div 
                  key={log.id} 
                  className="p-4 border border-slate-200 rounded-lg hover:bg-slate-50 transition-colors"
                  data-testid={`log-entry-${log.id}`}
                >
                  <div className="flex items-start justify-between">
                    <div className="flex items-start gap-4">
                      <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-purple-500 to-purple-600 flex items-center justify-center flex-shrink-0">
                        <Activity className="w-5 h-5 text-white" />
                      </div>
                      <div>
                        <div className="flex items-center gap-2 mb-1">
                          <span className={`px-2 py-0.5 rounded text-xs font-semibold ${
                            log.action === 'CREATE' ? 'bg-green-100 text-green-800' :
                            log.action === 'UPDATE' ? 'bg-blue-100 text-blue-800' :
                            'bg-purple-100 text-purple-800'
                          }`}>
                            {log.action}
                          </span>
                          <span className="text-sm text-slate-600">{log.entity}</span>
                        </div>
                        <p className="text-sm text-slate-700">
                          <strong>{log.user}</strong> - {log.entityId}
                        </p>
                      </div>
                    </div>
                    <span className="text-sm text-slate-500">{log.time}</span>
                  </div>
                </div>
              ))}
            </div>
          </TabsContent>

          {/* Settings Tab */}
          <TabsContent value="settings" className="space-y-6">
            <h3 className="text-lg font-bold text-slate-800 mb-4">Sistem Ayarları</h3>
            
            <div className="space-y-6">
              <div className="space-y-3">
                <Label htmlFor="timezone">Saat Dilimi</Label>
                <Input id="timezone" value="Europe/Istanbul" readOnly />
              </div>

              <div className="space-y-3">
                <Label htmlFor="date-format">Tarih Formatı</Label>
                <Input id="date-format" value="YYYY-MM-DD" readOnly />
              </div>

              <div className="space-y-3">
                <Label htmlFor="flight-warning">Uçuş Uyarı Eşiği (Gün)</Label>
                <Input id="flight-warning" type="number" defaultValue="7" />
              </div>

              <div className="space-y-3">
                <Label htmlFor="backup-path">Yedekleme Yolu</Label>
                <Input id="backup-path" value="/var/backups/diogenes/" readOnly />
              </div>

              <Button className="bg-gradient-to-r from-cyan-500 to-teal-500 hover:from-cyan-600 hover:to-teal-600 text-white">
                Ayarları Kaydet
              </Button>
            </div>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
};

export default Admin;
