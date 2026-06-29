(function () {
  if (window.self === window.top) return;
  document.documentElement.classList.add('embudo-embedded');
  document.querySelectorAll('.embudo-inline-nav').forEach(function (el) {
    el.hidden = true;
  });
})();
