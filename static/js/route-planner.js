// Physical Reporting Route Planner & Document Checklist Controller

let currentCollege = '';
let currentHomeCity = '';
let currentCategory = '';
let currentTfw = 'N';

function openRoutePlanner(collegeName, category, homeCity, tfw = 'N') {
    currentCollege = collegeName || '';
    
    // Attempt to pull homeCity from page if it is not explicitly provided or is 'All'
    if (!homeCity || homeCity === 'All') {
        const pageHomeCity = document.getElementById('home_city')?.value;
        currentHomeCity = pageHomeCity && pageHomeCity !== 'All' ? pageHomeCity : 'All';
    } else {
        currentHomeCity = homeCity;
    }

    // Attempt to pull category from page if it is not explicitly provided
    if (!category) {
        const pageCategory = document.getElementById('category')?.value;
        currentCategory = pageCategory || 'UR';
    } else {
        currentCategory = category;
    }
    
    currentTfw = tfw || 'N';

    // Prefill the modal controls dropdowns
    const citySelect = document.getElementById('modal_home_city');
    if (citySelect) citySelect.value = currentHomeCity;

    const catSelect = document.getElementById('modal_category');
    if (catSelect) catSelect.value = currentCategory;

    const tfwSelect = document.getElementById('modal_tfw');
    if (tfwSelect) tfwSelect.value = currentTfw;

    // Reset view to Route tab
    switchModalTab('route');

    // Fetch details
    fetchRouteDetails();

    // Show the modal
    const modal = document.getElementById('route-planner-modal');
    if (modal) {
        modal.style.display = 'flex';
        document.body.style.overflow = 'hidden'; // Disable page background scroll
    }
}

function closeRoutePlanner() {
    const modal = document.getElementById('route-planner-modal');
    if (modal) {
        modal.style.display = 'none';
        document.body.style.overflow = ''; // Re-enable page scroll
    }
}

function recalculateRoute() {
    const citySelect = document.getElementById('modal_home_city');
    const catSelect = document.getElementById('modal_category');
    const tfwSelect = document.getElementById('modal_tfw');

    if (citySelect) currentHomeCity = citySelect.value;
    if (catSelect) currentCategory = catSelect.value;
    if (tfwSelect) currentTfw = tfwSelect.value;

    fetchRouteDetails();
}

function switchModalTab(tabName) {
    // Remove active classes
    document.querySelectorAll('.modal-tab-btn').forEach(btn => btn.classList.remove('active'));
    document.querySelectorAll('.modal-tab-pane').forEach(pane => pane.classList.remove('active'));

    // Add active classes
    const targetBtn = document.getElementById(`tab-btn-${tabName}`);
    const targetPane = document.getElementById(`tab-pane-${tabName}`);

    if (targetBtn) targetBtn.classList.add('active');
    if (targetPane) targetPane.classList.add('active');
}

function fetchRouteDetails() {
    if (!currentCollege) return;

    // Set loading states
    const stepsContainer = document.getElementById('route-steps-container');
    if (stepsContainer) {
        stepsContainer.innerHTML = `
            <div style="display:flex; flex-direction:column; align-items:center; justify-content:center; padding: 40px 0;">
                <div class="loader-spinner" style="border-top-color:var(--primary); width:36px; height:36px;"></div>
                <p style="font-size:0.85rem; color:var(--muted); margin-top:10px;">Generating route details...</p>
            </div>
        `;
    }

    document.getElementById('route-distance-val').textContent = 'Calculating...';
    document.getElementById('route-dest-val').textContent = 'Locating...';

    // Populate checklist with loading placeholder
    const docsContainer = document.getElementById('checklist-docs-container');
    if (docsContainer) {
        docsContainer.innerHTML = `
            <div style="text-align:center; padding: 30px 0; color:var(--muted); font-size:0.85rem;">
                Generating custom checklist...
            </div>
        `;
    }

    // Build API url
    const url = `/api/v1/college/route-info?college_name=${encodeURIComponent(currentCollege)}&home_city=${encodeURIComponent(currentHomeCity)}&category=${encodeURIComponent(currentCategory)}&tfw=${encodeURIComponent(currentTfw)}`;

    fetch(url)
        .then(response => {
            if (!response.ok) throw new Error('Failed to fetch route information');
            return response.json();
        })
        .then(data => {
            // Update Title
            const titleSpan = document.getElementById('route-modal-title');
            if (titleSpan) titleSpan.textContent = `Reporting Guide: ${data.college_name}`;

            // Update Dist & Dest
            document.getElementById('route-distance-val').textContent = data.distance_text || '—';
            document.getElementById('route-dest-val').textContent = data.dest_city || 'Madhya Pradesh';

            // Render Timeline Steps
            renderTimeline(data.route_steps);

            // Render Checklist
            renderChecklist(data.documents);

            // Render Contacts
            renderContacts(data.contact);
        })
        .catch(err => {
            console.error(err);
            if (stepsContainer) {
                stepsContainer.innerHTML = `
                    <div style="text-align:center; padding:20px; color:#ef4444; font-size:0.9rem;">
                        <i class="fas fa-exclamation-circle" style="font-size:1.5rem; margin-bottom:8px;"></i>
                        <p>Unable to load physical reporting information. Please try again later.</p>
                    </div>
                `;
            }
        });
}

function renderTimeline(steps) {
    const container = document.getElementById('route-steps-container');
    if (!container) return;

    container.innerHTML = '';
    if (!steps || steps.length === 0) {
        container.innerHTML = '<p style="text-align:center; color:var(--muted); padding: 20px;">No transit instructions available.</p>';
        return;
    }

    steps.forEach((step, idx) => {
        const isFirst = idx === 0;
        const isLast = idx === steps.length - 1;
        
        let markerIcon = '<i class="fas fa-arrow-down" style="font-size: 0.65rem; color:#fff;"></i>';
        if (isFirst) {
            markerIcon = '<i class="fas fa-home" style="font-size: 0.65rem; color:#fff;"></i>';
        } else if (isLast) {
            markerIcon = '<i class="fas fa-flag-checkered" style="font-size: 0.65rem; color:#fff;"></i>';
        }

        const stepDiv = document.createElement('div');
        stepDiv.className = `timeline-step ${isLast ? 'success' : 'active'}`;
        stepDiv.innerHTML = `
            <div class="timeline-marker">${markerIcon}</div>
            <div class="timeline-content">
                <p>${step}</p>
            </div>
        `;
        container.appendChild(stepDiv);
    });
}

function renderChecklist(documents) {
    const container = document.getElementById('checklist-docs-container');
    if (!container) return;

    container.innerHTML = '';
    if (!documents || documents.length === 0) {
        container.innerHTML = '<p style="text-align:center; color:var(--muted); padding:20px;">No specific documents required.</p>';
        return;
    }

    documents.forEach((doc, idx) => {
        const storageKey = `route_chk_${currentCollege.replace(/[^a-zA-Z0-9]/g, '_')}_${doc.name.replace(/[^a-zA-Z0-9]/g, '_')}`;
        const isChecked = localStorage.getItem(storageKey) === 'true';

        const card = document.createElement('div');
        card.className = `checklist-item-card ${isChecked ? 'checked' : ''}`;
        card.onclick = function() {
            toggleChecklistDoc(this, storageKey);
        };

        card.innerHTML = `
            <input type="checkbox" id="chk-doc-${idx}" ${isChecked ? 'checked' : ''} onclick="event.stopPropagation(); toggleChecklistDoc(this.closest('.checklist-item-card'), '${storageKey}')">
            <div class="doc-info">
                <span class="doc-name">${doc.name}</span>
                <span class="doc-desc">${doc.desc}</span>
            </div>
        `;
        container.appendChild(card);
    });
}

function toggleChecklistDoc(cardEl, storageKey) {
    const checkbox = cardEl.querySelector('input[type="checkbox"]');
    const newState = !checkbox.checked;
    
    checkbox.checked = newState;
    if (newState) {
        cardEl.classList.add('checked');
        localStorage.setItem(storageKey, 'true');
    } else {
        cardEl.classList.remove('checked');
        localStorage.setItem(storageKey, 'false');
    }
}

// Render Contacts in the third tab
function renderContacts(contact) {
    if (!contact) return;
    
    const addr = document.getElementById('contact-address-val');
    const phone = document.getElementById('contact-phone-val');
    const email = document.getElementById('contact-email-val');
    const web = document.getElementById('contact-website-val');

    if (addr) addr.textContent = contact.address || '—';
    if (phone) phone.textContent = contact.phone || '—';
    if (email) email.textContent = contact.email || '—';
    
    if (web) {
        if (contact.website) {
            web.href = contact.website;
            if (contact.website.includes('google.com/search')) {
                web.textContent = 'Search official site on Google';
            } else {
                web.textContent = contact.website.replace('https://', '').replace('http://', '').replace('www.', '');
            }
            web.style.pointerEvents = '';
        } else {
            web.removeAttribute('href');
            web.textContent = '—';
            web.style.pointerEvents = 'none';
        }
    }
}

// Close modal on escape key or clicking outside
document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape') closeRoutePlanner();
});

document.addEventListener('click', function(e) {
    const modal = document.getElementById('route-planner-modal');
    if (modal && e.target === modal) closeRoutePlanner();
});
