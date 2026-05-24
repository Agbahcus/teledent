function closeToast(btn) {
  const toast = btn.closest('.toast');
  if (toast) toast.remove();
}

function initToasts() {
  document.querySelectorAll('[data-toast-autodismiss="true"]').forEach((toast) => {
    window.setTimeout(() => {
      toast.remove();
    }, 4000);
  });
}

function initSidebarToggle() {
  const btn = document.querySelector('[data-sidebar-toggle="true"]');
  const sidebar = document.querySelector('[data-sidebar="true"]');
  if (!btn || !sidebar) return;
  btn.addEventListener('click', () => {
    sidebar.classList.toggle('is-open');
  });
}

function initLightbox() {
  const lightbox = document.querySelector('[data-lightbox="true"]');
  if (!lightbox) return;

  const image = lightbox.querySelector('.lightbox__image');
  const close = lightbox.querySelector('[data-lightbox-close="true"]');

  document.querySelectorAll('[data-lightbox-src]').forEach((button) => {
    button.addEventListener('click', () => {
      image.src = button.dataset.lightboxSrc;
      image.alt = button.dataset.lightboxAlt || 'Consultation photo';
      lightbox.classList.add('is-open');
      lightbox.setAttribute('aria-hidden', 'false');
    });
  });

  function closeLightbox() {
    lightbox.classList.remove('is-open');
    lightbox.setAttribute('aria-hidden', 'true');
    image.src = '';
  }

  close.addEventListener('click', closeLightbox);
  lightbox.addEventListener('click', (event) => {
    if (event.target === lightbox) closeLightbox();
  });
  document.addEventListener('keydown', (event) => {
    if (event.key === 'Escape' && lightbox.classList.contains('is-open')) closeLightbox();
  });
}

document.addEventListener('DOMContentLoaded', () => {
  initToasts();
  initSidebarToggle();
  initLightbox();
  initPublicConsultationForm();
});

function initPublicConsultationForm(){
  const form = document.getElementById('public-consultation-form');
  if(!form) return;
  const imagesInput = form.querySelector('#images');
  const preview = document.getElementById('image-preview');
  const submitBtn = document.getElementById('submit-btn');
  const skeleton = document.getElementById('skeleton');

  imagesInput.addEventListener('change', (e)=>{
    preview.innerHTML='';
    const files = Array.from(e.target.files).slice(0,3);
    files.forEach(file=>{
      const reader = new FileReader();
      const wrapper = document.createElement('div');
      wrapper.style.width='72px';wrapper.style.height='72px';wrapper.style.overflow='hidden';wrapper.style.borderRadius='8px';wrapper.style.border='1px solid rgba(0,0,0,0.06)';
      reader.onload = (ev)=>{
        const img = document.createElement('img');
        img.src = ev.target.result; img.style.width='100%'; img.style.height='100%'; img.style.objectFit='cover';
        wrapper.appendChild(img);
      };
      reader.readAsDataURL(file);
      preview.appendChild(wrapper);
    });
  });

  form.addEventListener('submit', (e)=>{
    // show skeleton while submitting to simulate app-like feedback
    skeleton.style.display='block';
    submitBtn.disabled = true;
  });
}

function initFormStepper(){
  const form = document.getElementById('public-consultation-form');
  if(!form) return;
  const steps = Array.from(form.querySelectorAll('.step'));
  let current = 0;
  const stepper = form.querySelector('[data-stepper="true"]');
  const stepperCurrent = stepper ? stepper.querySelector('[data-stepper-current]') : null;
  const stepperTotal = stepper ? stepper.querySelector('[data-stepper-total]') : null;
  const stepperPct = stepper ? stepper.querySelector('[data-stepper-pct]') : null;
  const stepperBar = stepper ? stepper.querySelector('[data-stepper-bar]') : null;
  const stepperDots = stepper ? Array.from(stepper.querySelectorAll('[data-stepper-dot]')) : [];

  function setFieldError(input, message){
    const field = input.closest('.field');
    if(!field) return;

    field.classList.add('field-error');
    input.setAttribute('aria-invalid', 'true');

    let err = field.querySelector('.form-error[data-client-error="true"]');
    if(!err){
      err = document.createElement('div');
      err.className = 'form-error';
      err.dataset.clientError = 'true';
      field.appendChild(err);
    }
    err.textContent = `! ${message}`;
  }

  function clearFieldError(input){
    const field = input.closest('.field');
    if(!field) return;

    input.removeAttribute('aria-invalid');
    const clientErr = field.querySelector('.form-error[data-client-error="true"]');
    if(clientErr) clientErr.remove();

    // Only clear the red state if there are no server-side errors left
    if(field.querySelectorAll('.form-error:not([data-client-error="true"])').length === 0){
      field.classList.remove('field-error');
    }
  }

  function validateStep(i){
    const step = steps[i];
    if(!step) return true;

    let firstInvalid = null;
    const inputs = Array.from(step.querySelectorAll('input, select, textarea'));

    inputs.forEach((el) => {
      if(el.hasAttribute('required')){
        const value = (el.value || '').trim();
        if(!value){
          setFieldError(el, 'This field is required.');
          firstInvalid = firstInvalid || el;
          return;
        }
      }

      if(el.tagName === 'SELECT'){
        if(el.hasAttribute('required') && (el.value === '' || el.value == null)){
          setFieldError(el, 'Please select an option.');
          firstInvalid = firstInvalid || el;
          return;
        }
      }

      if(el.type === 'email' && (el.value || '').trim()){
        if(!el.checkValidity()){
          setFieldError(el, 'Enter a valid email address.');
          firstInvalid = firstInvalid || el;
          return;
        }
      }

      if(el.type === 'number' && (el.value || '').trim()){
        const num = Number(el.value);
        const min = el.min !== '' ? Number(el.min) : null;
        const max = el.max !== '' ? Number(el.max) : null;
        if(Number.isNaN(num) || (min != null && num < min) || (max != null && num > max)){
          setFieldError(el, `Enter a number between ${el.min || '0'} and ${el.max || '10'}.`);
          firstInvalid = firstInvalid || el;
          return;
        }
      }

      if(el.tagName === 'TEXTAREA' && el.name && el.name.includes('patient_complaint')){
        const val = (el.value || '').trim();
        if(val && val.length < 10){
          setFieldError(el, 'Please add a bit more detail (at least 10 characters).');
          firstInvalid = firstInvalid || el;
          return;
        }
      }
    });

    if(firstInvalid){
      firstInvalid.focus({ preventScroll: true });
      firstInvalid.scrollIntoView({ behavior: 'smooth', block: 'center' });
      return false;
    }
    return true;
  }

  function updateProgress(i){
    if(!stepper) return;
    const total = steps.length || 1;
    const stepNum = i + 1;
    const pct = Math.round((stepNum / total) * 100);

    if(stepperTotal) stepperTotal.textContent = String(total);
    if(stepperCurrent) stepperCurrent.textContent = String(stepNum);
    if(stepperPct) stepperPct.textContent = `${pct}%`;
    if(stepperBar) stepperBar.style.width = `${pct}%`;

    stepper.setAttribute('aria-valuenow', String(stepNum));
    const progressEl = stepper.querySelector('[role="progressbar"]');
    if(progressEl) progressEl.setAttribute('aria-valuenow', String(stepNum));

    stepperDots.forEach((dot) => {
      const idx = Number(dot.dataset.stepperDot);
      dot.classList.toggle('is-active', idx === i);
      dot.classList.toggle('is-done', idx < i);
    });
  }

  function show(i){
    steps.forEach((s, idx)=> s.style.display = idx===i ? '' : 'none');
    current = i;
    updateProgress(i);

    const firstFocusable = steps[i].querySelector('input, select, textarea, button');
    if(firstFocusable) firstFocusable.focus({ preventScroll: true });
  }
  form.addEventListener('click', (e)=>{
    if(e.target.matches('[data-step-next]')){
      e.preventDefault();
      if(!validateStep(current)) return;
      if(current < steps.length-1) show(current+1);
    }
    if(e.target.matches('[data-step-prev]')){
      e.preventDefault();
      if(current > 0) show(current-1);
    }
  });

  form.addEventListener('input', (e) => {
    const el = e.target;
    if(!(el instanceof HTMLElement)) return;
    if(el.matches('input, select, textarea')) clearFieldError(el);
  });

  // If the server returned errors, jump to the first step with an error
  const firstErrorStepIndex = steps.findIndex((s) => s.querySelector('.field-error'));
  show(firstErrorStepIndex >= 0 ? firstErrorStepIndex : 0);
}

document.addEventListener('DOMContentLoaded', () => {
  initFormStepper();
});
