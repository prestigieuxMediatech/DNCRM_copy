// static/js/punchin.js

const elapsedHero = document.getElementById("elapsedHero");
const workingHours = document.getElementById("workingHours");
const remainingTime = document.getElementById("remainingTime");

if (elapsedHero && elapsedHero.dataset.punchIn) {
  const punchInAt = new Date(elapsedHero.dataset.punchIn).getTime();

  // 1. Office Closing Time set karte hain (Aaj Shaam 6:00 PM)
  const officeEndTime = new Date();
  officeEndTime.setHours(18, 0, 0, 0); 

  const updateTimers = () => {
    const now = Date.now();
    
    // --- Live Working Hours Counter ---
    const totalSeconds = Math.max(Math.floor((now - punchInAt) / 1000), 0);
    const hours = Math.floor(totalSeconds / 3600);
    const minutes = Math.floor((totalSeconds % 3600) / 60);
    const seconds = totalSeconds % 60;
    const formattedWorking = `${hours}h ${String(minutes).padStart(2, "0")}m ${String(seconds).padStart(2, "0")}s`;

    elapsedHero.textContent = formattedWorking;
    if (workingHours) {
      workingHours.textContent = formattedWorking;
    }

    // --- Live Remaining Time Till 6:00 PM Counter ---
    if (remainingTime) {
      const remainingMs = officeEndTime.getTime() - now;
      // if (remainingMs <= 0) {
      //   remainingTime.textContent = "0h 00m 00s";
      // } 

        if (remainingMs <= 0) {
           remainingTime.textContent = "Office Closed";
        
        // 6:10 PM ke baad page reload taaki backend auto-close dikha sake
           const now = new Date();
        if (now.getHours() >= 18 && now.getMinutes() >= 10) {
            location.reload();
        }
      } else {
        const remTotalSec = Math.floor(remainingMs / 1000);
        const remH = Math.floor(remTotalSec / 3600);
        const remM = Math.floor((remTotalSec % 3600) / 60);
        const remS = remTotalSec % 60;
        remainingTime.textContent = `${remH}h ${String(remM).padStart(2, "0")}m ${String(remS).padStart(2, "0")}s`;
      }
    }
  };

  updateTimers();
  window.setInterval(updateTimers, 1000);
}





































// const elapsedHero = document.getElementById("elapsedHero");
// const workingHours = document.getElementById("workingHours");

// if (elapsedHero?.dataset.punchIn) {
//   const punchInAt = new Date(elapsedHero.dataset.punchIn).getTime();

//   const formatElapsed = () => {
//     const totalSeconds = Math.max(Math.floor((Date.now() - punchInAt) / 1000), 0);
//     const hours = Math.floor(totalSeconds / 3600);
//     const minutes = Math.floor((totalSeconds % 3600) / 60);
//     const seconds = totalSeconds % 60;
//     return `${hours}h ${String(minutes).padStart(2, "0")}m ${String(seconds).padStart(2, "0")}s`;
//   };

//   const updateTimer = () => {
//     const value = formatElapsed();
//     elapsedHero.textContent = value;
//     if (workingHours) {
//       workingHours.textContent = value;
//     }
//   };

//   updateTimer();
//   window.setInterval(updateTimer, 1000);
// }
