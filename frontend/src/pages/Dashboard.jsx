import { Users, UserCheck, UserX, Clock, AlertCircle, TrendingUp } from "lucide-react";
import StatCard from "@/components/StatCard";
import ArrivalDepartureChart from "@/components/ArrivalDepartureChart";
import TopHotels from "@/components/TopHotels";
import TopProducts from "@/components/TopProducts";
import { mockDashboardData } from "@/lib/mockData";

const Dashboard = () => {
  const stats = mockDashboardData.stats;

  return (
    <div className="space-y-6" data-testid="dashboard">
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5 gap-4 lg:gap-6">
        <StatCard
          icon={Users}
          title="Gelecekteki Toplam Yolcu"
          value={stats.totalUpcomingPassengers}
          iconColor="from-blue-500 to-blue-600"
          bgColor="from-blue-50 to-blue-100"
          testId="stat-upcoming-passengers"
        />
        <StatCard
          icon={UserCheck}
          title="Bugün Gelecek Yolcu"
          value={stats.todayArrivals}
          iconColor="from-green-500 to-green-600"
          bgColor="from-green-50 to-green-100"
          testId="stat-today-arrivals"
        />
        <StatCard
          icon={UserX}
          title="Bugün Dönecek Yolcu"
          value={stats.todayDepartures}
          iconColor="from-orange-500 to-orange-600"
          bgColor="from-orange-50 to-orange-100"
          testId="stat-today-departures"
        />
        <StatCard
          icon={TrendingUp}
          title="Toplam Ağırlanan Turist"
          value={stats.totalServedTourists}
          iconColor="from-purple-500 to-purple-600"
          bgColor="from-purple-50 to-purple-100"
          testId="stat-total-served"
        />
        <StatCard
          icon={AlertCircle}
          title="Bekleyen Uçak Bileti"
          value={stats.pendingTickets}
          iconColor="from-red-500 to-red-600"
          bgColor="from-red-50 to-red-100"
          badge="Acil"
          testId="stat-pending-tickets"
        />
      </div>

      <div className="bg-white rounded-2xl p-6 lg:p-8 border border-slate-200 shadow-lg" style={{
        boxShadow: "0 8px 32px rgba(8, 145, 178, 0.12)"
      }}>
        <div className="flex items-center justify-between mb-6">
          <div>
            <h3 className="text-lg lg:text-xl font-bold text-slate-800">Son 7 Gün</h3>
            <p className="text-sm text-slate-500 mt-1">Geliş ve Gidiş Grafiği (Dünden geriye)</p>
          </div>
          <div className="flex items-center gap-4 text-sm">
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 rounded-full bg-cyan-500"></div>
              <span className="text-slate-600">Geliş</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 rounded-full bg-teal-500"></div>
              <span className="text-slate-600">Gidiş</span>
            </div>
          </div>
        </div>
        <ArrivalDepartureChart data={mockDashboardData.weeklyData} />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <TopHotels data={mockDashboardData.topHotels} />
        <TopProducts data={mockDashboardData.topProducts} />
      </div>
    </div>
  );
};

export default Dashboard;
