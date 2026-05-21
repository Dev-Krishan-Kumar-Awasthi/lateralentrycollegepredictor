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

  global.DteExport = {
    buildCsv: buildCsv,
    buildPlainText: buildPlainText,
    exportCsv: exportCsv,
    exportTxt: exportTxt,
    copyToClipboard: copyToClipboard,
    shortlistToChoices: shortlistToChoices,
  };
})(typeof window !== 'undefined' ? window : global);
