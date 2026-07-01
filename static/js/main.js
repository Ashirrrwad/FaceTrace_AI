document.addEventListener('DOMContentLoaded', () => {
    // Elements
    const generateBtn = document.getElementById('generate-btn');
    const descriptionInput = document.getElementById('description');
    const ageSlider = document.getElementById('age-slider');
    const ageVal = document.getElementById('age-val');
    const genderSelect = document.getElementById('gender-select');
    const styleSelect = document.getElementById('style-select');
    const stageMonitor = document.getElementById('stage-monitor');
    const progressBar = document.getElementById('main-progress');
    const primaryImage = document.getElementById('primary-image');
    const sketchDisplay = document.getElementById('sketch-display');   // spec-required alias
    const imagePlaceholder = document.getElementById('image-placeholder');
    const confidenceBadge = document.getElementById('confidence-badge');
    const aiReportText = document.getElementById('ai-report-text');
    const historyList = document.getElementById('history-list');
    const caseNameInput = document.getElementById('case-name-input');
    const caseIdInput = document.getElementById('case-id-input');       // new Case ID field
    const caseIdDisplay = document.getElementById('current-case-id');
    const analysisReport = document.getElementById('analysis-report');
    const hudOverlay = document.getElementById('hud-overlay');
    const compareBtn = document.getElementById('compare-btn');
    const matchesPanel = document.getElementById('matches-panel');
    const matchesList = document.getElementById('matches-list');
    const logBody = document.getElementById('live-logs');
    
    let history = [];

    
    const generateCaseId = () => `CASE: #${Math.floor(Math.random() * 9000) + 1000}-${Math.random().toString(36).substring(2, 5).toUpperCase()}`;

    const setStage = (stageNum) => {
        const stages = document.querySelectorAll('.stage');
        stages.forEach(s => s.classList.remove('active'));
        const current = document.querySelector(`.stage[data-stage="${stageNum}"]`);
        if (current) current.classList.add('active');
        progressBar.style.width = `${(stageNum / 3) * 100}%`;
    };

    const addToHistory = (caseData) => {
        const item = document.createElement('div');
        item.className = 'history-item';
        item.innerHTML = `
            <div class="hist-header">
                <span class="case-id">${caseData.id}</span>
                <span class="case-name-tag">${caseData.name || 'UNNAMED_CASE'}</span>
            </div>
            <span class="case-desc">${caseData.description.substring(0, 35)}...</span>
        `;
        item.onclick = () => restoreCase(caseData);
        historyList.prepend(item);
        if (historyList.querySelector('.empty-state')) historyList.querySelector('.empty-state').remove();
    };

    const restoreCase = (data) => {
        currentCaseData = data;
        
        const homeNav = document.querySelector('[data-section="home"]');
        if (homeNav) homeNav.click();

        primaryImage.src = data.image;
        primaryImage.classList.remove('hidden');
        imagePlaceholder.classList.add('hidden');
        hudOverlay.classList.remove('hidden');
        
        descriptionInput.value = data.description;
        caseIdDisplay.textContent = data.id;
        caseNameInput.value = data.name || '';
        ageSlider.value = data.traits.age;
        ageVal.textContent = data.traits.age;
        genderSelect.value = data.traits.gender;
        styleSelect.value = data.traits.style;
        
        aiReportText.textContent = data.report;
        confidenceBadge.textContent = `${data.confidence}% CONFIDENCE`;
        analysisReport.classList.remove('hidden');
        
        // Handle warning banner on restore
        const oldWarning = document.querySelector('.simulated-warning');
        if (oldWarning) oldWarning.remove();

        if (data.is_simulated) {
            imagePlaceholder.parentElement.classList.add('simulated');
            const warningDiv = document.createElement('div');
            warningDiv.className = 'simulated-warning';
            warningDiv.innerHTML = `⚠️ <strong>CRITICAL LOG: ARCHIVED CASE (SIMULATED FALLBACK)</strong><br>This sketch was reconstructed using the offline fallback biometric matching protocol.`;
            imagePlaceholder.parentElement.parentElement.appendChild(warningDiv);
        } else {
            imagePlaceholder.parentElement.classList.remove('simulated');
        }
        
        addLog(`ARCHIVE RESTORED: ${data.id}`);
    };

    const addLog = (message, highlight = false) => {
        if (!logBody) return;
        const line = document.createElement('div');
        line.className = highlight ? 'log-line highlight' : 'log-line';
        line.textContent = `> ${message.toUpperCase()}`;
        logBody.appendChild(line);
        logBody.scrollTop = logBody.scrollHeight;
        if (logBody.children.length > 10) logBody.children[0].remove();
    };

   
    ageSlider.addEventListener('input', (e) => {
        ageVal.textContent = e.target.value;
    });

   
    let allCases = [];
    let currentCaseData = null;

    // Live Rename Logic
    caseNameInput.addEventListener('input', (e) => {
        if (currentCaseData) {
            currentCaseData.name = e.target.value.trim();
            // Find and update the history item in the UI
            const items = historyList.querySelectorAll('.history-item');
            for (let item of items) {
                if (item.querySelector('.case-id').textContent === currentCaseData.id) {
                    item.querySelector('.case-name-tag').textContent = currentCaseData.name || 'UNNAMED_CASE';
                    break;
                }
            }
        }
    });

    const loadCases = async () => {
        const casesGrid = document.getElementById('cases-grid');
        const caseCount = document.getElementById('case-count');
        if (!casesGrid) return;

        try {
            const response = await fetch('/cases');
            const data = await response.json();
            allCases = data.cases;
            renderCases(allCases);
            if (caseCount) caseCount.textContent = `ENTRIES: ${allCases.length}`;
        } catch (error) {
            console.error("Failed to load cases:", error);
        }
    };

    const renderCases = (cases) => {
        const casesGrid = document.getElementById('cases-grid');
        casesGrid.innerHTML = '';

        cases.forEach(c => {
            const card = document.createElement('div');
            card.className = 'forensic-card glass';
            card.innerHTML = `
                <div class="card-status ${c.status.toLowerCase().replace(' ', '-')}">${c.status}</div>
                <div class="card-inner">
                    <div class="card-visual double-image">
                        <img src="${c.sketch_url || c.image_url}" class="card-sketch" alt="${c.name} Sketch">
                        <img src="${c.photo_url}" class="card-photo" alt="${c.name} Mugshot">
                        <div class="image-mode-badge">SKETCH ⇄ MUGSHOT</div>
                        <div class="visual-overlay"></div>
                    </div>
                    <div class="card-content">
                        <div class="content-header">
                            <span class="case-id-tag">${c.id}</span>
                            <span class="case-date">${c.date_created}</span>
                        </div>
                        <h3>${c.name.toUpperCase()}</h3>
                        <div class="stats-grid">
                            <div class="stat-item"><label>AGE</label><span>${c.age}</span></div>
                            <div class="stat-item"><label>GENDER</label><span>${c.gender}</span></div>
                            <div class="stat-item wide"><label>OFFENSE</label><span>${c.offense}</span></div>
                            <div class="stat-item wide"><label>LAST SEEN</label><span>${c.last_seen}</span></div>
                            <div class="stat-item wide"><label>ADDRESS</label><span>${c.address}</span></div>
                        </div>
                        <div class="card-actions">
                            <button class="btn-primary-sm use-demo" data-desc="${c.description}">LOAD FOR ANALYSIS</button>
                        </div>
                    </div>
                </div>
            `;
            casesGrid.appendChild(card);
        });
    };

   
    const caseSearch = document.getElementById('case-search');
    if (caseSearch) {
        caseSearch.addEventListener('input', (e) => {
            const term = e.target.value.toLowerCase();
            const filtered = allCases.filter(c => 
                c.name.toLowerCase().includes(term) || 
                c.id.toLowerCase().includes(term) || 
                c.offense.toLowerCase().includes(term)
            );
            renderCases(filtered);
        });
    }

  
    loadCases();

    const contactForm = document.getElementById('forensic-contact-form');
    if (contactForm) {
        contactForm.addEventListener('submit', (e) => {
            e.preventDefault();
            const btn = contactForm.querySelector('button');
            const originalText = btn.textContent;
            
            btn.textContent = 'TRANSMITTING SECURE DATA...';
            btn.disabled = true;
            
            setTimeout(() => {
                addLog("SECURE MESSAGE TRANSMITTED TO CCAB HEADQUARTERS");
                alert("INQUIRY SUBMITTED: Your encrypted message has been sent to the Digital Forensic Identification Unit.");
                btn.textContent = originalText;
                btn.disabled = false;
                contactForm.reset();
            }, 1500);
        });
    }

   
    const navLinks = document.querySelectorAll('.nav-link');
    const sections = document.querySelectorAll('.section-container');
    navLinks.forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            const target = link.getAttribute('data-section');
            navLinks.forEach(l => l.classList.remove('active'));
            link.classList.add('active');
            sections.forEach(s => {
                s.classList.add('hidden');
                s.classList.remove('active');
            });
            const targetSection = document.getElementById(`${target}-section`);
            if (targetSection) {
                targetSection.classList.remove('hidden');
                targetSection.classList.add('active');
            }

            if (target === 'cases') loadCases();
        });
    });

    
    document.addEventListener('click', (e) => {
        if (e.target.classList.contains('use-demo')) {
            const desc = e.target.getAttribute('data-desc');
            descriptionInput.value = desc;
            document.querySelector('[data-section="home"]').click();
            window.scrollTo({ top: 0, behavior: 'smooth' });
            addLog("DOSSIER LOADED INTO BUFFER");
        }
    });

   
    generateBtn.addEventListener('click', async () => {
        const description = descriptionInput.value.trim();
        if (!description) return alert('Please enter witness testimony.');

        const traits = {
            age: ageSlider.value,
            gender: genderSelect.value,
            style: styleSelect.value
        };

        // Determine case_id: use the input field value, or fall back to an auto-generated one
        const inputCaseId = caseIdInput ? caseIdInput.value.trim() : '';
        const currentCaseId = inputCaseId || generateCaseId().replace('CASE: #', '');
        caseIdDisplay.textContent = `CASE: #${currentCaseId}`;
        if (caseIdInput && !inputCaseId) caseIdInput.value = currentCaseId;

        generateBtn.disabled = true;
        generateBtn.querySelector('.btn-text').textContent = 'GENERATING...';
        stageMonitor.classList.remove('hidden');
        analysisReport.classList.add('hidden');
        imagePlaceholder.classList.remove('hidden');
        primaryImage.classList.add('hidden');
        if (sketchDisplay) sketchDisplay.classList.add('hidden');
        hudOverlay.classList.add('hidden');
        
       
        const sideSlots = document.querySelectorAll('.var-slot');
        sideSlots.forEach(slot => {
            const imgContainer = slot.querySelector('.slot-image');
            if (imgContainer) imgContainer.innerHTML = '<p>?</p>';
            slot.onclick = null;
        });

        addLog("INITIATING BIO-SCAN...", true);

        try {
            setStage(1);
            await new Promise(r => setTimeout(r, 1000));
            addLog("ACCESSING HUGGINGFACE_INFERENCE_V4");

            setStage(2);
            const response = await fetch('/generate', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ case_id: currentCaseId, description, traits })
            });

            const data = await response.json();
            if (!response.ok || data.error) throw new Error(data.error || `Server error ${response.status}`);
            if (!data.images || data.images.length === 0) throw new Error('No images generated');

            setStage(3);
            addLog("RECONSTRUCTING FACIAL LATTICE...");
            addLog(`BIOMETRIC LOCK ESTABLISHED: SEED_${data.master_seed || 'N/A'}`);
            await new Promise(r => setTimeout(r, 1000));

            // Cache-bust to prevent browser serving a stale PNG for the same case_id
            const ts = Date.now();

            // --- Primary image ---
            const primaryUrl = (data.primary_url || data.image_url || data.images?.[0]) + `?t=${ts}`;
            primaryImage.src = primaryUrl;
            primaryImage.classList.remove('hidden');
            imagePlaceholder.classList.add('hidden');

            // Keep spec-required sketch-display in sync
            if (sketchDisplay) {
                sketchDisplay.src = primaryUrl;
                sketchDisplay.classList.remove('hidden');
            }

            // --- Variation slots (VAR 01 / VAR 02) ---
            // Build the two variation URLs from the named response keys,
            // falling back to data.images[1/2] if named keys are absent (simulation path).
            const varUrls = [
                data.var1_url || data.images?.[1] || null,
                data.var2_url || data.images?.[2] || null,
            ];

            const sideSlots = document.querySelectorAll('.var-slot');
            varUrls.forEach((rawUrl, idx) => {
                const slot = sideSlots[idx];
                if (!slot) return;

                const slotImgContainer = slot.querySelector('.slot-image');
                if (!rawUrl) {
                    // No image for this slot — show the placeholder
                    slotImgContainer.innerHTML = '<p>?</p>';
                    slot.onclick = null;
                    return;
                }

                const varUrl = rawUrl + `?t=${ts}`;
                // Replace the "?" placeholder with a real image
                slotImgContainer.innerHTML = `<img src="${varUrl}" class="variation-img" alt="Variation ${idx + 1}" style="width:100%;height:100%;object-fit:cover;border-radius:6px;">`;

                // Swap with primary on click
                slot.style.cursor = 'pointer';
                slot.onclick = () => {
                    const mainImg = document.getElementById('primary-image');
                    const clickedImg = slotImgContainer.querySelector('img');
                    if (mainImg && clickedImg) {
                        const tempSrc = mainImg.src;
                        mainImg.src = clickedImg.src;
                        clickedImg.src = tempSrc;
                        if (sketchDisplay) sketchDisplay.src = mainImg.src;
                        addLog(`SWITCHING VIEW: VARIATION ${idx + 1} (IDENTITY PRESERVED)`);
                    }
                };
            });

            addLog(`VARIATIONS RENDERED: ${varUrls.filter(Boolean).length}/2 SLOTS POPULATED`, true);

            confidenceBadge.textContent = `${data.confidence}% CONFIDENCE`;
            aiReportText.textContent = data.report;
            analysisReport.classList.remove('hidden');
            
            // Remove any pre-existing simulated warning
            const oldWarning = document.querySelector('.simulated-warning');
            if (oldWarning) oldWarning.remove();

            if (data.is_simulated) {
                addLog("CRITICAL: API THRESHOLD EXCEEDED", true);
                addLog("ENGAGING OFFLINE MATCHING PROTOCOL...", true);
                imagePlaceholder.parentElement.classList.add('simulated');
                
                // Add simulated warning element
                const warningDiv = document.createElement('div');
                warningDiv.className = 'simulated-warning';
                warningDiv.innerHTML = `⚠️ <strong>CRITICAL LOG: API TERMINATED (LIMIT EXCEEDED / OFFLINE)</strong><br>Engaging local fallback database matching. Suspect correlation established via offline biometric signatures.`;
                imagePlaceholder.parentElement.parentElement.appendChild(warningDiv);
            } else {
                addLog("RECONSTRUCTION COMPLETE: IDENTITY VERIFIED", true);
                imagePlaceholder.parentElement.classList.remove('simulated');
            }
            hudOverlay.classList.remove('hidden');

            const newCase = {
                id: currentCaseId,
                name: caseNameInput.value.trim(),
                description: description,
                image: data.images[0],
                traits: {...traits},
                report: data.report,
                confidence: data.confidence,
                seed: data.master_seed,
                is_simulated: data.is_simulated
            };
            
            currentCaseData = newCase;
            addToHistory(newCase);

        } catch (error) {
            console.error(error);
            alert(`Forensic analysis failed: ${error.message || 'System offline or API limit reached.'}`);
            addLog('SYSTEM ERROR: INFERENCE FAILED', true);
        } finally {
            generateBtn.disabled = false;
            generateBtn.querySelector('.btn-text').textContent = 'INITIATE RECONSTRUCTION';
            setTimeout(() => {
                stageMonitor.classList.add('hidden');
                progressBar.style.width = '0%';
            }, 2000);
        }
    });

  
    compareBtn.addEventListener('click', async () => {
        const description = descriptionInput.value.trim();
        if (!description) return;

        compareBtn.disabled = true;
        compareBtn.textContent = 'SCANNING...';
        addLog("CROSS-REFERENCING CRIMINAL DATABASE...", true);

        try {
            const response = await fetch('/compare', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ description })
            });

            const data = await response.json();
            matchesList.innerHTML = '';
            matchesPanel.classList.remove('hidden');

            if (data.matches && data.matches.length > 0) {
                addLog(`FOUND ${data.matches.length} POTENTIAL MATCHES`, true);
                data.matches.forEach(match => {
                    const item = document.createElement('div');
                    item.className = 'match-card glass';
                    item.style.cssText = 'min-width: 200px; padding: 10px; border: 1px solid rgba(0, 242, 255, 0.2); border-radius: 8px; margin-bottom: 10px; position: relative;';
                    item.innerHTML = `
                        <div class="match-card-visual">
                            <img src="${match.sketch_url || match.image_url}" class="match-sketch" alt="${match.name} Sketch">
                            <img src="${match.photo_url}" class="match-photo" alt="${match.name} Mugshot">
                            <div class="match-mode-badge">SKETCH ⇄ MUGSHOT</div>
                        </div>
                        <div style="margin-top:8px;">
                            <h4 style="font-size:0.8rem; color:var(--primary-neon);">${match.name}</h4>
                            <div class="match-bar-container" style="height:4px; background:rgba(255,255,255,0.1); margin:5px 0;">
                                <div style="width:${match.similarity}%; height:100%; background:var(--primary-neon);"></div>
                            </div>
                            <span style="font-size:0.6rem; color:var(--text-dim);">${match.similarity}% MATCH</span>
                        </div>
                    `;
                    matchesList.appendChild(item);
                });
            } else {
                addLog("NO DATABASE MATCHES FOUND", true);
                matchesList.innerHTML = '<p style="padding:20px; color:var(--text-dim);">NO MATCHES FOUND IN CURRENT SECTOR.</p>';
            }
        } catch (error) {
            console.error(error);
            addLog("DATABASE ACCESS ERROR", true);
        } finally {
            compareBtn.disabled = false;
            compareBtn.textContent = 'COMPARE TO DATABASE';
        }
    });

    const downloadCaseBtn = document.getElementById('download-case-btn');
    if (downloadCaseBtn) {
        downloadCaseBtn.addEventListener('click', () => {
            const currentImg = document.getElementById('primary-image');
            if (!currentImg || currentImg.classList.contains('hidden') || !currentImg.src) {
                alert("NO CASE DATA TO DOWNLOAD. INITIATE RECONSTRUCTION FIRST.");
                return;
            }

            const link = document.createElement('a');
            link.href = currentImg.src;
            link.download = `FACETRACE_${caseIdDisplay.textContent.replace('CASE: #', '').replace(':', '')}.png`;
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
            addLog("CASE DOSSIER EXPORTED TO DISK");
        });
    }
   
    const newCaseBtn = document.getElementById('new-case-btn');
    if (newCaseBtn) {
        newCaseBtn.addEventListener('click', () => {
            
            currentCaseData = null;
            
            descriptionInput.value = '';
            ageSlider.value = 30;
            ageVal.textContent = 30;
            genderSelect.selectedIndex = 0;
            styleSelect.selectedIndex = 0;
            caseNameInput.value = '';
            caseIdDisplay.textContent = 'CASE: #PENDING';
            
            // Clear warning banner and class list
            const oldWarning = document.querySelector('.simulated-warning');
            if (oldWarning) oldWarning.remove();
            imagePlaceholder.parentElement.classList.remove('simulated');

            primaryImage.src = '';
            primaryImage.classList.add('hidden');
            imagePlaceholder.classList.remove('hidden');
            hudOverlay.classList.add('hidden');
            analysisReport.classList.add('hidden');
            if (matchesPanel) matchesPanel.classList.add('hidden');
            
            const sideSlots = document.querySelectorAll('.var-slot');
            sideSlots.forEach(slot => {
                const imgContainer = slot.querySelector('.slot-image');
                if (imgContainer) imgContainer.innerHTML = '<p>?</p>';
                slot.onclick = null; 
            });

            addLog("SYSTEM RESET: READY FOR NEW CASE", true);
            window.scrollTo({ top: 0, behavior: 'smooth' });
        });
    }
});
