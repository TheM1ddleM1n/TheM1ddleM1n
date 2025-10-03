let count = 20;
let interval = setInterval(() => {
  process.stdout.write("\rCountdown: " + count);
  if (count-- <= 0) {
    clearInterval(interval);
    console.log("\nTime's up!");
  }
}, 2000);
