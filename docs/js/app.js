async function loadData(){
  try{
    const r = await fetch('data/savings.json');
    return await r.json();
  }catch(e){ console.error(e); return null; }
}
function formatMoney(n){
  return new Intl.NumberFormat('en-US',{style:'currency',currency:'USD',maximumFractionDigits:0}).format(n);
}
function formatMoney2(n){
  return new Intl.NumberFormat('en-US',{style:'currency',currency:'USD',maximumFractionDigits:2}).format(n);
}
function calcInterest(principal, apy){
  // APY already compounding; yearly interest = principal * apy/100
  return principal * (apy/100);
}
document.addEventListener('DOMContentLoaded', async ()=>{
  const data = await loadData();
  if(!data) return;
  // populate KPI if exists
  const elFDIC = document.getElementById('kpi-fdic');
  if(elFDIC) elFDIC.textContent = '$250,000';
  const elAvg = document.getElementById('kpi-avg');
  if(elAvg) elAvg.textContent = '0.37%';
  const elTop = document.getElementById('kpi-top');
  if(elTop) elTop.textContent = '3.75%';
  const elCount = document.getElementById('kpi-count');
  if(elCount) elCount.textContent = data.banks.length + ' banks';
});
function filterTable(inputId, tableId){
  const q = document.getElementById(inputId).value.toLowerCase();
  const rows = document.querySelectorAll('#'+tableId+' tbody tr');
  rows.forEach(tr=>{
    tr.style.display = tr.textContent.toLowerCase().includes(q) ? '' : 'none';
  });
}
function sortTable(tableId, colIndex, numeric){
  const tbody = document.querySelector('#'+tableId+' tbody');
  const rows = Array.from(tbody.querySelectorAll('tr'));
  const dir = tbody.dataset.sortDir === 'asc' ? 'desc' : 'asc';
  tbody.dataset.sortDir = dir;
  rows.sort((a,b)=>{
    let va = a.children[colIndex].textContent.trim();
    let vb = b.children[colIndex].textContent.trim();
    if(numeric){
      va = parseFloat(va.replace(/[^0-9.\-]/g,''))||0;
      vb = parseFloat(vb.replace(/[^0-9.\-]/g,''))||0;
      return dir==='asc'? va-vb : vb-va;
    } else {
      return dir==='asc'? va.localeCompare(vb) : vb.localeCompare(va);
    }
  });
  rows.forEach(r=> tbody.appendChild(r));
}
