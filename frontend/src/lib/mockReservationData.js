export const mockReservations = [
  {
    id: 1,
    voucherNo: "DG2024-001",
    leader: { name: "Hans Mueller", passport: "C01234567" },
    product: { code: "CAP7", name: "Kapadokya 7 Gün Turu" },
    hotel: "Museum Hotel",
    arrivalDate: "2024-12-20",
    departureDate: "2024-12-27",
    pax: 4,
    status: "confirmed"
  },
  {
    id: 2,
    voucherNo: "DG2024-002",
    leader: { name: "Maria Schmidt", passport: "C02345678" },
    product: { code: "IST5", name: "İstanbul 5 Gün Turu" },
    hotel: "Grand Hyatt Istanbul",
    arrivalDate: "2024-12-18",
    departureDate: "2024-12-23",
    pax: 2,
    status: "confirmed"
  },
  {
    id: 3,
    voucherNo: "DG2024-003",
    leader: { name: "Thomas Weber", passport: "C03456789" },
    product: { code: "AYT10", name: "Antalya 10 Gün Tatil" },
    hotel: "Rixos Premium Belek",
    arrivalDate: "2024-12-22",
    departureDate: "2025-01-01",
    pax: 6,
    status: "pending"
  },
  {
    id: 4,
    voucherNo: "DG2024-004",
    leader: { name: "Anna Becker", passport: "C04567890" },
    product: { code: "BDR14", name: "Bodrum 14 Gün Tatil" },
    hotel: "Mandarin Oriental",
    arrivalDate: "2024-12-25",
    departureDate: "2025-01-08",
    pax: 3,
    status: "confirmed"
  },
  {
    id: 5,
    voucherNo: "DG2024-005",
    leader: { name: "Peter Fischer", passport: "C05678901" },
    product: { code: "EGE8", name: "Ege Turu 8 Gün" },
    hotel: "Swissotel The Bosphorus",
    arrivalDate: "2024-12-19",
    departureDate: "2024-12-27",
    pax: 2,
    status: "confirmed"
  }
];

export const mockHotelBlockages = {
  "2024-12": {
    "Grand Hyatt Istanbul": [5, 12, 18, 25],
    "Rixos Premium Belek": [8, 15, 22, 29],
    "Museum Hotel": [3, 10, 17, 24, 31]
  }
};
