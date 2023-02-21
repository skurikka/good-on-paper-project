function terms(){
	alert('Nobody reads these...');
}

function copyToken() {
	var copyText = document.getElementById("token");
	copyText.select();
	copyText.setSelectionRange(0, 99999);
	document.execCommand("copy");
}

function language(){
	var lang = document.getElementById("lang-desktop");
	if (lang.classList.contains("hidden")) {
		lang.classList.add("block");
		lang.classList.remove("hidden");
	} else {
		lang.classList.add("hidden");
		lang.classList.remove("block");
	}
}

function language_mob(){
	var lang = document.getElementById("lang-mobile");
	if (lang.classList.contains("hidden")) {
		lang.classList.add("block");
		lang.classList.remove("hidden");
	} else {
		lang.classList.add("hidden");
		lang.classList.remove("block");
	}
}