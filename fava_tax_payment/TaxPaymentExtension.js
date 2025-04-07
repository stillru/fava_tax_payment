export default {
    init() {
      console.log("TaxPaymentExtension initialized");
    },
    onPageLoad() {
      console.log("A Fava page has loaded:", window.location.pathname);
    },
    onExtensionPageLoad() {
      console.log("TaxPaymentExtension page loaded:", window.location.pathname);
  
      const generateButton = document.getElementById("generate-pdfs");
      if (generateButton) {
        generateButton.addEventListener("click", () => {
          fetch("./generate_tax_pdfs", { method: "POST" })
            .then(response => response.json())
            .then(data => {
              document.getElementById("result").innerHTML = data.status === "success"
                ? "Generated: " + data.files.join(", ")
                : "Error: " + data.message;
            })
            .catch(error => {
              document.getElementById("result").innerHTML = "Error: " + error;
            });
        });
      }
  
      const addTaxButton = document.getElementById("add-tax");
      if (addTaxButton) {
        addTaxButton.addEventListener("click", () => {
          const container = document.getElementById("taxes-container");
          const newTaxDiv = document.createElement("div");
          newTaxDiv.className = "tax-entry";
          newTaxDiv.innerHTML = `
            <div class="flex-row">
              <div class="input-field">
                <label>Tax Slug:</label>
                <input type="text" name="tax_name" value="new_tax">
              </div>
              <div class="input-field">
                <label>Purpose:</label>
                <input type="text" name="purpose" value="">
              </div>
            </div>
            <div class="flex-row">
              <button type="button" class="remove-tax">Remove Tax</button>
            </div>
          `;
          container.appendChild(newTaxDiv);
          this.addRemoveListeners();
        });
      }
  
      this.addRemoveListeners();
  
      const configForm = document.getElementById("config-form");
      if (configForm) {
        configForm.addEventListener("submit", (event) => {
          event.preventDefault();
          const config = {
            payer: {
              name: document.getElementById("payer-name").value,
              account: document.getElementById("payer-account").value
            },
            expense_category: document.getElementById("expense-category").value,
            taxes: {}
          };
          document.querySelectorAll(".tax-entry").forEach(taxEntry => {
            const taxName = taxEntry.querySelector("input[name='tax_name']").value;
            config.taxes[taxName] = {
              purpose: taxEntry.querySelector("input[name='purpose']").value,
              recipient: taxEntry.querySelector("input[name='recipient']").value,
              payment_code: taxEntry.querySelector("input[name='payment_code']").value,
              recipient_account: taxEntry.querySelector("input[name='recipient_account']").value,
              model: taxEntry.querySelector("input[name='model']").value,
              reference_number: taxEntry.querySelector("input[name='reference_number']").value
            };
          });
          fetch("./save_config", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(config)
          })
            .then(response => response.json())
            .then(data => {
              document.getElementById("config-result").innerHTML = data.status === "success"
                ? "Configuration saved successfully!"
                : "Error: " + data.message;
            })
            .catch(error => {
              document.getElementById("config-result").innerHTML = "Error: " + error;
            });
        });
      }
    },
  
    // Вспомогательная функция
    addRemoveListeners() {
      document.querySelectorAll(".remove-tax").forEach(button => {
        button.removeEventListener("click", this.removeTaxHandler);
        button.addEventListener("click", this.removeTaxHandler);
      });
    },
  
    removeTaxHandler(event) {
      event.target.closest(".tax-entry").remove();
    }
  };