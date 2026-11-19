/**
 * AntiGravity AI Resume Screener - Core Client Script
 */

document.addEventListener('DOMContentLoaded', () => {
  // Auto-dismiss alert banners after 5 seconds
  const alerts = document.querySelectorAll('.alert-dismissible');
  alerts.forEach((alert) => {
    setTimeout(() => {
      const bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
      if (bsAlert) bsAlert.close();
    }, 5000);
  });

  // Setup Drag & Drop File Upload Areas
  const dropzones = document.querySelectorAll('.dropzone-box');
  dropzones.forEach((zone) => {
    const input = zone.querySelector('input[type="file"]');
    const preview = zone.querySelector('.file-preview-list');

    if (!input) return;

    ['dragenter', 'dragover'].forEach((eventName) => {
      zone.addEventListener(eventName, (e) => {
        e.preventDefault();
        zone.classList.add('dragover');
      });
    });

    ['dragleave', 'drop'].forEach((eventName) => {
      zone.addEventListener(eventName, (e) => {
        e.preventDefault();
        zone.classList.remove('dragover');
      });
    });

    zone.addEventListener('drop', (e) => {
      if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
        input.files = e.dataTransfer.files;
        updateFilePreview(input.files, preview);
      }
    });

    input.addEventListener('change', () => {
      updateFilePreview(input.files, preview);
    });
  });

  function updateFilePreview(files, container) {
    if (!container) return;
    container.innerHTML = '';
    if (files.length === 0) return;

    const listGroup = document.createElement('ul');
    listGroup.className = 'list-group list-group-flush text-start mt-3';

    Array.from(files).forEach((file) => {
      const li = document.createElement('li');
      li.className = 'list-group-item d-flex justify-content-between align-items-center bg-transparent py-2';
      li.innerHTML = `
        <div class="d-flex align-items-center gap-2 text-truncate">
          <i class="fa-solid fa-file-pdf text-danger"></i>
          <span class="small fw-medium text-truncate">${file.name}</span>
        </div>
        <span class="badge bg-secondary-subtle text-secondary small">${(file.size / 1024).toFixed(1)} KB</span>
      `;
      listGroup.appendChild(li);
    });

    container.appendChild(listGroup);
  }

  // Dynamic Skill Tag Input Component for Job Creation
  const tagInputs = document.querySelectorAll('.skill-tag-input-container');
  tagInputs.forEach((container) => {
    const input = container.querySelector('.tag-input');
    const hiddenField = container.querySelector('input[type="hidden"]');
    const badgeContainer = container.querySelector('.tags-wrapper');

    let tags = [];
    if (hiddenField && hiddenField.value) {
      try {
        tags = JSON.parse(hiddenField.value);
      } catch {
        tags = hiddenField.value.split(',').map((t) => t.trim()).filter(Boolean);
      }
    }

    function renderTags() {
      if (!badgeContainer) return;
      badgeContainer.innerHTML = '';
      tags.forEach((tag, idx) => {
        const badge = document.createElement('span');
        badge.className = 'badge bg-primary-subtle text-primary border border-primary-subtle d-inline-flex align-items-center gap-1 me-1 mb-1';
        badge.innerHTML = `
          ${tag}
          <button type="button" class="btn-close btn-close-white" style="font-size: 0.55rem;" aria-label="Remove" data-idx="${idx}"></button>
        `;
        badge.querySelector('button').addEventListener('click', () => {
          tags.splice(idx, 1);
          sync();
        });
        badgeContainer.appendChild(badge);
      });
    }

    function sync() {
      if (hiddenField) {
        hiddenField.value = JSON.stringify(tags);
      }
      renderTags();
    }

    if (input) {
      input.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' || e.key === ',') {
          e.preventDefault();
          const val = input.value.trim().replace(/^,|,$/g, '');
          if (val && !tags.includes(val)) {
            tags.push(val);
            input.value = '';
            sync();
          }
        }
      });
    }

    renderTags();
  });
});
