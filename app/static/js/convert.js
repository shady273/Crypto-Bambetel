const inputFields = document.querySelectorAll(".input-field");

inputFields.forEach(function (input) {
  input.addEventListener("input", function () {
    setTimeout(function () {
      multiply(input);
    }, 500);
  });
});

function multiply(input) {
  const inputType = input.id;
  const inputValue = input.value;

  if (inputType === "coinInput") {
    if (!isNaN(inputValue) && inputValue !== "") {
      const usdResultElem = document.getElementById("usdInput");
      const usdResult = inputValue * coinPrice;
      usdResultElem.value = usdResult.toFixed(2);
    } else {
      document.getElementById("usdInput").value = "";
    }
  } else if (inputType === "usdInput") {
    if (!isNaN(inputValue) && inputValue !== "") {
      const coinResultElem = document.getElementById("coinInput");
      const coinResult = inputValue / coinPrice;
      coinResultElem.value = coinResult.toFixed(8);
    } else {
      document.getElementById("coinInput").value = "";
    }
  }
}
