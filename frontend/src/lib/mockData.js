// Helper function to generate real-time dates (yesterday + next 5 days)
const generateWeeklyData = () => {
  const data = [];
  const today = new Date();
  const months = ['Oca', 'Şub', 'Mar', 'Nis', 'May', 'Haz', 'Tem', 'Ağu', 'Eyl', 'Eki', 'Kas', 'Ara'];
  
  // Start from yesterday (-1) and go to next 5 days (+5) = 7 days total
  for (let i = -1; i <= 5; i++) {
    const date = new Date(today);
    date.setDate(today.getDate() + i);
    
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

// Get today's date in Turkish format (DD.MM.YYYY)
export const getTodayDate = () => {
  const today = new Date();
  const day = String(today.getDate()).padStart(2, '0');
  const month = String(today.getMonth() + 1).padStart(2, '0');
  const year = today.getFullYear();
  
  return `${day}.${month}.${year}`;
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
