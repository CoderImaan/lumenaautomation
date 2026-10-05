document.addEventListener('DOMContentLoaded', function () {

  /* Topic tabs → hidden input */
  const tabs = document.querySelectorAll('.topic-tab');
  const hiddenTopic = document.getElementById('hiddenTopic');
  const subjectField = document.getElementById('msgSubject');

  tabs.forEach(tab => {
    const selectTopic = function () {
      tabs.forEach(t => t.classList.remove('active'));
      this.classList.add('active');
      tabs.forEach(t => t.setAttribute('aria-pressed', String(t === this)));
      hiddenTopic.value = this.dataset.topic;
      if (!subjectField.value) {
        subjectField.value = 'Inquiry about ' + this.dataset.topic;
      }
    };
    tab.addEventListener('click', selectTopic);
    tab.addEventListener('keydown', function (event) {
      if (event.key === 'Enter' || event.key === ' ') {
        event.preventDefault();
        selectTopic.call(this);
      }
    });
  });

  /* FAQ accordion */
  document.querySelectorAll('.faq-question').forEach(q => {
    q.addEventListener('click', function () {
      const item = this.closest('.faq-item');
      const isOpen = item.classList.contains('open');
      document.querySelectorAll('.faq-item').forEach(i => i.classList.remove('open'));
      if (!isOpen) item.classList.add('open');
      document.querySelectorAll('.faq-question').forEach(question => {
        question.setAttribute('aria-expanded', String(question.closest('.faq-item').classList.contains('open')));
      });
    });
  });

  /* Form submit with Formspree + success message */
  const form = document.getElementById('contactForm');
  const successMsg = document.getElementById('formSuccess');
  const errorMsg = document.getElementById('formError');

  form.addEventListener('submit', async function (e) {
    e.preventDefault();
    if (!form.reportValidity()) return;
    errorMsg.hidden = true;
    const submitBtn = form.querySelector('button[type="submit"]');
    submitBtn.disabled = true;
    submitBtn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Sending…';

    try {
      const res = await fetch(form.action, {
        method: 'POST',
        body: new FormData(form),
        headers: { 'Accept': 'application/json' }
      });
      if (res.ok) {
        form.reset();
        successMsg.classList.add('visible');
        successMsg.focus();
        submitBtn.innerHTML = '<i class="fa-solid fa-circle-check"></i> Message Sent';
        submitBtn.style.background = 'linear-gradient(135deg,#22c55e,#16a34a)';
      } else {
        throw new Error('Submission failed');
      }
    } catch {
      submitBtn.disabled = false;
      submitBtn.innerHTML = 'Send Message &nbsp;<i class="fa-solid fa-paper-plane"></i>';
      errorMsg.hidden = false;
      errorMsg.focus();
    }
  });
});
