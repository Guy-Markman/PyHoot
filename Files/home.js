function changeDiv() {
	document.getElementById('p1').style.display =
		"none";
	document.getElementById('p2').style.display =
		"inline";
	document.getElementById('name').focus();
}

function check_length_name() {
	if (document.getElementById("name").value.length >= 3) {
		check("name");
	} else {
		document.getElementById("p2_title").innerHTML =
			"Name too short, at least 3 characters";
	}
}

function check(type) { //Check if name / test exist
	var data = document.getElementById("join_number").value;
	if (type == "name") {
		data += "&name=" + document.getElementById("name")
			.value;
	}
	xmlrequest("check_" + type + "?join_number=" + data,
		function() {
			if (this.readyState == 4 && this.status == 200) {
				var ans = xmlstring_to_boolean(this.responseText);
				if (type == "test") {
					if (ans) {
						changeDiv();
					} else {
						document.getElementById("p1_title").innerHTML =
							"No such Game Pin, enter right one";
					}
				} else if (type == "name") {
					if (ans) {
						document.getElementById("join").submit();
					} else {
						document.getElementById("p2_title").innerHTML =
							"Name taken, choose another name";
					}
				}
			}
		}
	);
}
