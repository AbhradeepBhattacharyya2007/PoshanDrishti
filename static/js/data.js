// Regional Anganwadi Coordinates & Metrics for Interactive India SVG Map
const INDIA_REGIONS = [
  { state: "Himachal Pradesh", zone: "North", x: 215, y: 95, awcs: 18925, kids: 9400, normal: 86.9, mam: 10.9, sam: 2.2, thr: 95.6, scheme: "Himalayan Millet & Rajma THR" },
  { state: "Punjab", zone: "North", x: 185, y: 115, awcs: 27314, kids: 16400, normal: 86.4, mam: 11.2, sam: 2.4, thr: 95.2, scheme: "Suposhit Punjab Wheat-Milk THR" },
  { state: "Uttarakhand", zone: "North", x: 245, y: 120, awcs: 20067, kids: 10800, normal: 84.8, mam: 12.4, sam: 2.8, thr: 93.4, scheme: "Mandua-Jhangora Baal Poshan" },
  { state: "Haryana", zone: "North", x: 195, y: 145, awcs: 25962, kids: 15900, normal: 85.1, mam: 12.1, sam: 2.8, thr: 94.1, scheme: "Panjiri & Fortified Milk Scheme" },
  { state: "Rajasthan", zone: "West", x: 145, y: 195, awcs: 62010, kids: 34900, normal: 78.4, mam: 16.9, sam: 4.7, thr: 89.0, scheme: "Poshan Vatika & Bajra Energy Mix" },
  { state: "Uttar Pradesh", zone: "North", x: 265, y: 185, awcs: 189796, kids: 98500, normal: 77.9, mam: 17.2, sam: 4.9, thr: 88.4, scheme: "Sambhav Abhiyaan SAM Drive" },
  { state: "Bihar", zone: "East", x: 335, y: 205, awcs: 114989, kids: 67400, normal: 76.5, mam: 18.1, sam: 5.4, thr: 87.6, scheme: "Annaprashan & Sattu Fortification" },
  { state: "Assam", zone: "North-East", x: 435, y: 185, awcs: 62153, kids: 32900, normal: 80.8, mam: 15.1, sam: 4.1, thr: 91.0, scheme: "Poshan Vatika Kitchen Gardens" },
  { state: "West Bengal", zone: "East", x: 365, y: 250, awcs: 119481, kids: 59300, normal: 82.0, mam: 14.5, sam: 3.5, thr: 92.8, scheme: "Egg-Fortified Hot Cooked Meals" },
  { state: "Jharkhand", zone: "East", x: 325, y: 245, awcs: 38432, kids: 24800, normal: 77.2, mam: 17.6, sam: 5.2, thr: 88.9, scheme: "Samar Campaign & Ragi THR" },
  { state: "Gujarat", zone: "West", x: 110, y: 255, awcs: 53029, kids: 31500, normal: 80.1, mam: 15.6, sam: 4.3, thr: 93.1, scheme: "Bal Shakti Take-Home Premix" },
  { state: "Madhya Pradesh", zone: "Central", x: 225, y: 250, awcs: 97135, kids: 54200, normal: 78.8, mam: 16.4, sam: 4.8, thr: 90.5, scheme: "Dastak & Bal Sanjeevani Drive" },
  { state: "Chhattisgarh", zone: "Central", x: 280, y: 280, awcs: 52474, kids: 27600, normal: 80.5, mam: 15.3, sam: 4.2, thr: 91.8, scheme: "Mukhyamantri Suposhan Abhiyaan" },
  { state: "Odisha", zone: "East", x: 320, y: 305, awcs: 74154, kids: 41200, normal: 81.9, mam: 14.3, sam: 3.8, thr: 94.0, scheme: "Mandia (Ragi) Laddu & Mamata" },
  { state: "Maharashtra", zone: "West", x: 175, y: 325, awcs: 110219, kids: 61200, normal: 81.5, mam: 14.8, sam: 3.7, thr: 91.2, scheme: "Rajmata Jijau Child Mission" },
  { state: "Telangana", zone: "South", x: 230, y: 360, awcs: 35700, kids: 21900, normal: 83.4, mam: 13.5, sam: 3.1, thr: 93.7, scheme: "Balamrutham Weaning Food" },
  { state: "Andhra Pradesh", zone: "South", x: 245, y: 410, awcs: 55607, kids: 31100, normal: 84.0, mam: 13.0, sam: 3.0, thr: 94.2, scheme: "YSR Sampoorna Poshana" },
  { state: "Karnataka", zone: "South", x: 185, y: 420, awcs: 65911, kids: 38400, normal: 84.2, mam: 13.1, sam: 2.7, thr: 94.5, scheme: "Ksheera Bhagya & Millet THR" },
  { state: "Kerala", zone: "South", x: 185, y: 485, awcs: 33115, kids: 18200, normal: 89.1, mam: 9.2, sam: 1.7, thr: 97.4, scheme: "Amrutham Nutrimix & VHSND" },
  { state: "Tamil Nadu", zone: "South", x: 225, y: 475, awcs: 54439, kids: 29800, normal: 87.6, mam: 10.4, sam: 2.0, thr: 96.8, scheme: "Puratchi Thalaivar Nutritious Meal" }
];
