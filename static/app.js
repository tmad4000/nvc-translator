var translate = document.querySelector("#btn-translate");
var input_translate = document.querySelector("#input-translate")
var output_translate = document.querySelector("#output-translate")
var loading = document.querySelector("#loading");

// mock server
// var url = "https://lessonfourapi.tanaypratap.repl.co/translate/yoda.json"


// actual server
var url = "translate"

function urlfunc(url) {
    return url + "?" + "text=" + input_translate.value
}

// Lightweight GA4 event helper (safe no-op if gtag is blocked/missing)
function track(name, params) {
    try { if (typeof gtag === 'function') gtag('event', name, params || {}); } catch (e) {}
}

function callback() {
    // Show spinner
    loading.style.display = 'block';
    // Hide translate button
    translate.style.display = 'none';

    var inputLen = (input_translate.value || '').length;
    track('translate_click', { input_chars: inputLen });

    fetch(urlfunc(url), {
        method: 'GET',
        mode: 'cors',
      })
        .then(response => response.json())
        .then(json => {
            console.log("json: ", json)
            var output_text = json[0].translation;

            // Distinguish a real translation from a server limit/error message
            var blocked = /translating quite fast|translation limit|daily capacity|bit long for the translator|hit an error/i.test(output_text);
            track(blocked ? 'translate_blocked' : 'translate', { input_chars: inputLen });

            output_translate.innerText = output_text.trim(); // For some reason the response comes back with leading \n's

            // Hide spinner
            loading.style.display = 'none';
            // Show translate button
            translate.style.display = 'block';

        }).catch(function errorhandler(error) {
            track('translate_error', {});
            // Hide spinner
            loading.style.display = 'none';
            // Show translate button
            translate.style.display = 'block';

            alert("Something wrong with the server. Please try again later.")
        })
}

translate.addEventListener("click", callback)

const currentTheme = localStorage.getItem("theme");
if (currentTheme == "dark") {
    document.getElementById('toggleknop').innerHTML = '<i class="fas fa-sun" id="zon" style="color:#d8c658;"></i>';
  document.body.classList.add("dark-theme");
}

function changeTheme() {
    document.body.classList.toggle("dark-theme");
  
  document.getElementById('toggleknop').innerHTML = '<i class="fas fa-moon" id="maan" style="color:#737eac;"></i>';

  let theme = "light";
  if (document.body.classList.contains("dark-theme")) {
    document.getElementById('toggleknop').innerHTML = '<i class="fas fa-sun" id="zon" style="color:#d8c658;"></i>';
    theme = "dark";
  }
  localStorage.setItem("theme", theme);
}
