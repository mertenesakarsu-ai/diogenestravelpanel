import React, { useState } from "react";
import { Database, Users, FileText, Settings, CheckCircle, XCircle, Activity, Upload, FileSpreadsheet, AlertCircle } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import api from "@/utils/api";
import { useAuth } from "@/context/AuthContext";

const Admin = () => {
  const { hasPermission } = useAuth();
  const [dbStatus] = useState({
    postgresql: { connected: false, records: 0 },
    mongodb: { connected: true, records: 1247 }
  });

  const [uploadFile, setUploadFile] = useState(null);
  const [uploadType, setUploadType] = useState("flights");
  const [uploadProgress, setUploadProgress] = useState(null);
  const [uploadError, setUploadError] = useState(null);

  const [users, setUsers] = useState([]);
  const [loadingUsers, setLoadingUsers] = useState(true);

  const mockLogs = [
    { id: 1, user: "admin@diogenestravel.com", action: "CREATE", entity: "reservations", entityId: "DG2024-005", time: "2024-12-15 14:30" },
    { id: 2, user: "operation@diogenestravel.com", action: "UPDATE", entity: "flights", entityId: "TK1234", time: "2024-12-15 13:15" },
    { id: 3, user: "flight@diogenestravel.com", action: "IMPORT_EXCEL", entity: "flights", entityId: "batch_001", time: "2024-12-15 11:45" },
    { id: 4, user: "reservation@diogenestravel.com", action: "UPDATE", entity: "reservations", entityId: "DG2024-003", time: "2024-12-15 10:20" },
  ];
  
  // User management state
  const [showUserModal, setShowUserModal] = useState(false);
  const [editingUser, setEditingUser] = useState(null);
  const [userForm, setUserForm] = useState({
    name: '',
    email: '',
    password: '',
    role: 'reservation',
    status: 'active'
  });

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      setUploadFile(file);
      setUploadError(null);
      setUploadProgress(null);
    }
  };

  const handleUpload = async () => {
    if (!uploadFile) {
      setUploadError("Lütfen bir dosya seçin");
      return;
    }

    // Check permission
    if (!hasPermission(uploadType, 'upload')) {
      setUploadError(`${uploadType} verilerini yükleme yetkiniz yok`);
      return;
    }

    const formData = new FormData();
    formData.append("file", uploadFile);

    try {
      setUploadProgress("Yükleniyor...");
      setUploadError(null);

      const response = await api.post(
        `/api/${uploadType}/upload`,
        formData,
        {
          headers: {
            "Content-Type": "multipart/form-data",
          },
        }
      );

      setUploadProgress(`Başarıyla yüklendi! ${response.data.count} kayıt eklendi.`);
      setUploadFile(null);
      
      // Reset file input
      const fileInput = document.getElementById("file-upload");
      if (fileInput) fileInput.value = "";
      
    } catch (error) {
      setUploadError(error.response?.data?.detail || "Yükleme başarısız oldu");
      setUploadProgress(null);
    }
  };

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
          <TabsList className="grid w-full max-w-3xl grid-cols-4 mb-6">
            <TabsTrigger value="users" data-testid="users-tab">
              <Users className="w-4 h-4 mr-2" />
              Kullanıcılar
            </TabsTrigger>
            <TabsTrigger value="upload" data-testid="upload-tab">
              <Upload className="w-4 h-4 mr-2" />
              Veri Yükleme
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

          {/* Upload Tab */}
          <TabsContent value="upload" className="space-y-6">
            <div className="space-y-6">
              <div>
                <h3 className="text-lg font-bold text-slate-800 mb-2">Veri Seti Yükleme</h3>
                <p className="text-sm text-slate-600">Excel dosyalarını (.xlsx, .xls) sisteme yükleyin</p>
              </div>

              {/* Upload Type Selection */}
              <div className="space-y-3">
                <Label htmlFor="upload-type">Veri Tipi Seçin</Label>
                <select
                  id="upload-type"
                  value={uploadType}
                  onChange={(e) => setUploadType(e.target.value)}
                  className="w-full h-10 px-3 rounded-md border border-slate-300 bg-white text-slate-900 focus:outline-none focus:ring-2 focus:ring-cyan-500"
                >
                  <option value="flights">Uçuşlar (Flights)</option>
                  <option value="reservations">Rezervasyonlar (Reservations)</option>
                  <option value="operations">Operasyonlar (Operations)</option>
                </select>
              </div>

              {/* File Upload Area */}
              <div className="border-2 border-dashed border-slate-300 rounded-xl p-8 text-center hover:border-cyan-400 transition-colors">
                <div className="flex flex-col items-center gap-4">
                  <div className="w-16 h-16 rounded-full bg-cyan-100 flex items-center justify-center">
                    <FileSpreadsheet className="w-8 h-8 text-cyan-600" />
                  </div>
                  
                  <div>
                    <label htmlFor="file-upload" className="cursor-pointer">
                      <span className="text-cyan-600 hover:text-cyan-700 font-semibold">
                        Dosya seçmek için tıklayın
                      </span>
                      <span className="text-slate-600"> veya sürükleyip bırakın</span>
                    </label>
                    <input
                      id="file-upload"
                      type="file"
                      accept=".xlsx,.xls"
                      onChange={handleFileChange}
                      className="hidden"
                    />
                    <p className="text-sm text-slate-500 mt-2">Excel dosyaları (.xlsx, .xls)</p>
                  </div>

                  {uploadFile && (
                    <div className="flex items-center gap-3 px-4 py-2 bg-slate-100 rounded-lg">
                      <FileSpreadsheet className="w-5 h-5 text-slate-600" />
                      <span className="font-medium text-slate-800">{uploadFile.name}</span>
                      <span className="text-sm text-slate-500">
                        ({(uploadFile.size / 1024).toFixed(2)} KB)
                      </span>
                    </div>
                  )}

                  <Button
                    onClick={handleUpload}
                    disabled={!uploadFile || uploadProgress === "Yükleniyor..."}
                    className="bg-gradient-to-r from-cyan-500 to-teal-500 hover:from-cyan-600 hover:to-teal-600 text-white px-8"
                  >
                    <Upload className="w-4 h-4 mr-2" />
                    {uploadProgress === "Yükleniyor..." ? "Yükleniyor..." : "Yükle"}
                  </Button>
                </div>
              </div>

              {/* Success Message */}
              {uploadProgress && uploadProgress !== "Yükleniyor..." && (
                <div className="p-4 bg-green-50 border border-green-200 rounded-lg flex items-start gap-3">
                  <CheckCircle className="w-5 h-5 text-green-600 flex-shrink-0 mt-0.5" />
                  <div>
                    <p className="font-semibold text-green-800">Başarılı!</p>
                    <p className="text-sm text-green-700">{uploadProgress}</p>
                  </div>
                </div>
              )}

              {/* Error Message */}
              {uploadError && (
                <div className="p-4 bg-red-50 border border-red-200 rounded-lg flex items-start gap-3">
                  <AlertCircle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
                  <div>
                    <p className="font-semibold text-red-800">Hata!</p>
                    <p className="text-sm text-red-700">{uploadError}</p>
                  </div>
                </div>
              )}

              {/* Info Box */}
              <div className="p-4 bg-blue-50 border border-blue-200 rounded-lg">
                <h4 className="font-semibold text-blue-900 mb-2">Excel Kolon Gereksinimleri:</h4>
                <ul className="text-sm text-blue-800 space-y-1 list-disc list-inside">
                  <li><strong>Uçuşlar:</strong> flightCode, airline, from, to, date, time, direction, passengers, hasPNR, pnr</li>
                  <li><strong>Rezervasyonlar:</strong> voucherNo, leader_name, leader_passport, product_code, product_name, hotel, arrivalDate, departureDate, pax, status</li>
                  <li><strong>Operasyonlar:</strong> flightCode, type, from, to, date, time, passengers, hotel, transferTime, notes</li>
                </ul>
              </div>
            </div>
          </TabsContent>

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
