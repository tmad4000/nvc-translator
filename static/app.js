var translate = document.querySelector("#btn-translate");
var input_translate = document.querySelector("#input-translate")
var output_translate = document.querySelector("#output-translate")
var output_observations = document.querySelector("#output-giraffe-observations")
var output_feelings = document.querySelector("#output-giraffe-feelings")
var output_needs = document.querySelector("#output-giraffe-needs")
var output_requests = document.querySelector("#output-giraffe-requests")
var loading = document.querySelector("#loading");

// actual server
var mobileUrl = "https://www.nvctranslator.com/translate"
var webUrl = "translate"

function getText(text) {
  return text?.join(', ') || '';
}

function urlfunc() {
  var base = config.src === "mobile" ? mobileUrl : webUrl;
  // encodeURIComponent: without it, an "&" or "#" in the input silently
  // truncates the text before it reaches the server.
  return base + "?text=" + encodeURIComponent(input_translate.value);
}

// Lightweight GA4 event helper (safe no-op if gtag is blocked/missing)
function track(name, params) {
  try { if (typeof gtag === 'function') gtag('event', name, params || {}); } catch (e) { }
}

function setBreakdown(observations, feelings, needs, requests) {
  output_observations.innerText = getText(observations);
  output_feelings.innerText = getText(feelings);
  output_needs.innerText = getText(needs);
  output_requests.innerText = getText(requests);
}

function resetUi() {
  loading.style.display = 'none';
  translate.style.display = 'block';
}

function callback() {
  // Show spinner
  loading.style.display = 'block';
  // Hide translate button
  translate.style.display = 'none';

  var inputLen = (input_translate.value || '').length;
  track('translate_click', { input_chars: inputLen });

  fetch(urlfunc(), {
    method: 'GET',
    mode: 'cors',
  })
    .then(response => response.json())
    .then(json => {
      if (!json[0]) {
        alert("please enter some text")
        resetUi();
        return;
      }

      var raw = json[0].translation;
      var parsed = null;
      try {
        parsed = JSON.parse(raw);
      } catch (e) {
        // Not JSON. The server returns a plain sentence for rate limits, an
        // over-length input, an empty input, or an upstream error — show it
        // as-is rather than failing into the generic error alert.
        parsed = null;
      }

      if (parsed && typeof parsed === 'object' && parsed.rephrased_txt) {
        output_translate.innerText = String(parsed.rephrased_txt).trim();
        setBreakdown(parsed.observations, parsed.feelings, parsed.needs, parsed.requests);
        track('translate', { input_chars: inputLen });
      } else {
        var message = String(raw || '').trim();
        output_translate.innerText = message;
        setBreakdown([], [], [], []);
        var blocked = /translating quite fast|translation limit|daily capacity|bit long for the translator|hit an error/i.test(message);
        track(blocked ? 'translate_blocked' : 'translate', { input_chars: inputLen });
      }

      resetUi();
    }).catch(function errorhandler(error) {
      console.log("err: ", error)
      track('translate_error', {});
      resetUi();
      alert("Something wrong with the server. Please try again later.")
    })
}

translate.addEventListener("click", callback)


// Setting icon according to theme
if (currentTheme === "dark") {
  document.querySelectorAll('.theme-icon').forEach((icon) => icon.innerHTML = `<i class="fas fa-sun" id="zon"></i>`)
} else {
  document.querySelectorAll('.theme-icon').forEach((icon) => icon.innerHTML = `<i class="fas fa-moon" id="maan"></i>`)
}
function changeTheme() {
  const theme = document.documentElement.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
  document.documentElement.setAttribute('data-theme', theme);
  // Save the user's preference to local storage
  localStorage.setItem('theme', theme);

  // updating theme icon
  if (theme === "light") {
    document.querySelectorAll('.theme-icon').forEach((icon) => icon.innerHTML = `<i class="fas fa-moon" id="maan"></i>`)
  } else {
    document.querySelectorAll('.theme-icon').forEach((icon) => icon.innerHTML = `<i class="fas fa-sun" id="zon"></i>`)
  }
}

// Navbar
window.addEventListener('scroll', () => {
  if (window.scrollY > 80) {
    document.querySelectorAll('.nav-wrapper').forEach((nav) => { nav.classList.add('active') })
  } else {
    document.querySelectorAll('.nav-wrapper').forEach((nav) => { nav.classList.remove('active') })
  }
})

function handleNavMenu() {
  document.querySelectorAll('.navigation').forEach((navbar) => { navbar.classList.toggle('active') })
  document.querySelectorAll('.menu-icon').forEach((icon) => { icon.classList.toggle('active') })
}

// Scroll to translate section
function scrollToTranslator() {
  document.getElementById('translate-section').scrollIntoView({ behavior: 'smooth' });
}

function handleTranslateButton() {
  scrollToTranslator();
  localStorage.setItem('scrolled', 'true');
}

// Check localStorage on page load
window.onload = function () {
  if (localStorage.getItem('scrolled') === 'true') {
    scrollToTranslator();
  }
}
