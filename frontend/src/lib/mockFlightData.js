export const mockFlights = [
  {
    id: 1,
    date: "2024-12-18",
    time: "10:45",
    flightCode: "TK1234",
    from: "VIE",
    to: "IST",
    direction: "arrival",
    passengers: 156,
    hasPNR: true,
    daysUntilFlight: 3
  },
  {
    id: 2,
    date: "2024-12-18",
    time: "14:30",
    flightCode: "XQ567",
    from: "IST",
    to: "AYT",
    direction: "departure",
    passengers: 142,
    hasPNR: true,
    daysUntilFlight: 3
  },
  {
    id: 3,
    date: "2024-12-19",
    time: "08:15",
    flightCode: "PC890",
    from: "MUC",
    to: "IST",
    direction: "arrival",
    passengers: 178,
    hasPNR: false,
    daysUntilFlight: 4
  },
  {
    id: 4,
    date: "2024-12-20",
    time: "11:20",
    flightCode: "TK2345",
    from: "FRA",
    to: "AYT",
    direction: "arrival",
    passengers: 198,
    hasPNR: true,
    daysUntilFlight: 5
  },
  {
    id: 5,
    date: "2024-12-21",
    time: "16:40",
    flightCode: "XQ678",
    from: "IST",
    to: "VIE",
    direction: "departure",
    passengers: 145,
    hasPNR: false,
    daysUntilFlight: 6
  }
];

export const mockFlightDetails = {
  1: {
    passengers: [
      { name: "Hans Mueller", voucherNo: "DG2024-001", hotel: "Grand Hyatt Istanbul", pnr: "ABC123" },
      { name: "Maria Schmidt", voucherNo: "DG2024-002", hotel: "Swissotel", pnr: "DEF456" },
      { name: "Thomas Weber", voucherNo: "DG2024-003", hotel: "Rixos Premium", pnr: "GHI789" }
    ],
    transfers: [
      { time: "12:00", from: "IST Airport", to: "Grand Hyatt Istanbul", vehicle: "Mercedes Sprinter", driver: "Ahmet Y." },
      { time: "12:30", from: "IST Airport", to: "Swissotel", vehicle: "VW Crafter", driver: "Mehmet K." }
    ]
  }
};
