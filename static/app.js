var translate = document.querySelector("#btn-translate");
var input_translate = document.querySelector("#input-translate")
var output_translate = document.querySelector("#output-translate")
var output_observations = document.querySelector("#output-giraffe-observations")
var output_feelings = document.querySelector("#output-giraffe-feelings")
var output_needs = document.querySelector("#output-giraffe-needs")
var output_requests = document.querySelector("#output-giraffe-requests")
var loading = document.querySelector("#loading");

// mock server
// var url = "https://lessonfourapi.tanaypratap.repl.co/translate/yoda.json"


// actual server
var url = "translate"

function urlfunc(url) {
    return url + "?" + "text=" + input_translate.value
}
function jsonEncoder(str) {
  try {
      let ans = JSON.parse(str);
      return ans;
  } catch (e) {
      return JSON.parse(JSON.parse(JSON.stringify(str)));
  }
}

function callback() {
    // Show spinner
    loading.style.display = 'block';
    // Hide translate button
    translate.style.display = 'none';

    fetch(urlfunc(url), {
        method: 'GET',
        mode: 'cors',
      })
        .then(response => response.json())
        .then(json => {
          let output_text;
          console.log("original res: ", json)
          console.log("json0: ", (json[0].translation))
          //********************* removing new lines and spaces *******************************************/
          output_text = json[0].translation.split('\n').filter(s => Boolean(s.trim()));
          console.log("json1: ", output_text)
          //********************* converting to array of objects (key: [values]) **************************/
          output_text = output_text.map(e => ( { [`${e.split(':')[0]}`] : jsonEncoder(e.split(':')[1]) } ))
          console.log("json2: ", output_text)
          //********************* reducing array of objects to one object *********************************/
          output_text = output_text.reduce((prev, nxt) => ({...prev, ...nxt}), {})
          console.log("json3: ", output_text)
          /*
            output_text: {
              "original_txt": "",
              "rephrased_txt": "",
              "observations": [],
              "feelings": [],
              "needs": [],
              "requests": []
            }
          */
          //********assigning values */
          output_translate.innerText = output_text.rephrased_txt; // For some reason the response comes back with leading \n's
          output_observations.innerText = output_text.observations;
          output_feelings.innerText = output_text.feelings;
          output_needs.innerText = output_text.needs;
          output_requests.innerText = output_text.requests;
          // Hide spinner
          loading.style.display = 'none';
          // Show translate button
          translate.style.display = 'block';
        }).catch(function errorhandler(error) {
          console.log("err: ", error)
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
