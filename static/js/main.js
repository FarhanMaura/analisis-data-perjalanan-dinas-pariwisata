// Enhanced JavaScript dengan lebih banyak animasi dan interaksi

document.addEventListener("DOMContentLoaded", function () {
  // Initialize semua komponen
  initBackgroundAnimation();
  initMobileMenu();
  initFileUpload();
  initFormValidation();
  initScrollAnimations();
  initHoverEffects();
  initTypewriterEffect();
  initChartAnimations();
  initFlashMessages();
  initParticleEffects();
});

// Background Animation dengan bubbles
function initBackgroundAnimation() {
  const bgContainer = document.querySelector(".animated-bg");
  if (!bgContainer) return;

  // Create bubbles
  for (let i = 0; i < 6; i++) {
    const bubble = document.createElement("div");
    bubble.className = "bubble";
    bgContainer.appendChild(bubble);
  }
}

// Mobile Menu dengan animasi
function initMobileMenu() {
  const mobileMenuBtn = document.querySelector(".mobile-menu-btn");
  const navMenu = document.querySelector("nav ul");

  if (mobileMenuBtn && navMenu) {
    mobileMenuBtn.addEventListener("click", function () {
      const isActive = navMenu.classList.toggle("active");
      this.innerHTML = isActive ? "✕" : "☰";
      this.style.transform = isActive ? "rotate(180deg)" : "rotate(0deg)";

      // Animate menu items
      if (isActive) {
        const menuItems = navMenu.querySelectorAll("li");
        menuItems.forEach((item, index) => {
          item.style.animation = `slideInRight 0.5s ease ${index * 0.1}s both`;
        });
      }
    });
  }
}

// Enhanced File Upload dengan drag & drop
function initFileUpload() {
  const fileInputs = document.querySelectorAll('input[type="file"]');

  fileInputs.forEach((input) => {
    const fileInputContainer = input.closest(".file-input");
    if (!fileInputContainer) return;

    // Drag and drop functionality
    ["dragenter", "dragover", "dragleave", "drop"].forEach((eventName) => {
      fileInputContainer.addEventListener(eventName, preventDefaults, false);
    });

    function preventDefaults(e) {
      e.preventDefault();
      e.stopPropagation();
    }

    ["dragenter", "dragover"].forEach((eventName) => {
      fileInputContainer.addEventListener(eventName, highlight, false);
    });

    ["dragleave", "drop"].forEach((eventName) => {
      fileInputContainer.addEventListener(eventName, unhighlight, false);
    });

    function highlight() {
      fileInputContainer.style.background = "rgba(6, 182, 212, 0.2)";
      fileInputContainer.style.borderColor = "#3b82f6";
      fileInputContainer.style.transform = "scale(1.05)";
    }

    function unhighlight() {
      fileInputContainer.style.background = "";
      fileInputContainer.style.borderColor = "";
      fileInputContainer.style.transform = "";
    }

    fileInputContainer.addEventListener("drop", handleDrop, false);

    function handleDrop(e) {
      const dt = e.dataTransfer;
      const files = dt.files;
      input.files = files;
      updateFileNameDisplay(files[0].name, fileInputContainer);
    }

    input.addEventListener("change", function (e) {
      const fileName = e.target.files[0]
        ? e.target.files[0].name
        : "Pilih file";
      updateFileNameDisplay(fileName, fileInputContainer);
    });
  });
}

function updateFileNameDisplay(fileName, container) {
  const fileLabel = container.querySelector(".file-label");
  if (fileLabel) {
    fileLabel.innerHTML = `📁 ${fileName}`;

    // Celebration animation
    container.style.animation = "none";
    setTimeout(() => {
      container.style.animation = "pulse 0.6s ease";
    }, 10);

    // Add confetti effect for successful file selection
    if (fileName !== "Pilih file") {
      createConfetti(container);
    }
  }
}

// Enhanced Form Validation dengan animasi
function initFormValidation() {
  const forms = document.querySelectorAll("form");

  forms.forEach((form) => {
    form.addEventListener("submit", function (e) {
      let isValid = true;
      const requiredFields = this.querySelectorAll("[required]");

      requiredFields.forEach((field) => {
        if (!field.value.trim()) {
          showFieldError(field, "Field ini wajib diisi");
          isValid = false;
        } else {
          clearFieldError(field);

          // Special validation for year field
          if (field.type === "number" && field.name === "year") {
            const year = parseInt(field.value);
            if (year < 2000 || year > 2030) {
              showFieldError(field, "Tahun harus antara 2000 dan 2030");
              isValid = false;
            }
          }

          // Special validation for file input
          if (field.type === "file" && field.accept === ".csv") {
            const file = field.files[0];
            if (file && !file.name.toLowerCase().endsWith(".csv")) {
              showFieldError(
                field.closest(".file-input"),
                "File harus berformat CSV"
              );
              isValid = false;
            }
          }
        }
      });

      if (!isValid) {
        e.preventDefault();
        showNotification(
          "Harap perbaiki error pada form sebelum melanjutkan",
          "error"
        );

        // Shake animation for form
        form.style.animation = "none";
        setTimeout(() => {
          form.style.animation = "shake 0.5s ease";
        }, 10);
      } else {
        // Success animation
        showNotification("Form berhasil divalidasi! Memproses...", "success");
      }
    });
  });
}

// Field Error Handling
function showFieldError(field, message) {
  clearFieldError(field);

  field.style.borderColor = "#ef4444";

  const errorElement = document.createElement("div");
  errorElement.className = "field-error";
  errorElement.style.color = "#ef4444";
  errorElement.style.fontSize = "0.875rem";
  errorElement.style.marginTop = "5px";
  errorElement.textContent = message;

  field.parentNode.appendChild(errorElement);
}

function clearFieldError(field) {
  field.style.borderColor = "";

  const existingError = field.parentNode.querySelector(".field-error");
  if (existingError) {
    existingError.remove();
  }
}

// Scroll Animations
function initScrollAnimations() {
  const observerOptions = {
    threshold: 0.1,
    rootMargin: "0px 0px -50px 0px",
  };

  const observer = new IntersectionObserver(function (entries) {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        entry.target.style.opacity = "1";
        entry.target.style.transform = "translateY(0)";

        // Stagger animation for children
        if (entry.target.classList.contains("features")) {
          const cards = entry.target.querySelectorAll(".feature-card");
          cards.forEach((card, index) => {
            card.style.animationDelay = `${index * 0.2}s`;
          });
        }
      }
    });
  }, observerOptions);

  // Observe elements for animation
  const animatedElements = document.querySelectorAll(
    ".feature-card, .stat-card, .chart-container, .suggestion-item"
  );
  animatedElements.forEach((el) => {
    el.style.opacity = "0";
    el.style.transform = "translateY(50px)";
    el.style.transition = "opacity 0.8s ease, transform 0.8s ease";
    observer.observe(el);
  });
}

// Hover Effects
function initHoverEffects() {
  // Add hover effects to cards
  const cards = document.querySelectorAll(
    ".feature-card, .stat-card, .chart-container"
  );
  cards.forEach((card) => {
    card.addEventListener("mouseenter", function () {
      this.style.transform = "translateY(-15px) scale(1.02)";
    });

    card.addEventListener("mouseleave", function () {
      this.style.transform = "translateY(0) scale(1)";
    });
  });
}

// Typewriter Effect untuk hero text
function initTypewriterEffect() {
  const heroText = document.querySelector(".hero h1");
  if (heroText) {
    const text = heroText.textContent;
    heroText.textContent = "";
    let i = 0;

    function typeWriter() {
      if (i < text.length) {
        heroText.textContent += text.charAt(i);
        i++;
        setTimeout(typeWriter, 100);
      }
    }

    // Start typewriter effect
    setTimeout(typeWriter, 1000);
  }
}

// Chart Animations
function initChartAnimations() {
  // This will be handled by the chart initialization in dashboard.html
  console.log("Chart animations ready");
}

// Enhanced Flash Messages
function initFlashMessages() {
  const flashMessages = document.querySelectorAll(".flash-message");

  flashMessages.forEach((message) => {
    // Add close button
    const closeBtn = document.createElement("button");
    closeBtn.innerHTML = "✕";
    closeBtn.style.background = "none";
    closeBtn.style.border = "none";
    closeBtn.style.fontSize = "1.4rem";
    closeBtn.style.cursor = "pointer";
    closeBtn.style.marginLeft = "auto";
    closeBtn.style.color = "inherit";
    closeBtn.style.transition = "transform 0.3s ease";

    closeBtn.addEventListener("mouseenter", function () {
      this.style.transform = "scale(1.2) rotate(90deg)";
    });

    closeBtn.addEventListener("mouseleave", function () {
      this.style.transform = "scale(1) rotate(0deg)";
    });

    closeBtn.addEventListener("click", function () {
      message.style.opacity = "0";
      message.style.transform = "translateX(100%)";
      setTimeout(() => {
        if (message.parentNode) {
          message.parentNode.removeChild(message);
        }
      }, 500);
    });

    message.appendChild(closeBtn);

    // Auto-hide setelah 6 detik
    setTimeout(() => {
      if (message.parentNode) {
        message.style.opacity = "0";
        message.style.transform = "translateX(100%)";
        setTimeout(() => {
          if (message.parentNode) {
            message.parentNode.removeChild(message);
          }
        }, 500);
      }
    }, 6000);
  });
}

// Particle Effects untuk konfetti
function initParticleEffects() {
  window.createConfetti = function (element) {
    const confettiCount = 30;
    const colors = ["#3b82f6", "#06b6d4", "#1e40af", "#67e8f9"];

    for (let i = 0; i < confettiCount; i++) {
      const confetti = document.createElement("div");
      confetti.style.position = "absolute";
      confetti.style.width = "8px";
      confetti.style.height = "8px";
      confetti.style.background =
        colors[Math.floor(Math.random() * colors.length)];
      confetti.style.borderRadius = "50%";
      confetti.style.left = "50%";
      confetti.style.top = "50%";
      confetti.style.pointerEvents = "none";
      confetti.style.zIndex = "1000";

      element.appendChild(confetti);

      // Animate confetti
      const angle = Math.random() * Math.PI * 2;
      const velocity = 2 + Math.random() * 2;
      const rotation = Math.random() * 360;

      confetti.animate(
        [
          {
            transform: `translate(-50%, -50%) rotate(0deg)`,
            opacity: 1,
          },
          {
            transform: `translate(${Math.cos(angle) * 100}px, ${
              Math.sin(angle) * 100
            }px) rotate(${rotation}deg)`,
            opacity: 0,
          },
        ],
        {
          duration: 1000 + Math.random() * 1000,
          easing: "cubic-bezier(0.25, 0.46, 0.45, 0.94)",
        }
      ).onfinish = () => {
        confetti.remove();
      };
    }
  };
}

// Enhanced Notification System
function showNotification(message, type = "info") {
  const notification = document.createElement("div");
  notification.className = `flash-message flash-${type}`;
  notification.innerHTML = `
        <i style="font-size: 1.4rem;">${getNotificationIcon(type)}</i>
        <span style="flex: 1;">${message}</span>
    `;

  const flashContainer =
    document.querySelector(".flash-messages") || createFlashContainer();
  flashContainer.appendChild(notification);

  // Animate in
  setTimeout(() => {
    notification.style.opacity = "1";
    notification.style.transform = "translateX(0)";
  }, 10);

  // Auto remove setelah 5 detik
  setTimeout(() => {
    if (notification.parentNode) {
      notification.style.opacity = "0";
      notification.style.transform = "translateX(100%)";
      setTimeout(() => {
        if (notification.parentNode) {
          notification.parentNode.removeChild(notification);
        }
      }, 500);
    }
  }, 5000);

  // Add close button
  const closeBtn = document.createElement("button");
  closeBtn.innerHTML = "✕";
  closeBtn.style.background = "none";
  closeBtn.style.border = "none";
  closeBtn.style.fontSize = "1.4rem";
  closeBtn.style.cursor = "pointer";
  closeBtn.style.marginLeft = "15px";
  closeBtn.style.color = "inherit";
  closeBtn.style.transition = "transform 0.3s ease";

  closeBtn.addEventListener("click", function () {
    notification.style.opacity = "0";
    notification.style.transform = "translateX(100%)";
    setTimeout(() => {
      if (notification.parentNode) {
        notification.parentNode.removeChild(notification);
      }
    }, 500);
  });

  notification.appendChild(closeBtn);
}

function createFlashContainer() {
  const container = document.createElement("div");
  container.className = "flash-messages";
  document.querySelector(".container").prepend(container);
  return container;
}

function getNotificationIcon(type) {
  const icons = {
    success: "🎉",
    error: "❌",
    warning: "⚠️",
    info: "ℹ️",
  };
  return icons[type] || icons.info;
}

// Utility Functions
function formatNumber(num) {
  return new Intl.NumberFormat("id-ID").format(num);
}

// Add CSS for shake animation
const style = document.createElement("style");
style.textContent = `
    @keyframes shake {
        0%, 100% { transform: translateX(0); }
        25% { transform: translateX(-10px); }
        75% { transform: translateX(10px); }
    }
    
    @keyframes slideInRight {
        from {
            opacity: 0;
            transform: translateX(50px);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }
    
    .field-error {
        color: #ef4444;
        font-size: 0.875rem;
        margin-top: 5px;
    }
`;
document.head.appendChild(style);

// Export functions untuk penggunaan di file lain
window.TourismApp = {
  showNotification,
  formatNumber,
  createConfetti,
};
