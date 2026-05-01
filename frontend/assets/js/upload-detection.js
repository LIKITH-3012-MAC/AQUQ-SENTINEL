/**
 * AquaSentinel AI - Image Upload & AI Detection Controller
 * Uses the standardized API layer from api.js
 */

const imageInput = document.getElementById('imageInput');
if (imageInput) {
  imageInput.addEventListener('change', async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    const uploadArea = document.getElementById('uploadArea');
    const processingArea = document.getElementById('processingArea');
    const progressBar = document.getElementById('progressBar');
    
    if (uploadArea) uploadArea.style.display = 'none';
    if (processingArea) processingArea.style.display = 'block';

    try {
      // 1. Upload Image via FormData
      const formData = new FormData();
      formData.append('file', file);
      
      if (progressBar) progressBar.style.width = '30%';
      
      const token = localStorage.getItem('token');
      const headers = {};
      if (token) headers['Authorization'] = `Bearer ${token}`;
      
      const uploadResponse = await fetch(`${CONFIG.API_BASE_URL}/api/images/upload`, {
        method: 'POST',
        headers,
        body: formData
      });
      
      if (!uploadResponse.ok) throw new Error('Upload failed');
      const uploadData = await uploadResponse.json();
      
      // Show preview immediately
      const reader = new FileReader();
      reader.onload = (ev) => {
        const previewImg = document.getElementById('previewImage');
        if (previewImg) previewImg.src = ev.target.result;
      };
      reader.readAsDataURL(file);

      // 2. Show completion
      if (progressBar) progressBar.style.width = '100%';
      setTimeout(() => {
        if (processingArea) processingArea.style.display = 'none';
        displayUploadSuccess(uploadData);
      }, 500);

    } catch (err) {
      console.error(err);
      alert('AI processing failed. Please try again.');
      if (uploadArea) uploadArea.style.display = 'block';
      if (processingArea) processingArea.style.display = 'none';
    }
  });
}

function displayUploadSuccess(data) {
  const resultsArea = document.getElementById('predictionResult');
  if (!resultsArea) return;
  
  resultsArea.style.display = 'grid';
  resultsArea.innerHTML = `
    <div class="glass-card" style="text-align: center; padding: 2rem;">
      <i class="fas fa-check-circle text-gradient" style="font-size: 3rem; margin-bottom: 1rem;"></i>
      <h3>Image Uploaded Successfully</h3>
      <p style="color: var(--text-secondary); margin-top: 1rem;">File: ${data.filename || 'Unknown'}</p>
      <p style="color: var(--text-secondary);">ID: ${data.id || 'N/A'}</p>
      <p style="color: var(--accent-color); margin-top: 1rem; font-size: 0.85rem;">AI analysis pipeline has been queued.</p>
    </div>
  `;
}
