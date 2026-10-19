/**
 * CampusPulse - Real-Time Engine & Client Interactions
 */

document.addEventListener('DOMContentLoaded', () => {
  initImagePreview();
  initOtherLocationToggle();
  initHostelLocationAutofill();
  initNotificationBell();
  initRealtimeSSE();
  initToastAutoDismiss();
  initFaqAccordion();
  initScreenScrollSpy();
  initScrollReveal();
});

/**
 * Topbar Notification Bell Popover Controller
 */
function initNotificationBell() {
  const bellBtn = document.getElementById('notifBellBtn');
  const popover = document.getElementById('notifPopover');
  const markReadBtn = document.getElementById('markReadBtn');
  const badgeDot = document.getElementById('notifBadgeDot');

  if (!bellBtn || !popover) return;

  bellBtn.addEventListener('click', (e) => {
    e.stopPropagation();
    const isShowing = popover.style.display === 'block';
    popover.style.display = isShowing ? 'none' : 'block';
  });

  document.addEventListener('click', (e) => {
    if (!popover.contains(e.target) && e.target !== bellBtn) {
      popover.style.display = 'none';
    }
  });

  if (markReadBtn) {
    markReadBtn.addEventListener('click', async (e) => {
      e.preventDefault();
      try {
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value || '';
        await fetch('/api/notifications/mark-read/', {
          method: 'POST',
          headers: {
            'X-CSRFToken': csrfToken,
            'Content-Type': 'application/json'
          }
        });
        if (badgeDot) badgeDot.style.display = 'none';
      } catch (err) {
        console.error('Failed to mark notifications read', err);
      }
    });
  }
}

/**
 * 1. Native Image / Mobile Camera Preview Handler
 */
function initImagePreview() {
  const photoInput = document.getElementById('defectPhotoInput');
  const previewBox = document.getElementById('imagePreviewContainer');
  const previewImg = document.getElementById('imagePreviewImg');
  const removeBtn = document.getElementById('removePreviewBtn');

  if (!photoInput || !previewBox || !previewImg) return;

  photoInput.addEventListener('change', (e) => {
    const file = e.target.files[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = (event) => {
        previewImg.src = event.target.result;
        previewBox.style.display = 'block';
      };
      reader.readAsDataURL(file);
    }
  });

  if (removeBtn) {
    removeBtn.addEventListener('click', (e) => {
      e.preventDefault();
      photoInput.value = '';
      previewImg.src = '';
      previewBox.style.display = 'none';
    });
  }
}

/**
 * 2. Location Type "Other" Dynamic Field Toggle
 */
function initOtherLocationToggle() {
  const select = document.getElementById('locationTypeSelect');
  const otherGroup = document.getElementById('otherLocationGroup');
  const otherInput = document.getElementById('otherLocationInput');

  if (!select || !otherGroup) return;

  function checkToggle() {
    if (select.value === 'Other') {
      otherGroup.style.display = 'block';
      if (otherInput) otherInput.setAttribute('required', 'required');
    } else {
      otherGroup.style.display = 'none';
      if (otherInput) {
        otherInput.removeAttribute('required');
        otherInput.value = '';
      }
    }
  }

  select.addEventListener('change', checkToggle);
  checkToggle();
}

/**
 * 2b. Registered Student Hostel Coordinates Auto-fill Engine
 */
function initHostelLocationAutofill() {
  const select = document.getElementById('locationTypeSelect');
  const bldInput = document.getElementById('building_or_block');
  const roomInput = document.getElementById('room_or_area');
  const floorInput = document.getElementById('floor');
  const autofillNotice = document.getElementById('hostelAutofillNotice');
  const studentData = document.getElementById('studentProfileData');
  const quickFillBtn = document.getElementById('btnAutofillHostel');
  const deptSelect = document.getElementById('department_id');

  if (!select || !bldInput || !roomInput || !studentData) return;

  const defaultHostel = (studentData.getAttribute('data-hostel') || '').trim();
  const defaultRoom = (studentData.getAttribute('data-room') || '').trim();

  // Helper to infer floor from room string (e.g. B-1005 -> 10, 302 -> 3)
  function inferFloor(roomStr) {
    if (!roomStr) return '';
    const match = roomStr.match(/\b([A-Z]-)?(\d{1,4})\b/i);
    if (match && match[2]) {
      const num = match[2];
      if (num.length >= 3) {
        return num.slice(0, num.length - 2); // e.g., 1005 -> 10, 302 -> 3
      }
    }
    return '';
  }

  function applyHostelAutofill(flashHighlight = false) {
    if (!defaultHostel && !defaultRoom) return;

    if (defaultHostel) {
      bldInput.value = defaultHostel;
      const bldLabel = document.getElementById('bldgDropdownSelectedText');
      if (bldLabel) {
        bldLabel.innerHTML = `<span style="font-family: var(--font-mono); font-weight: 700; color: var(--text-primary); margin-right: 6px;">${defaultHostel}</span> <span style="color: var(--text-secondary); font-weight: 500;">(Registered Hostel)</span>`;
        bldLabel.style.color = 'var(--text-primary)';
      }
    }
    if (defaultRoom) roomInput.value = defaultRoom;
    if (floorInput && !floorInput.value) {
      const inferred = inferFloor(defaultRoom);
      if (inferred) floorInput.value = inferred;
    }

    if (autofillNotice) {
      autofillNotice.style.display = 'inline-flex';
    }

    if (flashHighlight) {
      const trigger = document.getElementById('bldgDropdownTrigger') || bldInput;
      [trigger, roomInput].forEach(inp => {
        inp.style.transition = 'box-shadow 0.3s ease, border-color 0.3s ease';
        inp.style.borderColor = 'var(--orange-primary)';
        inp.style.boxShadow = '0 0 0 3px rgba(255, 87, 34, 0.2)';
        setTimeout(() => {
          inp.style.borderColor = '';
          inp.style.boxShadow = '';
        }, 1200);
      });
    }
  }

  function handleLocationChange() {
    if (select.value === 'Hostel') {
      applyHostelAutofill(true);
    } else {
      if (autofillNotice) {
        autofillNotice.style.display = 'none';
      }
      // If the fields currently equal the default hostel/room, reset them for fresh entry
      if (bldInput.value === defaultHostel && defaultHostel) {
        bldInput.value = '';
        const bldLabel = document.getElementById('bldgDropdownSelectedText');
        if (bldLabel) {
          bldLabel.innerHTML = 'Select campus block or hostel...';
          bldLabel.style.color = '#9CA3AF';
        }
      }
      if (roomInput.value === defaultRoom && defaultRoom) {
        roomInput.value = '';
      }
    }
  }

  select.addEventListener('change', handleLocationChange);

  if (quickFillBtn) {
    quickFillBtn.addEventListener('click', (e) => {
      e.preventDefault();
      select.value = 'Hostel';
      applyHostelAutofill(true);
    });
  }

  // If user selects HVAC/AC department, and location type has not been set away from default, suggest/fill Hostel
  if (deptSelect) {
    deptSelect.addEventListener('change', () => {
      const selectedText = (deptSelect.options[deptSelect.selectedIndex]?.text || '').toLowerCase();
      if ((selectedText.includes('hvac') || selectedText.includes('ac') || selectedText.includes('air cond')) && defaultHostel && defaultRoom) {
        if (!bldInput.value || bldInput.value === defaultHostel) {
          select.value = 'Hostel';
          applyHostelAutofill(true);
        }
      }
    });
  }

  // Run on initial load if location type is Hostel
  if (select.value === 'Hostel') {
    applyHostelAutofill(false);
  }
}

/**
 * 3. Real-Time Server-Sent Events (SSE) Push Engine
 */
function initRealtimeSSE() {
  // Only connect if user is a student on the dashboard or report page
  const sseMeta = document.querySelector('meta[name="realtime-stream"]');
  if (!sseMeta) return;

  const streamUrl = sseMeta.getAttribute('content');
  if (!streamUrl) return;

  let eventSource = null;

  function connect() {
    eventSource = new EventSource(streamUrl);

    eventSource.onopen = () => {
      console.log('[CampusPulse] Connected to Real-Time Event Stream');
      const ind = document.getElementById('liveIndicator');
      if (ind) ind.style.display = 'flex';
    };

    eventSource.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        if (data.type === 'issue_resolved') {
          handleIssueResolvedEvent(data);
        }
      } catch (err) {
        console.debug('SSE heartbeat:', event.data);
      }
    };

    eventSource.onerror = (err) => {
      console.warn('SSE connection interrupted, retrying in 5s...', err);
      eventSource.close();
      setTimeout(connect, 5000);
    };
  }

  connect();
}

/**
 * Handles incoming issue_resolved real-time event
 */
function handleIssueResolvedEvent(data) {
  // 1. Play pleasant audio chime using Web Audio API
  playResolutionChime();

  // 2. Show floating toast (Clean, professional, no emojis)
  showToast(
    `Defect Resolved: ${data.ticket_id}`,
    `${data.location}: ${data.message}`
  );

  // 2b. Show bell notification dot and append item
  const badgeDot = document.getElementById('notifBadgeDot');
  if (badgeDot) badgeDot.style.display = 'block';

  const container = document.getElementById('notifListContainer');
  if (container) {
    const item = document.createElement('div');
    item.className = 'notif-popover-item';
    item.style.cssText = 'padding: 0.6rem 0.5rem; border-bottom: 1px solid #F3F4F6;';
    item.innerHTML = `
      <div style="font-weight: 700; font-size: 0.8125rem; color: var(--text-primary);">${data.location}</div>
      <div style="font-size: 0.75rem; color: var(--text-secondary); margin-top: 2px;">${data.message}</div>
      <div style="font-size: 0.7rem; color: var(--text-muted); margin-top: 4px;">Just now</div>
    `;
    container.prepend(item);
  }

  // 3. Dynamically update dashboard KPI numbers if present
  const pendingEl = document.getElementById('kpiPendingCount');
  const fulfilledEl = document.getElementById('kpiFulfilledCount');
  if (pendingEl && fulfilledEl) {
    let p = parseInt(pendingEl.innerText) || 0;
    let f = parseInt(fulfilledEl.innerText) || 0;
    if (p > 0) pendingEl.innerText = Math.max(0, p - 1);
    fulfilledEl.innerText = f + 1;
  }

  // 4. Update the card badge in real time if visible on the student's screen
  const ticketCard = document.getElementById(`ticket-card-${data.ticket_id}`);
  if (ticketCard) {
    const badge = ticketCard.querySelector('.status-badge');
    if (badge) {
      badge.className = 'badge badge-resolved status-badge';
      badge.innerHTML = '● Fulfilled / Resolved';
    }
  }
}

/**
 * Synthesizes a futuristic celebration chime
 */
function playResolutionChime() {
  try {
    const ctx = new (window.AudioContext || window.webkitAudioContext)();
    const osc = ctx.createOscillator();
    const gain = ctx.createGain();

    osc.type = 'sine';
    osc.frequency.setValueAtTime(523.25, ctx.currentTime); // C5
    osc.frequency.exponentialRampToValueAtTime(783.99, ctx.currentTime + 0.15); // G5
    osc.frequency.exponentialRampToValueAtTime(1046.50, ctx.currentTime + 0.3); // C6

    gain.gain.setValueAtTime(0.2, ctx.currentTime);
    gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + 0.6);

    osc.connect(gain);
    gain.connect(ctx.destination);

    osc.start();
    osc.stop(ctx.currentTime + 0.6);
  } catch (e) {
    // AudioContext might be blocked until user gesture, safely ignore
  }
}

/**
 * Toast notification renderer (Dark Obsidian Glass card with accent dot & dismiss)
 */
function showToast(title, message, type = 'success') {
  let container = document.getElementById('toast-container');
  if (!container) {
    container = document.createElement('div');
    container.id = 'toast-container';
    container.className = 'toast-hub';
    document.body.appendChild(container);
  }

  const toast = document.createElement('div');
  toast.className = `toast-card toast-${type}`;
  toast.innerHTML = `
    <div class="toast-icon">
      ${type === 'error' ? 
        `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="8" x2="12" y2="12"></line><line x1="12" y1="16" x2="12.01" y2="16"></line></svg>` : 
        `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><circle cx="12" cy="12" r="10"></circle><polyline points="16 12 12 8 8 12"></polyline></svg>`}
    </div>
    <div class="toast-content">
      <div class="toast-title">${escapeHtml(title)}</div>
      <div class="toast-text">${escapeHtml(message)}</div>
    </div>
    <button type="button" class="toast-close" onclick="this.closest('.toast-card').remove();" aria-label="Dismiss notification">
      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><line x1="18" y1="6" x2="6" y2="18"></line><line x1="6" y1="6" x2="18" y2="18"></line></svg>
    </button>
  `;

  container.appendChild(toast);

  // Auto remove after 5 seconds
  setTimeout(() => {
    toast.style.transition = 'opacity 0.4s ease, transform 0.4s ease';
    toast.style.opacity = '0';
    toast.style.transform = 'translateY(-16px)';
    setTimeout(() => toast.remove(), 400);
  }, 5000);
}

/**
 * Auto-dismiss any server-rendered Django flash messages after 4.5s
 */
function initToastAutoDismiss() {
  const cards = document.querySelectorAll('.toast-card[data-autodismiss="true"]');
  cards.forEach((card, index) => {
    setTimeout(() => {
      card.style.transition = 'opacity 0.4s ease, transform 0.4s ease';
      card.style.opacity = '0';
      card.style.transform = 'translateY(-16px)';
      setTimeout(() => card.remove(), 400);
    }, 4500 + (index * 500));
  });
}

/**
 * FAQ Interactive Accordion
 */
function initFaqAccordion() {
  const items = document.querySelectorAll('.faq-accordion-item');
  items.forEach(item => {
    const btn = item.querySelector('.faq-question-btn');
    if (!btn) return;
    btn.addEventListener('click', () => {
      const isOpen = item.classList.contains('is-open');
      // Smoothly close any other opened FAQ items
      items.forEach(otherItem => {
        if (otherItem !== item) {
          otherItem.classList.remove('is-open');
        }
      });
      // Toggle the clicked FAQ item
      if (isOpen) {
        item.classList.remove('is-open');
      } else {
        item.classList.add('is-open');
      }
    });
  });
}

/**
 * Screen Scroll Spy for Floating Section Dots
 */
function initScreenScrollSpy() {
  const screens = document.querySelectorAll('.landing-screen');
  const dots = document.querySelectorAll('.screen-dot');
  if (!screens.length || !dots.length) return;

  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        const id = entry.target.id;
        dots.forEach(dot => {
          if (dot.getAttribute('href') === `#${id}`) {
            dot.classList.add('active');
          } else {
            dot.classList.remove('active');
          }
        });
      }
    });
  }, { threshold: 0.45 });

  screens.forEach(screen => observer.observe(screen));
}

/**
 * 4. Admin Resolution Modal Handlers
 */
function openResolveModal(issueId, ticketId, title, locationStr) {
  const modal = document.getElementById('resolveModal');
  const form = document.getElementById('resolveForm');
  const ticketDisplay = document.getElementById('modalTicketId');
  const titleDisplay = document.getElementById('modalIssueTitle');
  const locDisplay = document.getElementById('modalIssueLoc');

  if (!modal || !form) return;

  form.action = `/admin/issues/${issueId}/resolve/`;
  if (ticketDisplay) ticketDisplay.innerText = ticketId;
  if (titleDisplay) titleDisplay.innerText = title;
  if (locDisplay) locDisplay.innerText = locationStr;

  modal.style.display = 'flex';
}

function closeResolveModal() {
  const modal = document.getElementById('resolveModal');
  if (modal) modal.style.display = 'none';
}

// Close modal on Escape or overlay click
window.addEventListener('keydown', (e) => {
  if (e.key === 'Escape') closeResolveModal();
});

const modalOverlay = document.getElementById('resolveModal');
if (modalOverlay) {
  modalOverlay.addEventListener('click', (e) => {
    if (e.target === modalOverlay) closeResolveModal();
  });
}

function escapeHtml(str) {
  const div = document.createElement('div');
  div.innerText = str;
  return div.innerHTML;
}

/**
 * Scroll Reveal Engine
 */
function initScrollReveal() {
  const elements = document.querySelectorAll('.reveal-on-scroll');
  if (!elements.length) return;

  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('is-revealed');
      }
    });
  }, {
    threshold: 0.12,
    rootMargin: '0px 0px -40px 0px'
  });

  elements.forEach(el => observer.observe(el));
}
