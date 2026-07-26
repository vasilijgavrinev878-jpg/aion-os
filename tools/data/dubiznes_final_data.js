const dubiznesData = [
];

console.log("Total businesses:", dubiznesData.length);
const fs = require("fs");
fs.writeFileSync("dubiznes_final_data.json", JSON.stringify(dubiznesData, null, 2));
