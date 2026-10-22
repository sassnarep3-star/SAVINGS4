'use strict';
const inputs = document.querySelectorAll('[data-filter]');
function filterRows(){
  const query = (document.querySelector('[data-filter="search"]')?.value || '').trim().toLowerCase();
  const category = document.querySelector('[data-filter="category"]')?.value || '';
  const status = document.querySelector('[data-filter="status"]')?.value || '';
  let count = 0;
  document.querySelectorAll('tbody tr[data-search]').forEach(row=>{
    const visible = row.dataset.search.includes(query) && (!category || row.dataset.category === category) && (!status || row.dataset.status === status);
    row.hidden = !visible;
    if(visible) count++;
  });
  const label=document.querySelector('[data-count]');
  if(label) label.textContent=`${count} entries shown`;
  const empty=document.querySelector('.no-results');
  if(empty) empty.hidden=count!==0;
}
inputs.forEach(input=>input.addEventListener('input',filterRows));
if(inputs.length)filterRows();
// Never change the research/opening date silently to today's browser date.
if(new Date().toISOString().slice(0,10) > '2026-10-22') document.querySelector('#stale')?.style.setProperty('display','block');
