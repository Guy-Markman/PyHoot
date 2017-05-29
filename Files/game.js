var state = "wait";
var exteranl = "";
check_move_to_next();

function disconnect_user() {
	xmlrequest("diconnect_user", function() {
		if (this.readyState == 4) {
			window.location.href = '/';
		}
	});
}

function switch_screens() {
	console.log(state);
	switch (state) {
		case "question":
			to = "wait";
			color = "#00401F"; /*Caliban Green*/
			break;
		case "leaderboard":
			to = "question";
			color = "White";
			break;
		case "wait":
			to = "question";
			color = "White"
			break;
		case "wait_question":
			state = "wait";
			to = "leaderboard";
			color = "#5A005A"; /*Xereus Purple*/
			break;
	}
	var from_style_display = document.getElementById(state).style.display;
	var to_style_display = document.getElementById(to).style.display;
	from_style_display = [to_style_display, to_style_display = from_style_display][0];
	document.getElementById(state).style.display = from_style_display;
	document.getElementById(to).style.display = to_style_display;
	document.body.style.background = color
}

function send_answer(letter) {
	xmlrequest("answer?letter=" + letter,
		function() {
			if (this.readyState == 4 && this.status == 200) {
				switch_screens();
				state = "wait_question";
			}
		}
	);
}

function get_score() {
	xmlrequest("get_score",
		function() {
			if (this.readyState == 4 && this.status == 200) {
				var score_place = parse_xml_from_string(this.responseText).getElementsByTagName("score_place")[0];
				document.getElementById("score").innerHTML = score_place.getAttribute("score");
				document.getElementById("place").innerHTML = ordinal_suffix_of(score_place.getAttribute("place"));
			}
		}
	);
}

function ordinal_suffix_of(i) {
	var j = i % 10,
		k = i % 100;
	if (j == 1 && k != 11) {
		return i + "st";
	}
	if (j == 2 && k != 12) {
		return i + "nd";
	}
	if (j == 3 && k != 13) {
		return i + "rd";
	}
	return i + "th";
}

function get_title() {
	xmlrequest("get_title",
		function() {
			if (this.readyState == 4 && this.status == 200) {
				document.getElementById("title").innerHTML =
					parse_xml_from_string(this.responseText).getElementsByTagName("title")[0].textContent
			}
		}
	)
}

function check_move_to_next() {
	xmlrequest("check_move_next_page",
		function() {
			if (this.readyState == 4 && this.status == 200) {
				if (xmlstring_to_boolean(this.responseText)) {
					switch (state) {
						case "wait":
							switch_screens();
							state = "question";
							get_title()
							xmlrequest("moved_to_next_question", null);
							break;
						case "question":
							switch_screens();
							state = "leaderboard";
							xmlrequest("moved_to_next_question", null);
							break;
						case "wait_question":
							get_score();
							switch_screens();
							state = "leaderboard";
							xmlrequest("moved_to_next_question", null);
							break;
						case "leaderboard":
							switch_screens();
							xmlrequest("moved_to_next_question", null);
							state = "question";
							break;
					}
				}
			}
		}
	);
	setTimeout(check_move_to_next, 1000);
}
