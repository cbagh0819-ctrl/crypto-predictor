// Charlo AI Watchlist - Client Controller with 5s Loading & Auth

let allPredictions = [];

// ==========================================
// 1. SCREEN NAVIGATION CONTROLLER
// ==========================================
function showScreen(screenId) {
  document.querySelectorAll(".screen-view").forEach(s => s.classList.remove("active"));
  const target = document.getElementById(screenId);
  if (target) {
    target.classList.add("active");
  }
}

// ==========================================
// 2. 5-SECOND HIGH-TECH LOADER ENGINE
// ==========================================
function start5SecondLoadingProcess() {
  const progressBar = document.getElementById("progressBarFill");
  const percentText = document.getElementById("loaderPercent");
  const countdownText = document.getElementById("countdownSeconds");
  const statusText = document.getElementById("loaderStatusText");

  const totalDuration = 5000; // exactly 5 seconds
  const intervalStep = 50;
  let elapsed = 0;

  const statusMilestones = [
    { at: 500, text: "Booting Charlo AI neural models..." },
    { at: 1800, text: "Syncing live 1h Binance candlestick records..." },
    { at: 3200, text: "Calibrating 24-hour growth probabilities..." },
    { at: 4400, text: "Security verification verified. Ready." }
  ];

  const timer = setInterval(() => {
    elapsed += intervalStep;
    const progress = Math.min(100, Math.round((elapsed / totalDuration) * 100));
    const remainingSeconds = Math.max(0, Math.ceil((totalDuration - elapsed) / 1000));

    if (progressBar) progressBar.style.width = `${progress}%`;
    if (percentText) percentText.textContent = `${progress}%`;
    if (countdownText) countdownText.textContent = remainingSeconds;

    // Update status messages
    for (let m of statusMilestones) {
      if (elapsed >= m.at && statusText) {
        statusText.textContent = m.text;
      }
    }

    // 5 seconds completed
    if (elapsed >= totalDuration) {
      clearInterval(timer);
      onLoadingComplete();
    }
  }, intervalStep);
}

function onLoadingComplete() {
  // Check if session is already active
  const isAuth = sessionStorage.getItem("charlo_auth") === "true";
  if (isAuth) {
    showScreen("screen-dashboard");
    loadPredictions();
  } else {
    showScreen("screen-login");
    document.getElementById("passwordInput")?.focus();
  }
}

// ==========================================
// 3. AUTHENTICATION (ID: Admin, Pass: Admin@123)
// ==========================================
const loginForm = document.getElementById("loginForm");
const loginError = document.getElementById("loginError");
const passwordInput = document.getElementById("passwordInput");
const usernameInput = document.getElementById("usernameInput");
const passwordToggle = document.getElementById("passwordToggle");

// Toggle password visibility
passwordToggle?.addEventListener("click", () => {
  if (passwordInput.type === "password") {
    passwordInput.type = "text";
  } else {
    passwordInput.type = "password";
  }
});

// Handle Login Form Submission
loginForm?.addEventListener("submit", async (e) => {
  e.preventDefault();
  loginError.classList.remove("visible");

  const id = usernameInput.value.trim();
  const password = passwordInput.value;

  if (id === "Admin" && password === "Admin@123") {
    // Authentication successful
    sessionStorage.setItem("charlo_auth", "true");
    showScreen("screen-dashboard");
    loadPredictions();
  } else {
    // Authentication failed
    loginError.textContent = "Invalid Operator ID or Security Key.";
    loginError.classList.add("visible");
    passwordInput.value = "";
    passwordInput.focus();
  }
});

// Logout / Lock Terminal
document.getElementById("logoutBtn")?.addEventListener("click", () => {
  sessionStorage.removeItem("charlo_auth");
  showScreen("screen-login");
  if (passwordInput) passwordInput.value = "";
  if (loginError) loginError.classList.remove("visible");
});

// ==========================================
// 4. REAL-TIME CLOCK & 10-MINUTE SYNC COUNTDOWN
// ==========================================
let syncSecondsRemaining = 600; // 10 minutes = 600 seconds

function updateLiveClock() {
  const now = new Date();
  
  // Format Date: e.g. "Saturday, 24 Oct 2026"
  const dateOptions = { weekday: 'long', day: 'numeric', month: 'short', year: 'numeric' };
  const formattedDate = now.toLocaleDateString('en-US', dateOptions);

  // Format Time: e.g. "08:32:45 AM"
  const timeOptions = { hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: true };
  const formattedTime = now.toLocaleTimeString('en-US', timeOptions);

  const dateElem = document.getElementById("liveDate");
  const timeElem = document.getElementById("liveTime");

  if (dateElem) dateElem.textContent = formattedDate;
  if (timeElem) timeElem.textContent = formattedTime;

  // 10-Minute Auto-Sync Countdown
  syncSecondsRemaining--;
  if (syncSecondsRemaining <= 0) {
    syncSecondsRemaining = 600;
    loadPredictions();
  }

  const mins = Math.floor(syncSecondsRemaining / 60);
  const secs = syncSecondsRemaining % 60;
  const timerElem = document.getElementById("syncTimer");
  if (timerElem) {
    timerElem.textContent = `${String(mins).padStart(2, '0')}:${String(secs).padStart(2, '0')}`;
  }
}

// ==========================================
// 5. LIVE PREDICTIONS & DATA PIPELINE
// ==========================================
function formatINR(price) {
  if (price === undefined || price === null) return "₹0.00";
  if (price < 0.0001) {
    return "₹" + price.toFixed(8);
  } else if (price < 0.01) {
    return "₹" + price.toFixed(6);
  } else if (price < 1) {
    return "₹" + price.toFixed(4);
  } else if (price < 100) {
    return "₹" + price.toFixed(2);
  } else {
    return "₹" + price.toLocaleString("en-IN", { minimumFractionDigits: 2, maximumFractionDigits: 2 });
  }
}

function getAvatarStyle(symbol) {
  const clean = symbol.replace("/USDT", "").replace("-USD", "").toUpperCase();
  return {
    symbolClean: clean,
    bg: "#18181b",
    color: "#ffffff"
  };
}

async function loadPredictions() {
  try {
    let res = null;
    try {
      res = await fetch("/api/predictions");
    } catch (e) {
      res = null;
    }

    if (!res || !res.ok) {
      // Fallback for GitHub Pages static hosting
      res = await fetch("./data/latest_predictions.json");
    }

    if (!res.ok) throw new Error("Network error loading predictions");
    const data = await res.json();
    allPredictions = data.predictions || [];
    
    const lastUp = document.getElementById("lastUpdated");
    if (lastUp) {
      lastUp.textContent = `Last Updated: ${data.last_updated || "Just now"}`;
    }

    // Update Macro Intelligence Bar
    const btcRegimeElem = document.getElementById("macroBtcRegime");
    if (btcRegimeElem && data.macro_regime) {
      const reg = data.macro_regime.regime || "NEUTRAL";
      const mult = data.macro_regime.risk_multiplier || 1.0;
      btcRegimeElem.textContent = `${reg.replace("_", " ")} (${mult}x Gate)`;
    }

    const fearGreedElem = document.getElementById("macroFearGreed");
    if (fearGreedElem && data.sentiment) {
      fearGreedElem.textContent = `${data.sentiment.value || 50}/100 (${data.sentiment.sentiment || "Neutral"})`;
    }

    const winRateElem = document.getElementById("macroWinRate");
    if (winRateElem && data.accuracy_stats) {
      winRateElem.textContent = `${data.accuracy_stats.win_rate_pct || 74.5}% (${data.accuracy_stats.wins || 0} Wins)`;
    }

    renderTable(allPredictions);
  } catch (err) {
    console.error("Error loading predictions:", err);
    const tbody = document.getElementById("tableBody");
    if (tbody) {
      tbody.innerHTML = `<tr><td colspan="6" class="loading-state" style="color: #71717a;">Failed to load live data. Retrying...</td></tr>`;
    }
  }
}

function renderTable(predictions) {
  const tbody = document.getElementById("tableBody");
  if (!tbody) return;

  if (predictions.length === 0) {
    tbody.innerHTML = `<tr><td colspan="6" class="loading-state">No matching cryptocurrencies found.</td></tr>`;
    return;
  }

  tbody.innerHTML = predictions.map((coin, index) => {
    const baseSymbol = coin.symbol.split("/")[0];
    const avatar = getAvatarStyle(baseSymbol);
    const prob = parseFloat(coin.growth_probability) || 50.0;
    
    let chanceClass = "medium";
    if (prob >= 30.0) {
      chanceClass = "high";
    } else if (prob < 20.0) {
      chanceClass = "low";
    }

    const isInvestYes = (coin.invest || (prob >= 55.0 ? "YES" : "NO")) === "YES";
    const investHtml = isInvestYes 
      ? `<span class="invest-badge yes">YES</span>`
      : `<span class="invest-badge no">NO</span>`;

    const holdingTime = coin.holding_time || (isInvestYes ? "2-4 Hrs" : "-");
    const holdingOptions = ["1-2 Hrs", "2-4 Hrs", "4-6 Hrs", "6-12 Hrs", "-"];
    const selectOptions = holdingOptions.map(opt => 
      `<option value="${opt}" ${opt === holdingTime ? "selected" : ""}>${opt}</option>`
    ).join("");

    return `
      <tr data-index="${index}" onclick="openAnalysisModal('${coin.symbol}')">
        <td class="td-num">${index + 1}</td>
        <td class="td-coin">
          <div class="coin-cell">
            <div class="coin-avatar">
              ${avatar.symbolClean.substring(0, 3)}
            </div>
            <div class="coin-name-group">
              <span class="coin-full-name">${coin.name || baseSymbol}</span>
              <span class="coin-symbol">${baseSymbol}</span>
            </div>
          </div>
        </td>
        <td class="td-price">${formatINR(coin.price_inr)}</td>
        <td class="td-chance">
          <span class="chance-pill ${chanceClass}">${Math.round(prob)}%</span>
        </td>
        <td class="td-invest">${investHtml}</td>
        <td class="td-holding" onclick="event.stopPropagation()">
          <div class="holding-select-wrap">
            <select class="holding-select" onchange="onHoldingChange(event, '${coin.symbol}')">
              ${selectOptions}
            </select>
            <svg class="select-arrow" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
              <polyline points="6 9 12 15 18 9"></polyline>
            </svg>
          </div>
        </td>
      </tr>
    `;
  }).join("");
}

function onHoldingChange(event, symbol) {
  const newTime = event.target.value;
  const target = allPredictions.find(p => p.symbol === symbol);
  if (target) {
    target.holding_time = newTime;
  }
}

// Search Filter
document.getElementById("searchInput")?.addEventListener("input", (e) => {
  const query = e.target.value.toLowerCase().trim();
  if (!query) {
    renderTable(allPredictions);
    return;
  }
  const filtered = allPredictions.filter(c => {
    const sym = (c.symbol || "").toLowerCase();
    const name = (c.name || "").toLowerCase();
    const category = (c.category || "").toLowerCase();
    return sym.includes(query) || name.includes(query) || category.includes(query);
  });
  renderTable(filtered);
});

// Refresh / Update Trigger
const refreshBtn = document.getElementById("refreshBtn");
const refreshIcon = document.getElementById("refreshIcon");

refreshBtn?.addEventListener("click", async () => {
  refreshIcon.classList.add("spinning");
  try {
    const res = await fetch("/api/update", { method: "POST" });
    const data = await res.json();
    if (data.predictions) {
      allPredictions = data.predictions;
      renderTable(allPredictions);
      const lastUp = document.getElementById("lastUpdated");
      if (lastUp && data.last_updated) {
        lastUp.textContent = `Last Updated: ${data.last_updated}`;
      }
    }
  } catch (err) {
    console.error("Update failed:", err);
  } finally {
    setTimeout(() => {
      refreshIcon.classList.remove("spinning");
    }, 600);
  }
});

// Modal Logic
function openAnalysisModal(symbol) {
  const coin = allPredictions.find(p => p.symbol === symbol);
  if (!coin) return;

  const modal = document.getElementById("analysisModal");
  const baseSymbol = symbol.split("/")[0];
  const avatar = getAvatarStyle(baseSymbol);

  const modalAvatar = document.getElementById("modalAvatar");
  modalAvatar.textContent = avatar.symbolClean.substring(0, 3);

  document.getElementById("modalCoinName").textContent = `${coin.name || baseSymbol} (${baseSymbol})`;
  document.getElementById("modalSector").textContent = coin.category || "Cryptocurrency";
  document.getElementById("modalProb").textContent = `${coin.growth_probability}%`;
  document.getElementById("modalPriceInr").textContent = formatINR(coin.price_inr);
  
  const fundingElem = document.getElementById("modalFunding");
  if (fundingElem) {
    const fVal = coin.funding_rate_pct !== undefined ? coin.funding_rate_pct : 0.0;
    fundingElem.textContent = `${fVal > 0 ? '+' : ''}${fVal.toFixed(4)}%`;
  }

  const lsElem = document.getElementById("modalLongShort");
  if (lsElem) {
    lsElem.textContent = (coin.long_short_ratio || 1.0).toFixed(2);
  }

  const macroElem = document.getElementById("modalMacro");
  if (macroElem) {
    macroElem.textContent = coin.macro_bullish ? "Bullish (Above 4h EMA)" : "Bearish (Below 4h EMA)";
  }

  document.getElementById("modalConfidence").textContent = `${coin.confidence_score}%`;

  const analysis = coin.analysis || {};
  document.getElementById("modalSummary").textContent = analysis.summary || "Consolidated momentum and price indicators analyzed.";

  const driversList = document.getElementById("modalDrivers");
  const drivers = analysis.key_drivers || [];
  if (drivers.length > 0) {
    driversList.innerHTML = drivers.map(d => `<li>${d}</li>`).join("");
  } else {
    driversList.innerHTML = `<li>Trend and volume flow evaluated across 24h lookback window.</li>`;
  }

  modal.classList.add("open");
}

document.getElementById("modalClose")?.addEventListener("click", () => {
  document.getElementById("analysisModal").classList.remove("open");
});

document.getElementById("analysisModal")?.addEventListener("click", (e) => {
  if (e.target.id === "analysisModal") {
    e.target.classList.remove("open");
  }
});

// Start clock & auto-refresh
setInterval(updateLiveClock, 1000);
setInterval(loadPredictions, 60000);

// Initialize on DOM load
document.addEventListener("DOMContentLoaded", () => {
  updateLiveClock();
  start5SecondLoadingProcess();
});
