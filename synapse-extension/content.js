// Content script for visual feedback

// Listen for capture trigger
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.action === 'showCaptureFeedback') {
    showCaptureFeedback();
  }
});

function showCaptureFeedback() {
  // Create subtle flash overlay
  const flash = document.createElement('div');
  flash.id = 'synapse-capture-flash';
  flash.className = 'synapse-flash';
  document.body.appendChild(flash);

  // Play capture sound
  playSound();

  // Show toast notification
  showToast();

  // Remove flash after animation
  setTimeout(() => {
    flash.remove();
  }, 400);
}

function showToast() {
  // Create toast element
  const toast = document.createElement('div');
  toast.className = 'synapse-toast';
  toast.innerHTML = `
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
      <polyline points="20 6 9 17 4 12"></polyline>
    </svg>
    <span>Captured</span>
  `;

  document.body.appendChild(toast);

  // Animate in
  setTimeout(() => toast.classList.add('show'), 10);

  // Remove after 2 seconds
  setTimeout(() => {
    toast.classList.remove('show');
    setTimeout(() => toast.remove(), 300);
  }, 2000);
}

function playSound() {
  // Create audio element
  const audio = new Audio(chrome.runtime.getURL('capture.mp3'));
  audio.volume = 0.3; // Subtle volume
  audio.play().catch(() => {
    // Sound might be blocked, that's OK
  });
}
