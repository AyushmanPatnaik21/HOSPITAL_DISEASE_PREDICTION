// Hospital Management System - Main JavaScript File

document.addEventListener("DOMContentLoaded", function () {
  console.log("Hospital Management System loaded");
  loadDashboardData();
});

/**
 * Load dashboard statistics from API
 */
function loadDashboardData() {
  // Fetch total patients
  fetch("/api/patients")
    .then((response) => response.json())
    .then((data) => {
      document.getElementById("total-patients").textContent =
        data.patients.length;
    })
    .catch((error) => console.error("Error loading patients:", error));

  // Fetch total doctors
  fetch("/api/doctors")
    .then((response) => response.json())
    .then((data) => {
      document.getElementById("total-doctors").textContent =
        data.doctors.length;
    })
    .catch((error) => console.error("Error loading doctors:", error));

  // Fetch appointments
  fetch("/api/appointments")
    .then((response) => response.json())
    .then((data) => {
      document.getElementById("upcoming-appointments").textContent =
        data.appointments.length;
    })
    .catch((error) => console.error("Error loading appointments:", error));

  // Fetch bills
  fetch("/api/billing")
    .then((response) => response.json())
    .then((data) => {
      const pendingBills = data.bills.filter(
        (bill) => bill.status === "pending",
      ).length;
      document.getElementById("pending-bills").textContent = pendingBills;
    })
    .catch((error) => console.error("Error loading bills:", error));
}

/**
 * Make API call
 */
function apiCall(endpoint, method = "GET", data = null) {
  const options = {
    method: method,
    headers: {
      "Content-Type": "application/json",
    },
  };

  if (data) {
    options.body = JSON.stringify(data);
  }

  return fetch(endpoint, options).then((response) => response.json());
}

/**
 * Navigate to page
 */
function navigateTo(page) {
  window.location.href = `/${page}`;
}
