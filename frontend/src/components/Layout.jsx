import { Outlet, useLocation, useNavigate } from "react-router-dom";
import { useState } from "react";
import {
  LayoutDashboard,
  Calendar,
  Truck,
  Plane,
  Settings,
  ChevronLeft,
  User,
  Globe,
  Menu,
  X,
  LogOut,
  Camera,
  Upload as UploadIcon,
  Monitor,
  CalendarRange
} from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { useAuth } from "@/context/AuthContext";
import ReservationMonitor from "@/components/ReservationMonitor";

const Layout = () => {
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [language, setLanguage] = useState("TR");
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [showProfileModal, setShowProfileModal] = useState(false);
  const [profileImage, setProfileImage] = useState(null);
  const [profileImagePreview, setProfileImagePreview] = useState(null);
  const [showReservationMonitor, setShowReservationMonitor] = useState(false);
  const [monitorMenuOpen, setMonitorMenuOpen] = useState(false);
  const [dateRange, setDateRange] = useState({ startDate: '', endDate: '' });
  const [selectedDateRange, setSelectedDateRange] = useState(null);
  const location = useLocation();
  const navigate = useNavigate();
  const { user, logout, canAccessPage, updateUser } = useAuth();

  const allMenuItems = [
    { icon: LayoutDashboard, label: "Dashboard", path: "/", page: "dashboard" },
    { icon: Calendar, label: "Rezervasyon Departmanı", path: "/reservations", page: "reservations" },
    { icon: Truck, label: "Operasyon Departmanı", path: "/operations", page: "operations" },
    { icon: Plane, label: "Uçak Departmanı", path: "/flights", page: "flights" },
    { icon: Settings, label: "Yönetim Departmanı", path: "/management", page: "management" },
  ];

  // Filter menu items based on user permissions
  const menuItems = allMenuItems.filter(item => canAccessPage(item.page));

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const handleProfileImageChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      // Check file size (max 2MB)
      if (file.size > 2 * 1024 * 1024) {
        alert('Dosya boyutu 2MB\'dan küçük olmalıdır');
        return;
      }

      // Check file type
      if (!file.type.startsWith('image/')) {
        alert('Lütfen bir resim dosyası seçin');
        return;
      }

      setProfileImage(file);

      // Create preview
      const reader = new FileReader();
      reader.onloadend = () => {
        setProfileImagePreview(reader.result);
      };
      reader.readAsDataURL(file);
    }
  };

  const handleSaveProfileImage = async () => {
    if (!profileImagePreview) {
      alert('Lütfen bir resim seçin');
      return;
    }

    try {
      const api = (await import('@/utils/api')).default;
      
      // Send base64 image to backend
      await api.patch(`/api/users/${user.id}/profile-picture`, {
        profile_picture: profileImagePreview
      });

      // Update user in context
      if (updateUser) {
        updateUser({ ...user, profile_picture: profileImagePreview });
      }

      setShowProfileModal(false);
      setProfileImage(null);
      setProfileImagePreview(null);
      
      // Show success message (optional)
      alert('Profil resmi güncellendi!');
      
    } catch (error) {
      console.error('Error updating profile picture:', error);
      alert('Profil resmi güncellenirken hata oluştu');
    }
  };

  const getRoleBadgeColor = (role) => {
    const colors = {
      admin: 'from-purple-500 to-pink-500',
      flight: 'from-blue-500 to-cyan-500',
      reservation: 'from-green-500 to-emerald-500',
      operation: 'from-orange-500 to-red-500',
      management: 'from-indigo-500 to-purple-500'
    };
    return colors[role] || 'from-gray-500 to-gray-600';
  };

  const getRoleDisplayName = (role) => {
    const names = {
      admin: 'Yönetici',
      flight: 'Uçak',
      reservation: 'Rezervasyon',
      operation: 'Operasyon',
      management: 'Yönetim'
    };
    return names[role] || role;
  };

  const getPageTitle = () => {
    const item = allMenuItems.find(item => item.path === location.pathname);
    return item ? item.label : "Dashboard";
  };

  const handleApplyDateRange = () => {
    if (dateRange.startDate && dateRange.endDate) {
      setSelectedDateRange({
        startDate: dateRange.startDate,
        endDate: dateRange.endDate
      });
      setMonitorMenuOpen(false);
      // Tarihleri console'a yazdır (sonra kullanılabilir)
      console.log('Seçilen tarih aralığı:', {
        startDate: formatDateTurkish(dateRange.startDate),
        endDate: formatDateTurkish(dateRange.endDate)
      });
    } else {
      alert('Lütfen başlangıç ve bitiş tarihlerini seçin');
    }
  };

  const handleClearDateRange = () => {
    setDateRange({ startDate: '', endDate: '' });
    setSelectedDateRange(null);
    console.log('Tarih aralığı temizlendi');
  };

  const formatDateTurkish = (dateString) => {
    if (!dateString) return '';
    const date = new Date(dateString);
    const day = String(date.getDate()).padStart(2, '0');
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const year = date.getFullYear();
    return `${day}/${month}/${year}`;
  };

  return (
    <>
      {/* Profile Picture Modal */}
      {showProfileModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-2xl p-6 w-full max-w-md shadow-2xl">
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-xl font-bold text-slate-800">Profil Resmini Güncelle</h3>
              <button
                onClick={() => {
                  setShowProfileModal(false);
                  setProfileImage(null);
                  setProfileImagePreview(null);
                }}
                className="text-slate-400 hover:text-slate-600 transition-colors"
              >
                <X className="w-6 h-6" />
              </button>
            </div>

            <div className="space-y-6">
              {/* Image Preview */}
              <div className="flex justify-center">
                <div className="relative">
                  <div className={`w-32 h-32 rounded-full bg-gradient-to-br ${getRoleBadgeColor(user?.role || 'admin')} flex items-center justify-center shadow-lg overflow-hidden`}>
                    {profileImagePreview ? (
                      <img 
                        src={profileImagePreview} 
                        alt="Preview"
                        className="w-full h-full object-cover"
                      />
                    ) : user?.profile_picture ? (
                      <img 
                        src={user.profile_picture} 
                        alt={user.name}
                        className="w-full h-full object-cover"
                      />
                    ) : (
                      <User className="w-16 h-16 text-white" />
                    )}
                  </div>
                </div>
              </div>

              {/* File Upload */}
              <div className="border-2 border-dashed border-slate-300 rounded-xl p-6 text-center hover:border-cyan-400 transition-colors">
                <div className="flex flex-col items-center gap-3">
                  <div className="w-12 h-12 rounded-full bg-cyan-100 flex items-center justify-center">
                    <UploadIcon className="w-6 h-6 text-cyan-600" />
                  </div>
                  
                  <div>
                    <label htmlFor="profile-image-upload" className="cursor-pointer">
                      <span className="text-cyan-600 hover:text-cyan-700 font-semibold">
                        Resim seçmek için tıklayın
                      </span>
                    </label>
                    <input
                      id="profile-image-upload"
                      type="file"
                      accept="image/*"
                      onChange={handleProfileImageChange}
                      className="hidden"
                    />
                    <p className="text-sm text-slate-500 mt-1">PNG, JPG, JPEG (max 2MB)</p>
                  </div>

                  {profileImage && (
                    <div className="text-sm text-slate-600 bg-slate-100 px-4 py-2 rounded-lg">
                      {profileImage.name}
                    </div>
                  )}
                </div>
              </div>

              {/* Info */}
              <div className="p-3 bg-blue-50 border border-blue-200 rounded-lg">
                <p className="text-xs text-blue-800">
                  <strong>Not:</strong> Sadece profil resminizi değiştirebilirsiniz. İsim ve diğer bilgiler değiştirilemez.
                </p>
              </div>

              {/* Buttons */}
              <div className="flex gap-3">
                <Button
                  onClick={handleSaveProfileImage}
                  disabled={!profileImagePreview}
                  className="flex-1 bg-gradient-to-r from-cyan-500 to-teal-500 hover:from-cyan-600 hover:to-teal-600 text-white"
                >
                  Kaydet
                </Button>
                <Button
                  onClick={() => {
                    setShowProfileModal(false);
                    setProfileImage(null);
                    setProfileImagePreview(null);
                  }}
                  variant="outline"
                  className="flex-1"
                >
                  İptal
                </Button>
              </div>
            </div>
          </div>
        </div>
      )}

      <div className="flex h-screen bg-gradient-to-br from-slate-50 to-cyan-50">
        <aside
        data-testid="sidebar"
        className={`hidden lg:flex flex-col bg-white border-r border-slate-200 transition-all duration-300 ease-in-out ${
          sidebarOpen ? "w-64" : "w-20"
        }`}
        style={{
          boxShadow: "4px 0 24px rgba(8, 145, 178, 0.08)"
        }}
      >
        <div className="h-20 flex items-center justify-between px-6 border-b border-slate-200">
          <div className="flex items-center gap-3">
            <img 
              src="/images/logo.png" 
              alt="Diogenes Travel Logo" 
              className="h-10 w-10 object-contain"
            />
            {sidebarOpen && (
              <div>
                <h1 className="text-lg font-bold text-slate-800 leading-tight">Diogenes</h1>
                <p className="text-xs text-slate-500">Travel Panel</p>
              </div>
            )}
          </div>
          <Button
            data-testid="sidebar-toggle-btn"
            variant="ghost"
            size="icon"
            onClick={() => setSidebarOpen(!sidebarOpen)}
            className="hover:bg-cyan-50 transition-colors"
          >
            <ChevronLeft
              className={`w-5 h-5 text-slate-600 transition-transform duration-300 ${
                !sidebarOpen ? "rotate-180" : ""
              }`}
            />
          </Button>
        </div>

        <nav className="flex-1 p-4 space-y-2">
          {menuItems.map((item) => {
            const Icon = item.icon;
            const isActive = location.pathname === item.path;
            return (
              <button
                key={item.path}
                onClick={() => navigate(item.path)}
                data-testid={`menu-item-${item.label.toLowerCase()}`}
                className={`w-full flex items-center gap-4 px-4 py-3 rounded-xl transition-all duration-200 group ${
                  isActive
                    ? "bg-gradient-to-r from-cyan-500 to-teal-500 text-white shadow-lg shadow-cyan-200"
                    : "text-slate-700 hover:bg-slate-100"
                }`}
              >
                <Icon
                  className={`w-5 h-5 ${
                    isActive ? "text-white" : "text-slate-600 group-hover:text-cyan-600"
                  } transition-colors`}
                />
                {sidebarOpen && (
                  <span className={`font-medium text-xs ${
                    isActive ? "text-white" : "text-slate-700"
                  }`}>
                    {item.label}
                  </span>
                )}
              </button>
            );
          })}
        </nav>

        {sidebarOpen && user && (
          <div className="p-4 border-t border-slate-200">
            <div className="p-3 rounded-xl bg-slate-50 space-y-3">
              <div className="flex items-center gap-3">
                <div className="relative group">
                  <div className={`w-10 h-10 rounded-full bg-gradient-to-br ${getRoleBadgeColor(user.role)} flex items-center justify-center shadow-lg overflow-hidden`}>
                    {user.profile_picture ? (
                      <img 
                        src={user.profile_picture} 
                        alt={user.name}
                        className="w-full h-full object-cover"
                      />
                    ) : (
                      <User className="w-5 h-5 text-white" />
                    )}
                  </div>
                  <button
                    onClick={() => setShowProfileModal(true)}
                    className="absolute -bottom-1 -right-1 w-5 h-5 bg-cyan-500 rounded-full flex items-center justify-center shadow-lg opacity-0 group-hover:opacity-100 transition-opacity"
                  >
                    <Camera className="w-3 h-3 text-white" />
                  </button>
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-semibold text-slate-800 truncate">{user.name}</p>
                  <p className="text-xs text-slate-500 truncate">{user.email}</p>
                </div>
              </div>
              <div className="flex items-center justify-between">
                <span className={`inline-block px-2 py-1 rounded-lg text-xs font-semibold text-white bg-gradient-to-r ${getRoleBadgeColor(user.role)}`}>
                  {getRoleDisplayName(user.role)}
                </span>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={handleLogout}
                  className="text-xs text-red-600 hover:text-red-700 hover:bg-red-50"
                >
                  <LogOut className="w-4 h-4 mr-1" />
                  Çıkış
                </Button>
              </div>
            </div>
          </div>
        )}
      </aside>

      {mobileMenuOpen && (
        <div
          className="lg:hidden fixed inset-0 bg-black bg-opacity-50 z-40"
          onClick={() => setMobileMenuOpen(false)}
        />
      )}

      <aside
        className={`lg:hidden fixed inset-y-0 left-0 w-64 bg-white z-50 transform transition-transform duration-300 ${
          mobileMenuOpen ? "translate-x-0" : "-translate-x-full"
        }`}
        style={{
          boxShadow: "4px 0 24px rgba(8, 145, 178, 0.08)"
        }}
      >
        <div className="h-20 flex items-center justify-between px-6 border-b border-slate-200">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-cyan-500 to-teal-600 flex items-center justify-center shadow-lg">
              <Plane className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="text-lg font-bold text-slate-800 leading-tight">Diogenes</h1>
              <p className="text-xs text-slate-500">Travel Panel</p>
            </div>
          </div>
          <Button
            variant="ghost"
            size="icon"
            onClick={() => setMobileMenuOpen(false)}
          >
            <X className="w-5 h-5 text-slate-600" />
          </Button>
        </div>

        <nav className="flex-1 p-4 space-y-2">
          {menuItems.map((item) => {
            const Icon = item.icon;
            const isActive = location.pathname === item.path;
            return (
              <button
                key={item.path}
                onClick={() => {
                  navigate(item.path);
                  setMobileMenuOpen(false);
                }}
                className={`w-full flex items-center gap-4 px-4 py-3 rounded-xl transition-all duration-200 ${
                  isActive
                    ? "bg-gradient-to-r from-cyan-500 to-teal-500 text-white shadow-lg"
                    : "text-slate-700 hover:bg-slate-100"
                }`}
              >
                <Icon className={`w-5 h-5 ${isActive ? "text-white" : "text-slate-600"}`} />
                <span className={`font-medium text-xs ${isActive ? "text-white" : "text-slate-700"}`}>
                  {item.label}
                </span>
              </button>
            );
          })}
        </nav>
      </aside>

      <div className="flex-1 flex flex-col overflow-hidden">
        <header className="h-20 bg-white border-b border-slate-200 flex items-center justify-between px-4 lg:px-8" style={{
          boxShadow: "0 4px 24px rgba(8, 145, 178, 0.06)"
        }}>
          <div className="flex items-center gap-4">
            <Button
              variant="ghost"
              size="icon"
              className="lg:hidden"
              onClick={() => setMobileMenuOpen(true)}
              data-testid="mobile-menu-btn"
            >
              <Menu className="w-6 h-6 text-slate-700" />
            </Button>
            <div>
              <h2 className="text-xl lg:text-2xl font-bold text-slate-800">{getPageTitle()}</h2>
              <p className="text-xs lg:text-sm text-slate-500">Hoş geldiniz! İşte bugünün özeti</p>
            </div>
          </div>

          <div className="flex items-center gap-3">
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button
                  variant="outline"
                  size="sm"
                  className="border-slate-300 hover:border-cyan-400 hover:bg-cyan-50 transition-all"
                  data-testid="language-selector"
                >
                  <Globe className="w-4 h-4 mr-2" />
                  <span className="hidden sm:inline">{language}</span>
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end">
                <DropdownMenuItem onClick={() => setLanguage("TR")} data-testid="lang-tr">
                  🇹🇷 Türkçe
                </DropdownMenuItem>
                <DropdownMenuItem onClick={() => setLanguage("EN")} data-testid="lang-en">
                  🇬🇧 English
                </DropdownMenuItem>
                <DropdownMenuItem onClick={() => setLanguage("DE")} data-testid="lang-de">
                  🇩🇪 Deutsch
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>

            {/* Monitör butonu - sadece admin, reservation ve management için */}
            {(user?.role === 'admin' || user?.role === 'reservation' || user?.role === 'management') && (
              <Button
                variant="outline"
                size="sm"
                onClick={() => setShowReservationMonitor(true)}
                className="border-slate-300 hover:border-cyan-400 hover:bg-cyan-50 transition-all"
                data-testid="monitor-btn"
              >
                <Monitor className="w-4 h-4 mr-2" />
                <span className="hidden sm:inline">Monitör</span>
              </Button>
            )}

            {canAccessPage('admin') && (
              <Button
                onClick={() => navigate('/admin')}
                className="bg-gradient-to-r from-cyan-500 to-teal-500 hover:from-cyan-600 hover:to-teal-600 text-white shadow-lg shadow-cyan-200 transition-all hidden sm:flex"
                data-testid="admin-panel-btn"
              >
                <Settings className="w-4 h-4 mr-2" />
                Admin Paneli
              </Button>
            )}
          </div>
        </header>

        <main className="flex-1 overflow-y-auto p-4 lg:p-8">
          <Outlet />
        </main>
      </div>
      </div>

      {/* Reservation Monitor Modal */}
      <ReservationMonitor 
        isOpen={showReservationMonitor} 
        onClose={() => setShowReservationMonitor(false)} 
      />
    </>
  );
};

export default Layout;
