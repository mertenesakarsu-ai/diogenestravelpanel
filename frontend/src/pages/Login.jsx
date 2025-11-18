import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '@/context/AuthContext';
import { Button } from '@/components/ui/button';
import { LogIn, User, Shield } from 'lucide-react';
import axios from 'axios';

const Login = () => {
  const [users, setUsers] = useState([]);
  const [selectedUser, setSelectedUser] = useState('');
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    fetchUsers();
  }, []);

  const fetchUsers = async () => {
    try {
      const response = await axios.get(`${process.env.REACT_APP_BACKEND_URL}/api/users`);
      setUsers(response.data);
    } catch (error) {
      console.error('Error fetching users:', error);
      // If no users, initialize default users
      if (error.response?.status === 404 || error.response?.data?.detail?.includes('not found')) {
        initializeUsers();
      }
    }
  };

  const initializeUsers = async () => {
    try {
      await axios.post(`${process.env.REACT_APP_BACKEND_URL}/api/users/init`);
      fetchUsers();
    } catch (error) {
      console.error('Error initializing users:', error);
    }
  };

  const handleLogin = () => {
    if (!selectedUser) {
      alert('Lütfen bir kullanıcı seçin');
      return;
    }

    setLoading(true);
    const user = users.find(u => u.id === selectedUser);
    
    if (user) {
      login(user);
      navigate('/');
    }
    
    setLoading(false);
  };

  const getRoleBadgeColor = (role) => {
    const colors = {
      admin: 'bg-gradient-to-r from-purple-500 to-pink-500',
      flight: 'bg-gradient-to-r from-blue-500 to-cyan-500',
      reservation: 'bg-gradient-to-r from-green-500 to-emerald-500',
      operation: 'bg-gradient-to-r from-orange-500 to-red-500',
      management: 'bg-gradient-to-r from-indigo-500 to-purple-500'
    };
    return colors[role] || 'bg-gray-500';
  };

  const getRoleDisplayName = (role) => {
    const names = {
      admin: 'Yönetici',
      flight: 'Uçak Departmanı',
      reservation: 'Rezervasyon Departmanı',
      operation: 'Operasyon Departmanı',
      management: 'Yönetim Departmanı'
    };
    return names[role] || role;
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-100 flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        {/* Logo/Header */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-20 h-20 rounded-3xl bg-gradient-to-br from-blue-500 to-indigo-600 shadow-2xl mb-4">
            <Shield className="w-10 h-10 text-white" />
          </div>
          <h1 className="text-3xl font-bold text-slate-800 mb-2">Diogenes Travel Panel</h1>
          <p className="text-slate-600">Seyahat Yönetim Sistemi</p>
        </div>

        {/* Login Card */}
        <div className="bg-white rounded-3xl shadow-2xl p-8 border border-slate-200">
          <div className="mb-6">
            <h2 className="text-2xl font-bold text-slate-800 mb-2">Giriş Yap</h2>
            <p className="text-sm text-slate-600">Lütfen kullanıcınızı seçin</p>
          </div>

          {users.length === 0 ? (
            <div className="text-center py-8">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto mb-4"></div>
              <p className="text-slate-600">Kullanıcılar yükleniyor...</p>
            </div>
          ) : (
            <>
              {/* User Selection */}
              <div className="space-y-3 mb-6">
                {users.map((user) => (
                  <label
                    key={user.id}
                    className={`flex items-center p-4 rounded-2xl border-2 cursor-pointer transition-all ${
                      selectedUser === user.id
                        ? 'border-blue-500 bg-blue-50 shadow-lg scale-105'
                        : 'border-slate-200 hover:border-blue-300 hover:bg-slate-50'
                    }`}
                  >
                    <input
                      type="radio"
                      name="user"
                      value={user.id}
                      checked={selectedUser === user.id}
                      onChange={(e) => setSelectedUser(e.target.value)}
                      className="sr-only"
                    />
                    <div className={`w-12 h-12 rounded-xl ${getRoleBadgeColor(user.role)} flex items-center justify-center shadow-lg flex-shrink-0`}>
                      <User className="w-6 h-6 text-white" />
                    </div>
                    <div className="ml-4 flex-1">
                      <div className="font-semibold text-slate-800">{user.name}</div>
                      <div className="text-sm text-slate-500">{user.email}</div>
                    </div>
                    <div className="ml-2">
                      <span className={`inline-block px-3 py-1 rounded-full text-xs font-semibold text-white ${getRoleBadgeColor(user.role)}`}>
                        {getRoleDisplayName(user.role)}
                      </span>
                    </div>
                  </label>
                ))}
              </div>

              {/* Login Button */}
              <Button
                onClick={handleLogin}
                disabled={!selectedUser || loading}
                className="w-full h-12 text-base font-semibold rounded-xl bg-gradient-to-r from-blue-500 to-indigo-600 hover:from-blue-600 hover:to-indigo-700 shadow-lg"
              >
                {loading ? (
                  <div className="flex items-center gap-2">
                    <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                    <span>Giriş yapılıyor...</span>
                  </div>
                ) : (
                  <div className="flex items-center gap-2">
                    <LogIn className="w-5 h-5" />
                    <span>Giriş Yap</span>
                  </div>
                )}
              </Button>
            </>
          )}
        </div>

        {/* Footer */}
        <div className="text-center mt-6">
          <p className="text-sm text-slate-500">
            © 2025 Diogenes Travel. Tüm hakları saklıdır.
          </p>
        </div>
      </div>
    </div>
  );
};

export default Login;
