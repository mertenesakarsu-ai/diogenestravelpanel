import React from 'react';

const AccessDenied = () => {
  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-600 via-purple-700 to-indigo-800 flex items-center justify-center p-4">
      <div className="max-w-md w-full bg-white bg-opacity-10 backdrop-blur-lg rounded-3xl shadow-2xl border border-white border-opacity-20 p-8 text-center">
        {/* Lock Icon */}
        <div className="text-7xl mb-6 animate-pulse">
          🔒
        </div>
        
        {/* Error Code */}
        <h1 className="text-6xl font-bold text-white mb-4 drop-shadow-lg">
          403
        </h1>
        
        {/* Error Message */}
        <p className="text-2xl text-white mb-2 font-semibold">
          Erişim yok
        </p>
        
        <p className="text-white text-opacity-80 mb-6">
          Bu sayfaya erişim izniniz bulunmamaktadır.
        </p>
        
        {/* Divider */}
        <div className="border-t border-white border-opacity-30 my-6"></div>
        
        {/* Additional Info */}
        <div className="text-sm text-white text-opacity-70">
          <p className="mb-2">IP adresiniz yetkilendirilmemiş.</p>
          <p>Erişim için sistem yöneticisi ile iletişime geçin.</p>
        </div>
        
        {/* Back Button */}
        <button
          onClick={() => window.location.href = '/'}
          className="mt-8 px-6 py-3 bg-white bg-opacity-20 hover:bg-opacity-30 text-white rounded-lg transition-all duration-300 backdrop-blur-sm border border-white border-opacity-30"
        >
          Ana Sayfaya Dön
        </button>
      </div>
    </div>
  );
};

export default AccessDenied;
