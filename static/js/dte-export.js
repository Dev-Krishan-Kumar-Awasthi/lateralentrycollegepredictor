/**
 * DTE MP Choice List Export Utilities
 * Formats: CSV, plain-text (copy-paste), download
 */
(function (global) {
  'use strict';

  function escapeCsv(val) {
    const s = String(val == null ? '' : val);
    if (s.includes(',') || s.includes('"') || s.includes('\n')) {
      return '"' + s.replace(/"/g, '""') + '"';
    }
    return s;
  }

  function normalizeChoice(c) {
    return {
      college_name: c.college_name || c.college || '',
      branch: c.branch || '',
      branch_name: c.branch_name || c.branch || '',
    };
  }

  function toRows(choices) {
    return (choices || []).map(normalizeChoice);
  }

  function buildCsv(choices) {
    const rows = toRows(choices);
    const header = 'Priority,College Name,Branch Code,Branch Name';
    const lines = rows.map(function (c, i) {
      return [i + 1, c.college_name, c.branch, c.branch_name].map(escapeCsv).join(',');
    });
    return [header].concat(lines).join('\r\n');
  }

  function buildPlainText(choices) {
    const rows = toRows(choices);
    const lines = [
      'MP DTE LATERAL ENTRY — PRIORITY CHOICE LIST',
      'Generated: ' + new Date().toLocaleString('en-IN'),
      'Total Choices: ' + rows.length,
      '',
      '--- Copy below for reference when filling on dte.mponline.gov.in ---',
      '',
    ];
    rows.forEach(function (c, i) {
      lines.push(
        (i + 1) + '. ' + c.college_name + ' | Branch: ' + c.branch +
        (c.branch_name !== c.branch ? ' (' + c.branch_name + ')' : '')
      );
    });
    lines.push('');
    lines.push('Note: Verify exact college & branch names on official DTE portal before locking.');
    return lines.join('\n');
  }

  function downloadBlob(content, filename, mime) {
    const blob = new Blob([content], { type: mime || 'text/plain;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    a.click();
    URL.revokeObjectURL(url);
  }

  function exportCsv(choices, filename) {
    if (!choices || !choices.length) {
      if (global.showToast) global.showToast('Choice list is empty. Add colleges first.', 'error');
      else alert('Choice list is empty. Add colleges first.');
      return false;
    }
    const name = filename || 'MP-DTE-Choice-List-' + new Date().toISOString().slice(0, 10) + '.csv';
    downloadBlob(buildCsv(choices), name, 'text/csv;charset=utf-8');
    return true;
  }

  function exportTxt(choices, filename) {
    if (!choices || !choices.length) {
      if (global.showToast) global.showToast('Choice list is empty. Add colleges first.', 'error');
      else alert('Choice list is empty. Add colleges first.');
      return false;
    }
    const name = filename || 'MP-DTE-Choice-List-' + new Date().toISOString().slice(0, 10) + '.txt';
    downloadBlob(buildPlainText(choices), name, 'text/plain;charset=utf-8');
    return true;
  }

  function copyToClipboard(choices) {
    if (!choices || !choices.length) {
      if (global.showToast) global.showToast('Choice list is empty. Add colleges first.', 'error');
      else alert('Choice list is empty. Add colleges first.');
      return Promise.resolve(false);
    }
    const text = buildPlainText(choices);
    if (navigator.clipboard && navigator.clipboard.writeText) {
      return navigator.clipboard.writeText(text).then(function () { return true; });
    }
    const ta = document.createElement('textarea');
    ta.value = text;
    document.body.appendChild(ta);
    ta.select();
    document.execCommand('copy');
    document.body.removeChild(ta);
    return Promise.resolve(true);
  }

  function shortlistToChoices(shortlistIds) {
    return (shortlistIds || []).map(function (id) {
      const parts = String(id).split('|');
      return {
        college_name: parts[0] || '',
        branch: parts[1] || '',
        branch_name: parts[1] || '',
      };
    }).filter(function (c) { return c.college_name; });
  }

  let jspdfLoadPromise = null;

  function loadScript(src) {
    return new Promise(function (resolve, reject) {
      const s = document.createElement('script');
      s.src = src;
      s.onload = resolve;
      s.onerror = reject;
      document.head.appendChild(s);
    });
  }

  function ensureJsPdf() {
    if (global.jspdf) {
      return Promise.resolve();
    }
    if (jspdfLoadPromise) {
      return jspdfLoadPromise;
    }
    jspdfLoadPromise = loadScript('https://cdnjs.cloudflare.com/ajax/libs/jspdf/2.5.1/jspdf.umd.min.js')
      .then(function () {
        return loadScript('https://cdnjs.cloudflare.com/ajax/libs/jspdf-autotable/3.8.2/jspdf.plugin.autotable.min.js');
      })
      .catch(function (err) {
        jspdfLoadPromise = null;
        throw err;
      });
    return jspdfLoadPromise;
  }

  function exportPdf(choices, profileInfo, filename) {
    if (!choices || !choices.length) {
      if (global.showToast) global.showToast('Choice list is empty. Add colleges first.', 'error');
      else alert('Choice list is empty. Add colleges first.');
      return Promise.resolve(false);
    }
    profileInfo = profileInfo || {};

    if (global.showToast) global.showToast('Generating PDF Choice List...', 'info');

    return ensureJsPdf().then(function () {
      const { jsPDF } = global.jspdf;
      const doc = new jsPDF({
        orientation: 'p',
        unit: 'mm',
        format: 'a4'
      });

      // Title & Header Styling
      doc.setFillColor(30, 58, 138); // Navy blue header strip (#1E3A8A)
      doc.rect(0, 0, 210, 36, 'F');

      doc.setTextColor(255, 255, 255);
      doc.setFont('Helvetica', 'bold');
      doc.setFontSize(18);
      doc.text('MP DTE B.TECH LATERAL ENTRY PREDICTOR', 14, 15);
      doc.setFont('Helvetica', 'normal');
      doc.setFontSize(10);
      doc.text('Preference Choice List Report • For reference only', 14, 21);
      doc.text('Generated: ' + new Date().toLocaleString('en-IN'), 14, 27);

      // Student Meta Section
      doc.setFillColor(239, 246, 255); // Soft blue background (#EFF6FF)
      doc.rect(14, 42, 182, 32, 'F');
      doc.setDrawColor(219, 234, 254);
      doc.rect(14, 42, 182, 32);

      doc.setTextColor(30, 58, 138);
      doc.setFont('Helvetica', 'bold');
      doc.setFontSize(11);
      doc.text('STUDENT PROFILE DETAILS', 20, 48);

      doc.setTextColor(71, 85, 105);
      doc.setFont('Helvetica', 'normal');
      doc.setFontSize(9);
      doc.text('Name: ' + (profileInfo.name || '—'), 20, 56);
      doc.text('CGPA: ' + (profileInfo.cgpa || '—'), 20, 62);
      doc.text('Category: ' + (profileInfo.category || 'UR'), 20, 68);
      doc.text('Diploma Branch: ' + (profileInfo.branch || '—'), 100, 56);
      doc.text('Gender: ' + (profileInfo.gender === 'F' ? 'Female' : 'Male'), 100, 62);
      doc.text('Domicile: ' + (profileInfo.domicile === 'N' ? 'Non-MP' : 'MP Resident'), 100, 68);

      // Table Data Preparing
      const tableHeaders = [['#', 'College Name', 'Branch Code', 'Chance', 'Closing Cutoff']];
      const tableRows = (choices || []).map(function (c, i) {
        const probVal = (c.probability !== undefined && c.probability !== null) ? c.probability : (c.prob_type || '—');
        const displayProb = probVal + (typeof c.probability === 'number' ? '%' : '');
        return [
          i + 1,
          c.college_name || c.college || '',
          c.branch || '',
          displayProb,
          c.closing_rank || '—'
        ];
      });

      // AutoTable Plugin usage
      doc.autoTable({
        startY: 82,
        head: tableHeaders,
        body: tableRows,
        theme: 'striped',
        headStyles: {
          fillColor: [30, 58, 138],
          textColor: [255, 255, 255],
          fontSize: 9,
          fontStyle: 'bold'
        },
        bodyStyles: {
          fontSize: 8.5,
          textColor: [30, 41, 59]
        },
        columnStyles: {
          0: { cellWidth: 10, halign: 'center' },
          1: { cellWidth: 112 },
          2: { cellWidth: 24, halign: 'center' },
          3: { cellWidth: 18, halign: 'center' },
          4: { cellWidth: 18, halign: 'center' }
        },
        didParseCell: function (data) {
          if (data.section === 'body' && data.column.index === 3) {
            const cellVal = String(data.cell.raw);
            if (cellVal.includes('Safe') || parseInt(cellVal) >= 75) {
              data.cell.styles.textColor = [5, 150, 105]; // Green
              data.cell.styles.fontStyle = 'bold';
            } else if (cellVal.includes('Moderate') || cellVal.includes('Target') || parseInt(cellVal) >= 40) {
              data.cell.styles.textColor = [217, 119, 6]; // Amber
              data.cell.styles.fontStyle = 'bold';
            } else if (cellVal.includes('Dream') || cellVal.includes('Borderline') || (parseInt(cellVal) > 0 && parseInt(cellVal) < 40)) {
              data.cell.styles.textColor = [124, 58, 237]; // Purple
              data.cell.styles.fontStyle = 'bold';
            }
          }
        },
        margin: { left: 14, right: 14 }
      });

      // Footer disclaimer & help info
      const finalY = doc.lastAutoTable.finalY + 12;
      doc.setFillColor(248, 250, 252);
      doc.rect(14, finalY, 182, 22, 'F');
      doc.setFontSize(8);
      doc.setTextColor(148, 163, 184);
      doc.text('Important Notice: Cutoff ranks are estimated based on previous years\' DTE counseling trends.', 18, finalY + 6);
      doc.text('Please verify exact codes on the official portal (dte.mponline.gov.in) before submitting.', 18, finalY + 11);
      doc.text('Powering Future Engineers • MP B.Tech Lateral Entry Predictor', 18, finalY + 16);

      const name = filename || 'MP-DTE-Choice-List-' + new Date().toISOString().slice(0, 10) + '.pdf';
      doc.save(name);
      
      if (global.showToast) global.showToast('PDF Choice List generated successfully!', 'success');
      return true;
    }).catch(function (err) {
      console.error('PDF generation error:', err);
      if (global.showToast) global.showToast('Failed to generate PDF. Please try again.', 'error');
      else alert('Failed to generate PDF. Please try again.');
      return false;
    });
  }

  global.DteExport = {
    buildCsv: buildCsv,
    buildPlainText: buildPlainText,
    exportCsv: exportCsv,
    exportTxt: exportTxt,
    copyToClipboard: copyToClipboard,
    shortlistToChoices: shortlistToChoices,
    exportPdf: exportPdf,
  };
})(typeof window !== 'undefined' ? window : global);
