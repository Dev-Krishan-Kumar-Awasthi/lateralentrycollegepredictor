/**
 * What-if CGPA slider — live rank + top colleges preview
 */
(function (global) {
  'use strict';

  let debounceTimer = null;

  function debounce(fn, ms) {
    return function () {
      const args = arguments;
      clearTimeout(debounceTimer);
      debounceTimer = setTimeout(function () { fn.apply(null, args); }, ms);
    };
  }

  function collectFormParams(form) {
    const fd = new FormData(form);
    const branches = [];
    form.querySelectorAll('select[name=branch] option:checked, input[name=branch]:checked').forEach(function (el) {
      if (el.value) branches.push(el.value);
    });
    if (!branches.length) {
      const sel = form.querySelector('select[name=branch]');
      if (sel) {
        Array.from(sel.selectedOptions).forEach(function (o) {
          if (o.value) branches.push(o.value);
        });
      }
    }
    return {
      cgpa: fd.get('cgpa'),
      category: fd.get('category'),
      gender: fd.get('gender'),
      college_type: fd.get('college_type'),
      domicile: fd.get('domicile') || 'Y',
      city: fd.get('city') || 'All',
      branch: branches.join(','),
    };
  }

  function renderPreview(container, data) {
    if (!container) return;
    if (!data || data.error) {
      container.innerHTML = '<div class="whatif-error">' + (data && data.error ? data.error : 'Unable to load preview') + '</div>';
      container.style.display = 'block';
      return;
    }
    let html = '<div class="whatif-rank">';
    html += '<strong>Estimated Rank (' + data.year + '):</strong> ';
    html += '<span class="whatif-rank-val">' + data.min_rank + ' – ' + data.max_rank + '</span>';
    html += '</div>';
    if (data.top_colleges && data.top_colleges.length) {
      html += '<ul class="whatif-list">';
      data.top_colleges.forEach(function (c, i) {
        html += '<li><span class="whatif-num">' + (i + 1) + '</span> ';
        html += '<span class="whatif-college">' + escapeHtml(c.college_name) + '</span> ';
        html += '<span class="whatif-branch">' + escapeHtml(c.branch_name || c.branch) + '</span> ';
        html += '<span class="whatif-prob prob-' + probClass(c.probability) + '">' + c.probability + '%</span></li>';
      });
      html += '</ul>';
    } else {
      html += '<p class="whatif-empty">No matching colleges at this CGPA for selected filters.</p>';
    }
    container.innerHTML = html;
    container.style.display = 'block';
  }

  function escapeHtml(s) {
    const d = document.createElement('div');
    d.textContent = s;
    return d.innerHTML;
  }

  function probClass(p) {
    if (p >= 75) return 'high';
    if (p >= 40) return 'med';
    return 'low';
  }

  function fetchPreview(params, container) {
    const qs = new URLSearchParams(params);
    container.classList.add('whatif-loading');
    fetch('/api/v1/whatif?' + qs.toString())
      .then(function (r) { return r.json(); })
      .then(function (data) {
        container.classList.remove('whatif-loading');
        renderPreview(container, data);
      })
      .catch(function () {
        container.classList.remove('whatif-loading');
        renderPreview(container, { error: 'Network error' });
      });
  }

  function init(formId, sliderId, previewId) {
    const form = document.getElementById(formId);
    const slider = document.getElementById(sliderId);
    const preview = document.getElementById(previewId);
    const cgpaInput = form && form.querySelector('[name=cgpa]');
    const cgpaLabel = document.getElementById('whatif-cgpa-label');
    if (!form || !slider || !preview || !cgpaInput) return;

    function syncFromSlider() {
      const v = parseFloat(slider.value);
      cgpaInput.value = v.toFixed(2);
      if (cgpaLabel) cgpaLabel.textContent = v.toFixed(2);
      const params = collectFormParams(form);
      params.cgpa = v.toFixed(2);
      if (!params.category || !params.gender) return;
      fetchPreview(params, preview);
    }

    slider.addEventListener('input', debounce(syncFromSlider, 350));
    cgpaInput.addEventListener('change', function () {
      const v = parseFloat(cgpaInput.value);
      if (!isNaN(v) && v >= 0 && v <= 10) {
        slider.value = v;
        if (cgpaLabel) cgpaLabel.textContent = v.toFixed(2);
        debounce(syncFromSlider, 100)();
      }
    });

    ['category', 'gender', 'college_type', 'domicile', 'city'].forEach(function (name) {
      const el = form.querySelector('[name=' + name + ']');
      if (el) el.addEventListener('change', debounce(syncFromSlider, 400));
    });
  }

  global.WhatIfSlider = { init: init };
})(typeof window !== 'undefined' ? window : global);
