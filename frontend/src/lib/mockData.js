// Helper function to generate real-time dates
const generateWeeklyData = () => {
  const data = [];
  const today = new Date();
  const months = ['Oca', 'Şub', 'Mar', 'Nis', 'May', 'Haz', 'Tem', 'Ağu', 'Eyl', 'Eki', 'Kas', 'Ara'];
  
  // Generate data for last 7 days (yesterday and 6 days before)
  for (let i = 7; i >= 1; i--) {
    const date = new Date(today);
    date.setDate(today.getDate() - i);
    
    const day = date.getDate();
    const month = months[date.getMonth()];
    const dateStr = `${day} ${month}`;
    
    // Generate random but realistic data
    const baseArrivals = 150 + Math.floor(Math.random() * 100);
    const baseDepartures = 140 + Math.floor(Math.random() * 90);
    
    data.push({
      date: dateStr,
      arrivals: baseArrivals,
      departures: baseDepartures
    });
  }
  
  return data;
};

export const mockDashboardData = {
  stats: {
    totalUpcomingPassengers: 2847,
    todayArrivals: 156,
    todayDepartures: 142,
    totalServedTourists: 18456,
    pendingTickets: 23
  },
  
  weeklyData: generateWeeklyData(),
  
  topHotels: [
    { name: 'Grand Hyatt Istanbul', location: 'İstanbul, Beyoğlu', guests: 487 },
    { name: 'Rixos Premium Belek', location: 'Antalya, Belek', guests: 423 },
    { name: 'Swissotel The Bosphorus', location: 'İstanbul, Beşiktaş', guests: 389 },
    { name: 'Maxx Royal Belek', location: 'Antalya, Belek', guests: 356 },
    { name: 'Museum Hotel', location: 'Kapadokya, Nevşehir', guests: 312 }
  ],
  
  topProducts: [
    { code: 'CAP7', name: 'Kapadokya 7 Gün Turu', sales: 245 },
    { code: 'IST5', name: 'İstanbul 5 Gün Turu', sales: 198 },
    { code: 'AYT10', name: 'Antalya 10 Gün Tatil', sales: 176 },
    { code: 'BDR14', name: 'Bodrum 14 Gün Tatil', sales: 154 },
    { code: 'EGE8', name: 'Ege Turu 8 Gün', sales: 132 }
  ]
};
