const StatCard = ({ icon: Icon, title, value, iconColor, bgColor, badge, testId }) => {
  return (
    <div
      data-testid={testId}
      className="relative bg-white rounded-2xl p-6 border border-slate-200 hover:shadow-xl transition-all duration-300 group cursor-pointer"
      style={{
        boxShadow: "0 4px 20px rgba(8, 145, 178, 0.08)"
      }}
    >
      {badge && (
        <div className="absolute top-4 right-4">
          <span className="px-3 py-1 bg-red-100 text-red-600 text-xs font-semibold rounded-full">
            {badge}
          </span>
        </div>
      )}
      
      <div className="flex items-start gap-4">
        <div className={`w-14 h-14 rounded-xl bg-gradient-to-br ${iconColor} flex items-center justify-center shadow-lg group-hover:scale-110 transition-transform duration-300`}>
          <Icon className="w-7 h-7 text-white" />
        </div>
        
        <div className="flex-1">
          <p className="text-sm text-slate-600 mb-2">{title}</p>
          <h3 className="text-3xl font-bold text-slate-800">{value.toLocaleString('tr-TR')}</h3>
        </div>
      </div>
      
      <div className={`absolute bottom-0 left-0 right-0 h-1 bg-gradient-to-r ${bgColor} rounded-b-2xl`}></div>
    </div>
  );
};

export default StatCard;
