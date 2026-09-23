const weekdayLabel = document.getElementById("weekdayLabel");
const dateLabel = document.getElementById("dateLabel");

if (weekdayLabel || dateLabel) {
  const today = new Date();
  if (weekdayLabel) {
    weekdayLabel.textContent = today.toLocaleDateString(undefined, { weekday: "long" });
  }
  if (dateLabel) {
    dateLabel.textContent = today.toLocaleDateString(undefined, {
      day: "2-digit",
      month: "short",
      year: "numeric",
    });
  }
}
