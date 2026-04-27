document.getElementById('imageInput').addEventListener('change', async (e) => {
  const file = e.target.files[0];
  if (!file) return;

  const uploadArea = document.getElementById('uploadArea');
  const processingArea = document.getElementById('processingArea');
  const progressBar = document.getElementById('progressBar');
  
  uploadArea.style.display = 'none';
  processingArea.style.display = 'block';

  try {
    // 1. Upload Image
    const formData = new FormData();
    formData.append('file', file);
    
    progressBar.style.width = '30%';
    const uploadRes = await API.upload('/api/images/upload', formData);
    if (!uploadRes.ok) throw new Error('Upload failed');
    
    const uploadData = await uploadRes.json();
    const imageId = uploadData.id;
    
    // Show preview immediately
    const reader = new FileReader();
    reader.onload = (e) => {
      document.getElementById('previewImage').src = e.target.result;
    };
    reader.readAsDataURL(file);

    // 2. Run Debris Detection
    progressBar.style.width = '60%';
    const detectRes = await API.post(`/api/detect/debris/${imageId}`, {});
    const detectData = await detectRes.json();

    // 3. Run Ecosystem Segmentation
    progressBar.style.width = '90%';
    const segmentRes = await API.post(`/api/ecosystem/segment/${imageId}`, {});
    const segmentData = await segmentRes.json();

    // 4. Display Results
    progressBar.style.width = '100%';
    setTimeout(() => {
      processingArea.style.display = 'none';
      displayPrediction(detectData, segmentData);
    }, 500);

  } catch (err) {
    console.error(err);
    alert('AI processing failed. Please try again.');
    uploadArea.style.display = 'block';
    processingArea.style.display = 'none';
  }
});

function displayPrediction(detectData, segmentData) {
  const resultsArea = document.getElementById('predictionResult');
  resultsArea.style.display = 'grid';

  document.getElementById('densityScore').textContent = `${detectData.debris_density_score}%`;
  document.getElementById('densitySummary').textContent = detectData.summary;

  const segList = document.getElementById('segmentationList');
  const segments = [
    { label: 'Water', val: segmentData.water, color: '#0070f3' },
    { label: 'Algae', val: segmentData.algae, color: '#10b981' },
    { label: 'Coral', val: segmentData.coral, color: '#ef4444' },
    { label: 'Debris', val: segmentData.debris, color: '#f97316' },
    { label: 'Turbid Water', val: segmentData.turbid_water, color: '#8892b0' }
  ];

  segList.innerHTML = segments.map(s => `
    <div class="segmentation-item">
      <div class="segment-label">
        <span>${s.label}</span>
        <span>${s.val}%</span>
      </div>
      <div class="segment-bar">
        <div class="segment-fill" style="width: ${s.val}%; background-color: ${s.color};"></div>
      </div>
    </div>
  `).join('');

  // Draw Mock Bounding Boxes
  const boxesContainer = document.getElementById('boundingBoxes');
  boxesContainer.innerHTML = detectData.detections.map(d => `
    <div style="
      position: absolute;
      left: ${d.bbox[0]}%;
      top: ${d.bbox[1]}%;
      width: ${d.bbox[2] - d.bbox[0]}%;
      height: ${d.bbox[3] - d.bbox[1]}%;
      border: 2px solid var(--accent-cyan);
      box-shadow: 0 0 10px rgba(100, 255, 218, 0.5);
    ">
      <span style="
        position: absolute;
        top: -20px;
        left: -2px;
        background: var(--accent-cyan);
        color: var(--bg-dark);
        padding: 0 5px;
        font-size: 0.7rem;
        font-weight: bold;
        white-space: nowrap;
      ">${d.class} (${Math.round(d.confidence * 100)}%)</span>
    </div>
  `).join('');
}
