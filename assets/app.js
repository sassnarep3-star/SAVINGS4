'use strict';

// 1. Live multi-criteria table filter (National Banks Directory & Returns tier view)
const filterInputs = document.querySelectorAll('[data-filter]');
function filterRows() {
  const query = (document.querySelector('[data-filter="search"]')?.value || '').trim().toLowerCase();
  const category = document.querySelector('[data-filter="category"]')?.value || '';
  const status = document.querySelector('[data-filter="status"]')?.value || '';
  const tier = document.querySelector('[data-filter="tier"]')?.value || '';
  let count = 0;
  document.querySelectorAll('tbody tr[data-search], tbody tr[data-tier]').forEach(row => {
    const matchSearch = !row.dataset.search || row.dataset.search.includes(query);
    const matchCat = !category || row.dataset.category === category;
    const matchStatus = !status || row.dataset.status === status;
    const matchTier = !tier || !row.dataset.tier || row.dataset.tier === tier;
    const visible = matchSearch && matchCat && matchStatus && matchTier;
    row.hidden = !visible;
    if (visible) count++;
  });
  const label = document.querySelector('[data-count]');
  if (label) label.textContent = `${count} rows shown`;
  const empty = document.querySelector('.no-results');
  if (empty) empty.hidden = count !== 0;
}
filterInputs.forEach(el => el.addEventListener('input', filterRows));
if (filterInputs.length) filterRows();

// 2. Interactive Compound Return & FDIC Headroom Calculator (Overview & Returns pages)
const calcRoot = document.querySelector('[data-calc]');
if (calcRoot) {
  const principalEl = calcRoot.querySelector('[data-calc-principal]');
  const horizonEl = calcRoot.querySelector('[data-calc-days]');
  const modeEl = calcRoot.querySelector('[data-calc-mode]');
  const presetBtns = calcRoot.querySelectorAll('[data-preset]');

  const fmtMoney = n => '$' + n.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 });

  function updateCalc() {
    const P = Math.max(0, Number(principalEl?.value || 250000));
    const days = Number(horizonEl?.value || 365);
    const usePromo = (modeEl?.value || 'promo') === 'promo';

    presetBtns.forEach(btn => {
      btn.setAttribute('aria-pressed', Number(btn.dataset.preset) === P ? 'true' : 'false');
    });

    document.querySelectorAll('[data-calc-row]').forEach(tr => {
      const baseApy = Number(tr.dataset.baseApy);
      const promoApy = tr.dataset.promoApy ? Number(tr.dataset.promoApy) : null;
      const promoDays = Number(tr.dataset.promoDays || 0);
      const minOpen = Number(tr.dataset.minOpen || 0);
      const minTier = Number(tr.dataset.minTier || 0);
      const belowApy = tr.dataset.belowApy !== '' ? Number(tr.dataset.belowApy) : baseApy;
      const isBarclays = tr.dataset.accountId === 'barclays';

      const earnCell = tr.querySelector('[data-out-interest]');
      const endCell = tr.querySelector('[data-out-ending]');
      const fdicCell = tr.querySelector('[data-out-fdic]');
      if (!earnCell || !endCell) return;

      if (P < minOpen) {
        earnCell.innerHTML = `<span class="blank-dash">—</span><small>Needs $${minOpen.toLocaleString()} min open</small>`;
        endCell.innerHTML = `<span class="blank-dash">—</span>`;
        if (fdicCell) fdicCell.innerHTML = `<span class="pill neutral">Below min open</span>`;
        return;
      }

      let effBase = P < minTier ? belowApy : baseApy;
      if (isBarclays && P >= 250000) effBase = 3.65;

      let gf;
      if (usePromo && promoApy && promoDays > 0 && P >= minTier) {
        const pd = Math.min(days, promoDays);
        gf = Math.pow(1 + promoApy / 100, pd / 365) * Math.pow(1 + effBase / 100, (days - pd) / 365);
      } else {
        gf = Math.pow(1 + effBase / 100, days / 365);
      }

      const earned = P * (gf - 1);
      const ending = P + earned;
      earnCell.innerHTML = `<strong class="num">${fmtMoney(earned)}</strong>`;
      endCell.innerHTML = `<span class="num">${fmtMoney(ending)}</span>`;
      if (fdicCell) {
        if (ending <= 250000) {
          fdicCell.innerHTML = `<span class="pill">Fully insured (1 owner)</span><small>${fmtMoney(250000 - ending)} headroom</small>`;
        } else if (ending <= 500000) {
          fdicCell.innerHTML = `<span class="pill warn">Joint ($500k) or 2 banks</span><small>${fmtMoney(ending - 250000)} over 1-owner cap</small>`;
        } else {
          const banksNeeded = Math.ceil(ending / 250000);
          fdicCell.innerHTML = `<span class="pill warn">Split across ${banksNeeded}+ banks</span><small>Exceeds single &amp; joint caps</small>`;
        }
      }
    });
  }

  presetBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      principalEl.value = btn.dataset.preset;
      updateCalc();
    });
  });
  [principalEl, horizonEl, modeEl].forEach(el => el?.addEventListener('input', updateCalc));
  updateCalc();
}

// 3. Stale-snapshot banner guard (never mutates fixed 2026-10-22 opening date)
if (new Date().toISOString().slice(0, 10) > '2026-10-22') {
  document.querySelector('#stale')?.style.setProperty('display', 'block');
}
