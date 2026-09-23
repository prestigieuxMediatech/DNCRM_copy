// static/js/admin/payroll.js

(function () {
    "use strict";

    function formatCurrency(val) {
        return new Intl.NumberFormat("en-IN", {
            style: "currency",
            currency: "INR"
        }).format(val || 0);
    }

    function formatLPA(amount) {
        const lpa = amount / 100000;
        return lpa.toFixed(2) + " LPA";
    }

    function openModal(id) {
        const modal = document.getElementById(id);
        if (!modal) return;
        modal.classList.add("active");
        modal.style.display = "flex";
        modal.style.visibility = "visible";
        modal.style.opacity = "1";
        modal.style.pointerEvents = "auto";
        modal.setAttribute("aria-hidden", "false");
    }

    // function closeModal(id) {
    //     const modal = document.getElementById(id);
    //     if (!modal) return;
    //     if (modal.matches(":popover-open")) modal.hidePopover();
    //     modal.classList.remove("active");
    //     modal.style.removeProperty("display");
    //     modal.style.removeProperty("visibility");
    //     modal.style.removeProperty("opacity");
    //     modal.style.removeProperty("pointer-events");
    //     modal.setAttribute("aria-hidden", "true");
    // }



    function closeModal(id) {
    const modal = document.getElementById(id);

    if (!modal) return;

    modal.classList.remove("active");
    modal.style.removeProperty("display");
    modal.style.removeProperty("visibility");
    modal.style.removeProperty("opacity");
    modal.style.removeProperty("pointer-events");
    modal.setAttribute("aria-hidden", "true");
}

    // const generateModal = document.getElementById("modal-generate");
    // if (generateModal) {
    //     generateModal.addEventListener("toggle", () => {
    //         if (generateModal.matches(":popover-open")) {
    //             generateModal.setAttribute("aria-hidden", "false");
    //             return;
    //         }
    //         generateModal.classList.remove("active");
    //         generateModal.style.removeProperty("display");
    //         generateModal.style.removeProperty("visibility");
    //         generateModal.style.removeProperty("opacity");
    //         generateModal.style.removeProperty("pointer-events");
    //         generateModal.setAttribute("aria-hidden", "true");
    //     });
    // }

    document.addEventListener("click", function (e) {
        if (e.target.classList.contains("mycrm-modal-backdrop")) {
            closeModal(e.target.id);
        }
        if (e.target.closest("[data-mycrm-close-modal]")) {
            const modal = e.target.closest(".mycrm-modal-backdrop");
            if (modal) closeModal(modal.id);
        }
    });

    document.querySelectorAll("[data-mycrm-open-modal]").forEach(btn => {
        const showGenerateModal = () => {
            const modalId = "modal-" + btn.dataset.mycrmOpenModal;
            openModal(modalId);
        };
        btn.addEventListener("click", showGenerateModal);
        btn.addEventListener("pointerup", (event) => {
            if (event.pointerType !== "mouse") showGenerateModal();
        });
    });

    // Capture taps on touch devices even if another page-level handler stops bubbling.
    document.addEventListener("click", (event) => {
        const trigger = event.target.closest("[data-mycrm-open-modal]");
        if (!trigger) return;
        const modalId = "modal-" + trigger.dataset.mycrmOpenModal;
        openModal(modalId);
    }, true);

    function calculateNet(prefix) {
        const basic = parseFloat(document.getElementById(prefix + "-basic").value) || 0;
        const bonus = parseFloat(document.getElementById(prefix + "-bonus").value) || 0;
        const leave = parseFloat(document.getElementById(prefix + "-leave").value) || 0;
        const other = parseFloat(document.getElementById(prefix + "-other").value) || 0;
        const net = Math.max(0, basic + bonus - leave - other);
        document.getElementById(prefix + "-net").value = net.toFixed(2);
    }

    ["gen", "edit"].forEach(prefix => {
        ["basic", "bonus", "leave", "other"].forEach(field => {
            const el = document.getElementById(prefix + "-" + field);
            if (el) {
                el.addEventListener("input", () => calculateNet(prefix));
            }
        });
    });

    const genEmployee = document.getElementById("gen-employee");
    if (genEmployee) {
        genEmployee.addEventListener("change", function () {
            const selected = this.options[this.selectedIndex];
            const salary = selected.dataset.salary;
            if (salary) {
                document.getElementById("gen-basic").value = salary;
                calculateNet("gen");
            }
        });
    }

    document.querySelectorAll(".btn-view").forEach(btn => {
        btn.addEventListener("click", function () {
            const id = this.dataset.viewId;
            const url = PAYROLL_URLS.detail.replace("/0/", "/" + id + "/");
            
            fetch(url)
                .then(r => {
                    if (!r.ok) throw new Error("HTTP " + r.status);
                    return r.json();
                })
                .then(data => {
                    const html = `
                        <div class="payroll-view-grid">
                            <div class="view-row">
                                <span class="view-label">EMPLOYEE NAME:</span>
                                <span class="view-value">${data.employee_name}</span>
                            </div>
                            <div class="view-row">
                                <span class="view-label">EMPLOYEE CODE:</span>
                                <span class="view-value">${data.employee_code}</span>
                            </div>
                            <div class="view-row">
                                <span class="view-label">MONTH / YEAR:</span>
                                <span class="view-value">${data.month_year}</span>
                            </div>
                            <div class="view-row">
                                <span class="view-label">STATUS:</span>
                                <span class="view-value status-${data.status}">${data.status}</span>
                            </div>
                            <div class="view-row">
                                <span class="view-label">BASIC SALARY:</span>
                                <span class="view-value">${formatCurrency(data.basic_salary)}</span>
                            </div>
                            <div class="view-row">
                                <span class="view-label">BONUS:</span>
                                <span class="view-value">${formatCurrency(data.bonus)}</span>
                            </div>
                            <div class="view-row">
                                <span class="view-label">LEAVE DEDUCTION:</span>
                                <span class="view-value">${formatCurrency(data.leave_deduction)}</span>
                            </div>
                            <div class="view-row">
                                <span class="view-label">OTHER DEDUCTION:</span>
                                <span class="view-value">${formatCurrency(data.other_deduction)}</span>
                            </div>
                            <div class="view-row net-salary-row">
                                <span class="view-label">NET SALARY:</span>
                                <span class="view-value net-amount">${formatCurrency(data.net_salary)}</span>
                            </div>
                            <div class="view-row">
                                <span class="view-label">PAYMENT DATE:</span>
                                <span class="view-value">${data.payment_date || "-"}</span>
                            </div>
                        </div>
                    `;
                    document.getElementById("view-modal-body").innerHTML = html;
                    
                    const annualBtn = document.getElementById("btn-view-annual");
                    annualBtn.onclick = () => {
                        closeModal("modal-view");
                        const empId = data.employee_id;
                        loadAnnualBreakdown(
                            data.employee_name,
                            data.employee_code,
                            data.designation,
                            data.lpa_display,
                            data.annual_ctc,
                            empId,
                            data.year
                        );
                    };
                    
                    openModal("modal-view");
                })
                .catch(err => {
                    console.error("Error fetching payroll:", err);
                    alert("Error loading payroll details: " + err.message);
                });
        });
    });

    document.querySelectorAll(".btn-edit").forEach(btn => {
        btn.addEventListener("click", function () {
            const id = this.dataset.editId;
            const url = PAYROLL_URLS.detail.replace("/0/", "/" + id + "/");
            
            fetch(url)
                .then(r => {
                    if (!r.ok) throw new Error("HTTP " + r.status);
                    return r.json();
                })
                .then(data => {
                    document.getElementById("edit-id").value = id;
                    document.getElementById("edit-emp-display").value = `${data.employee_name} (${data.employee_code})`;
                    document.getElementById("edit-period-display").value = data.month_year;
                    document.getElementById("edit-basic").value = data.basic_salary.toFixed(2);
                    document.getElementById("edit-bonus").value = data.bonus.toFixed(2);
                    document.getElementById("edit-leave").value = data.leave_deduction.toFixed(2);
                    document.getElementById("edit-other").value = data.other_deduction.toFixed(2);
                    document.getElementById("edit-date").value = data.payment_date || "";
                    document.getElementById("edit-status").value = data.status;
                    
                    calculateNet("edit");
                    
                    const editUrl = PAYROLL_URLS.edit.replace("/0/", "/" + id + "/");
                    document.getElementById("form-edit-payroll").action = editUrl;
                    
                    openModal("modal-edit");
                })
                .catch(err => {
                    console.error("Error fetching payroll:", err);
                    alert("Error loading payroll details");
                });
        });
    });

    /* ❌ REMOVED: Mark Paid AJAX handler
       Ab HTML form POST handle karta hai, JS ki zaroorat nahi
       
    document.querySelectorAll(".btn-mark-paid").forEach(btn => {
        btn.addEventListener("click", function () {
            ...
        });
    });
    */

    function loadAnnualBreakdown(empName, empCode, designation, lpa, annualCtc, empId, year) {
        console.log("Loading annual for empId:", empId, "year:", year);
        
        let url = PAYROLL_URLS.annual.replace("/0/", "/" + empId + "/");
        url = url.replace("/2026/", "/" + year + "/");
        
        console.log("Annual URL:", url);
        
        fetch(url)
            .then(r => {
                if (!r.ok) {
                    throw new Error("HTTP " + r.status);
                }
                return r.json();
            })
            .then(data => {
                console.log("Annual data received:", data);
                
                let monthsHtml = "";
                data.months.forEach(m => {
                    if (m.generated) {
                        monthsHtml += `
                            <tr>
                                <td>${m.month}</td>
                                <td>${formatCurrency(m.base_salary)}</td>
                                <td>${formatCurrency(m.leave_deduction)}</td>
                                <td>${formatCurrency(m.net_salary)}</td>
                                <td>${m.payment_date || "-"}</td>
                                <td><span class="status-badge status-${m.status}">${m.status}</span></td>
                            </tr>
                        `;
                    } else {
                        monthsHtml += `
                            <tr>
                                <td>${m.month}</td>
                                <td style="color:#999">-</td>
                                <td style="color:#999">-</td>
                                <td style="color:#999">-</td>
                                <td style="color:#999">-</td>
                                <td><span class="status-badge" style="background:#f1f5f9;color:#999">Not Generated</span></td>
                            </tr>
                        `;
                    }
                });
                
                const html = `
                    <div class="annual-header">
                        <div class="annual-emp-info">
                            <h4>${data.employee.name}</h4>
                            <p>${data.employee.code}</p>
                            <p>${data.employee.designation}</p>
                        </div>
                        <div class="annual-ctc">
                            <span>ANNUAL CTC</span>
                            <strong>${data.employee.lpa_display}</strong>
                        </div>
                    </div>
                    
                    <div class="annual-summary">
                        <div class="summary-card">
                            <i class="fa-solid fa-check-circle"></i>
                            <div>
                                <span>Total Paid</span>
                                <strong>${formatCurrency(data.summary.total_paid)}</strong>
                            </div>
                        </div>
                        <div class="summary-card">
                            <i class="fa-solid fa-clock"></i>
                            <div>
                                <span>Total Pending</span>
                                <strong>${formatCurrency(data.summary.total_pending)}</strong>
                            </div>
                        </div>
                        <div class="summary-card">
                            <i class="fa-solid fa-minus-circle"></i>
                            <div>
                                <span>Total Deductions</span>
                                <strong>${formatCurrency(data.summary.total_deductions)}</strong>
                            </div>
                        </div>
                    </div>
                    
                    <div class="annual-table-wrap">
                        <table class="mycrm-table">
                            <thead>
                                <tr>
                                    <th>MONTH</th>
                                    <th>BASE SALARY</th>
                                    <th>LEAVE DEDUCTION</th>
                                    <th>NET PAID SALARY</th>
                                    <th>PAYMENT DATE</th>
                                    <th>STATUS</th>
                                </tr>
                            </thead>
                            <tbody>${monthsHtml}</tbody>
                            <tfoot>
                                <tr>
                                    <td><strong>Total Paid Till Date</strong></td>
                                    <td><strong>${formatCurrency(data.grand_totals.base_salary)}</strong></td>
                                    <td><strong>${formatCurrency(data.grand_totals.leave_deduction)}</strong></td>
                                    <td><strong>${formatCurrency(data.grand_totals.net_salary)}</strong></td>
                                    <td colspan="2"></td>
                                </tr>
                            </tfoot>
                        </table>
                    </div>
                `;
                
                document.getElementById("annual-modal-body").innerHTML = html;
                openModal("modal-annual");
            })
            .catch(err => {
                console.error("Error loading annual breakdown:", err);
                alert("Error loading annual breakdown: " + err.message);
            });
    }

    window.showToast = function(message) {
        const toast = document.querySelector("[data-mycrm-toast]");
        if (toast) {
            toast.textContent = message;
            toast.classList.add("show");
            setTimeout(() => toast.classList.remove("show"), 3000);
        }
    };

})();
































































































// // static/js/admin/payroll.js

// (function () {
//     "use strict";

//     // Utility: Format currency
//     function formatCurrency(val) {
//         return new Intl.NumberFormat("en-IN", {
//             style: "currency",
//             currency: "INR"
//         }).format(val || 0);
//     }

//     function formatLPA(amount) {
//         const lpa = amount / 100000;
//         return lpa.toFixed(2) + " LPA";
//     }

//     // Modal functions
//     function openModal(id) {
//         const modal = document.getElementById(id);
//         if (modal) modal.classList.add("active");
//     }

//     function closeModal(id) {
//         const modal = document.getElementById(id);
//         if (modal) modal.classList.remove("active");
//     }

//     // Close modal on backdrop click
//     document.addEventListener("click", function (e) {
//         if (e.target.classList.contains("mycrm-modal-backdrop")) {
//             e.target.classList.remove("active");
//         }
//         if (e.target.closest("[data-mycrm-close-modal]")) {
//             const modal = e.target.closest(".mycrm-modal-backdrop");
//             if (modal) modal.classList.remove("active");
//         }
//     });

//     // Open modal buttons
//     document.querySelectorAll("[data-mycrm-open-modal]").forEach(btn => {
//         btn.addEventListener("click", () => {
//             const modalId = "modal-" + btn.dataset.mycrmOpenModal;
//             openModal(modalId);
//         });
//     });

//     // ─────────────────────────────────────────────────────────
//     // LIVE NET SALARY CALCULATION
//     // ─────────────────────────────────────────────────────────
    
//     function calculateNet(prefix) {
//         const basic = parseFloat(document.getElementById(prefix + "-basic").value) || 0;
//         const bonus = parseFloat(document.getElementById(prefix + "-bonus").value) || 0;
//         const leave = parseFloat(document.getElementById(prefix + "-leave").value) || 0;
//         const other = parseFloat(document.getElementById(prefix + "-other").value) || 0;
//         const net = Math.max(0, basic + bonus - leave - other);
//         document.getElementById(prefix + "-net").value = net.toFixed(2);
//     }

//     ["gen", "edit"].forEach(prefix => {
//         ["basic", "bonus", "leave", "other"].forEach(field => {
//             const el = document.getElementById(prefix + "-" + field);
//             if (el) {
//                 el.addEventListener("input", () => calculateNet(prefix));
//             }
//         });
//     });

//     // ─────────────────────────────────────────────────────────
//     // AUTO-FILL SALARY ON EMPLOYEE SELECT (Generate Modal)
//     // ─────────────────────────────────────────────────────────
    
//     const genEmployee = document.getElementById("gen-employee");
//     if (genEmployee) {
//         genEmployee.addEventListener("change", function () {
//             const selected = this.options[this.selectedIndex];
//             const salary = selected.dataset.salary;
//             if (salary) {
//                 document.getElementById("gen-basic").value = salary;
//                 calculateNet("gen");
//             }
//         });
//     }

// // static/js/admin/payroll.js

// document.querySelectorAll(".btn-view").forEach(btn => {
//     btn.addEventListener("click", function () {
//         const id = this.dataset.viewId;
//         const url = PAYROLL_URLS.detail.replace("/0/", "/" + id + "/");
        
//         fetch(url)
//             .then(r => {
//                 if (!r.ok) throw new Error("HTTP " + r.status);
//                 return r.json();
//             })
//             .then(data => {
//                 // Populate view modal HTML
//                 const html = `
//                     <div class="payroll-view-grid">
//                         <div class="view-row">
//                             <span class="view-label">EMPLOYEE NAME:</span>
//                             <span class="view-value">${data.employee_name}</span>
//                         </div>
//                         <div class="view-row">
//                             <span class="view-label">EMPLOYEE CODE:</span>
//                             <span class="view-value">${data.employee_code}</span>
//                         </div>
//                         <div class="view-row">
//                             <span class="view-label">MONTH / YEAR:</span>
//                             <span class="view-value">${data.month_year}</span>
//                         </div>
//                         <div class="view-row">
//                             <span class="view-label">STATUS:</span>
//                             <span class="view-value status-${data.status}">${data.status}</span>
//                         </div>
//                         <div class="view-row">
//                             <span class="view-label">BASIC SALARY:</span>
//                             <span class="view-value">${formatCurrency(data.basic_salary)}</span>
//                         </div>
//                         <div class="view-row">
//                             <span class="view-label">BONUS:</span>
//                             <span class="view-value">${formatCurrency(data.bonus)}</span>
//                         </div>
//                         <div class="view-row">
//                             <span class="view-label">LEAVE DEDUCTION:</span>
//                             <span class="view-value">${formatCurrency(data.leave_deduction)}</span>
//                         </div>
//                         <div class="view-row">
//                             <span class="view-label">OTHER DEDUCTION:</span>
//                             <span class="view-value">${formatCurrency(data.other_deduction)}</span>
//                         </div>
//                         <div class="view-row net-salary-row">
//                             <span class="view-label">NET SALARY:</span>
//                             <span class="view-value net-amount">${formatCurrency(data.net_salary)}</span>
//                         </div>
//                         <div class="view-row">
//                             <span class="view-label">PAYMENT DATE:</span>
//                             <span class="view-value">${data.payment_date || "-"}</span>
//                         </div>
//                     </div>
//                 `;
//                 document.getElementById("view-modal-body").innerHTML = html;
                
//                 // ✅ ANNUAL BREAKDOWN BUTTON
//                 const annualBtn = document.getElementById("btn-view-annual");
//                 annualBtn.onclick = () => {
//                     closeModal("modal-view");
                    
//                     // ✅ Backend se aaya hua employee_id use karo
//                     const empId = data.employee_id;
//                     console.log("Opening annual for empId:", empId, "year:", data.year);
                    
//                     loadAnnualBreakdown(
//                         data.employee_name,
//                         data.employee_code,
//                         data.designation,
//                         data.lpa_display,
//                         data.annual_ctc,
//                         empId,
//                         data.year
//                     );
//                 };
                
//                 openModal("modal-view");
//             })
//             .catch(err => {
//                 console.error("Error fetching payroll:", err);
//                 alert("Error loading payroll details: " + err.message);
//             });
//     });
// });


// // Edit button click handler
// document.querySelectorAll(".btn-edit").forEach(btn => {
//     btn.addEventListener("click", function () {
//         const id = this.dataset.editId;
        
//         // ✅ SAHI - /0/ ko replace karo (slash ke saath, end nahi)
//         const url = PAYROLL_URLS.detail.replace("/0/", "/" + id + "/");
//         // /dashboard/admin/payroll/0/detail/ → /dashboard/admin/payroll/2/detail/
        
//         fetch(url)
//             .then(r => {
//                 if (!r.ok) throw new Error("HTTP " + r.status);
//                 return r.json();
//             })
//             .then(data => {
//                 // Hidden field mein ID store kar
//                 document.getElementById("edit-id").value = id;
                
//                 // Fields populate kar
//                 document.getElementById("edit-emp-display").value = `${data.employee_name} (${data.employee_code})`;
//                 document.getElementById("edit-period-display").value = data.month_year;
//                 document.getElementById("edit-basic").value = data.basic_salary.toFixed(2);
//                 document.getElementById("edit-bonus").value = data.bonus.toFixed(2);
//                 document.getElementById("edit-leave").value = data.leave_deduction.toFixed(2);
//                 document.getElementById("edit-other").value = data.other_deduction.toFixed(2);
//                 document.getElementById("edit-date").value = data.payment_date || "";
//                 document.getElementById("edit-status").value = data.status;
                
//                 // Net salary calculate kar
//                 calculateNet("edit");
                
//                 // ✅ SAHI - Form action update kar
//                 const editUrl = PAYROLL_URLS.edit.replace("/0/", "/" + id + "/");
//                 document.getElementById("form-edit-payroll").action = editUrl;
                
//                 openModal("modal-edit");
//             })
//             .catch(err => {
//                 console.error("Error fetching payroll:", err);
//                 alert("Error loading payroll details");
//             });
//     });
// });


// // POST form bhejo ya AJAX
// document.querySelectorAll(".btn-mark-paid").forEach(btn => {
//     btn.addEventListener("click", function () {
//         if (!confirm("Mark this payroll as paid?")) return;
//         const id = this.dataset.paidId;
//         const url = PAYROLL_URLS.markPaid.replace("/0/", "/" + id + "/");
        
//         fetch(url, {
//             method: "POST",
//             headers: {
//                 "X-CSRFToken": document.querySelector('[name=csrfmiddlewaretoken]').value,
//                 "Content-Type": "application/x-www-form-urlencoded"
//             },
//             body: "action=mark_paid"
//         })
//         .then(r => {
//             if (r.ok) window.location.reload();
//             else alert("Failed to mark as paid");
//         });
//     });
// });


//     function loadAnnualBreakdown(empName, empCode, designation, lpa, annualCtc, empId, year) {
//     console.log("Loading annual for empId:", empId, "year:", year);
    
//     // ✅ SAHI - slash ke saath replace karo taaki exact match ho
//     // /0/ → /1/ (employee_id)
//     let url = PAYROLL_URLS.annual.replace("/0/", "/" + empId + "/");
    
//     // ✅ SAHI - /2026/ → /year/
//     url = url.replace("/2026/", "/" + year + "/");
    
//     console.log("Annual URL:", url);
    
//     fetch(url)
//         .then(r => {
//             if (!r.ok) {
//                 throw new Error("HTTP " + r.status);
//             }
//             return r.json();
//         })
//         .then(data => {
//             console.log("Annual data received:", data);
            
//             let monthsHtml = "";
//             data.months.forEach(m => {
//                 if (m.generated) {
//                     monthsHtml += `
//                         <tr>
//                             <td>${m.month}</td>
//                             <td>${formatCurrency(m.base_salary)}</td>
//                             <td>${formatCurrency(m.leave_deduction)}</td>
//                             <td>${formatCurrency(m.net_salary)}</td>
//                             <td>${m.payment_date || "-"}</td>
//                             <td><span class="status-badge status-${m.status}">${m.status}</span></td>
//                         </tr>
//                     `;
//                 } else {
//                     monthsHtml += `
//                         <tr>
//                             <td>${m.month}</td>
//                             <td style="color:#999">-</td>
//                             <td style="color:#999">-</td>
//                             <td style="color:#999">-</td>
//                             <td style="color:#999">-</td>
//                             <td><span class="status-badge" style="background:#f1f5f9;color:#999">Not Generated</span></td>
//                         </tr>
//                     `;
//                 }
//             });
            
//             const html = `
//                 <div class="annual-header">
//                     <div class="annual-emp-info">
//                         <h4>${data.employee.name}</h4>
//                         <p>${data.employee.code}</p>
//                         <p>${data.employee.designation}</p>
//                     </div>
//                     <div class="annual-ctc">
//                         <span>ANNUAL CTC</span>
//                         <strong>${data.employee.lpa_display}</strong>
//                     </div>
//                 </div>
                
//                 <div class="annual-summary">
//                     <div class="summary-card">
//                         <i class="fa-solid fa-check-circle"></i>
//                         <div>
//                             <span>Total Paid</span>
//                             <strong>${formatCurrency(data.summary.total_paid)}</strong>
//                         </div>
//                     </div>
//                     <div class="summary-card">
//                         <i class="fa-solid fa-clock"></i>
//                         <div>
//                             <span>Total Pending</span>
//                             <strong>${formatCurrency(data.summary.total_pending)}</strong>
//                         </div>
//                     </div>
//                     <div class="summary-card">
//                         <i class="fa-solid fa-minus-circle"></i>
//                         <div>
//                             <span>Total Deductions</span>
//                             <strong>${formatCurrency(data.summary.total_deductions)}</strong>
//                         </div>
//                     </div>
//                 </div>
                
//                 <div class="annual-table-wrap">
//                     <table class="mycrm-table">
//                         <thead>
//                             <tr>
//                                 <th>MONTH</th>
//                                 <th>BASE SALARY</th>
//                                 <th>LEAVE DEDUCTION</th>
//                                 <th>NET PAID SALARY</th>
//                                 <th>PAYMENT DATE</th>
//                                 <th>STATUS</th>
//                             </tr>
//                         </thead>
//                         <tbody>${monthsHtml}</tbody>
//                         <tfoot>
//                             <tr>
//                                 <td><strong>Total Paid Till Date</strong></td>
//                                 <td><strong>${formatCurrency(data.grand_totals.base_salary)}</strong></td>
//                                 <td><strong>${formatCurrency(data.grand_totals.leave_deduction)}</strong></td>
//                                 <td><strong>${formatCurrency(data.grand_totals.net_salary)}</strong></td>
//                                 <td colspan="2"></td>
//                             </tr>
//                         </tfoot>
//                     </table>
//                 </div>
//             `;
            
//             document.getElementById("annual-modal-body").innerHTML = html;
//             openModal("modal-annual");
//         })
//         .catch(err => {
//             console.error("Error loading annual breakdown:", err);
//             alert("Error loading annual breakdown: " + err.message);
//         });
// }



//     // Toast function
//     window.showToast = function(message) {
//         const toast = document.querySelector("[data-mycrm-toast]");
//         if (toast) {
//             toast.textContent = message;
//             toast.classList.add("show");
//             setTimeout(() => toast.classList.remove("show"), 3000);
//         }
//     };

// })();
