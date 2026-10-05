document.addEventListener('DOMContentLoaded',function(){
  document.querySelectorAll('.filter-tab,.cat-row').forEach(el=>el.addEventListener('keydown',e=>{if(e.key==='Enter'||e.key===' '){e.preventDefault();el.click()}}));
  document.querySelectorAll('.filter-tab').forEach(tab=>tab.addEventListener('click',()=>filterPosts(tab.dataset.filter)));
});
function filterPosts(cat){
  document.querySelectorAll('.filter-tab').forEach(t=>t.classList.toggle('active',t.dataset.filter===cat));
  const items=document.querySelectorAll('.blog-item'); let visible=0;
  items.forEach(item=>{const show=cat==='all'||item.dataset.cat===cat;item.classList.toggle('hidden',!show);if(show)visible++});
  document.getElementById('emptyState').style.display=visible?'none':'block';
}
function handleNewsletter(e){
  const email=document.getElementById('newsletterEmail').value.trim();
  if(!email||!email.includes('@')||!email.includes('.')){
    e.preventDefault();
    const input=document.getElementById('newsletterEmail');
    input.style.borderColor='#f87171'; input.focus();
    setTimeout(()=>input.style.borderColor='',2000);
    return;
  }
  const link=e.currentTarget;
  link.href='mailto:info@lumenaautomation.co.in?subject=Newsletter%20Subscription&body='+encodeURIComponent('Please subscribe this email address to LumenaAutomation updates: '+email);
}
