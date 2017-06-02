/**
 * @file Files/game.js Implementation of @ref game
 * @defgroup game Functions for game.js
 * @addtogroup game
 * @{
 */


// The current state of the game
var state = "wait";

//Checking every second if need to moved
check_move_to_next();

/**
 * Disconnecting user from the system
 * @return nothing
 */
function disconnect_user() {
	xmlrequest("diconnect_user", function() {
		if (this.readyState == 4) {
			window.location.href = '/';
		}
	});
}

/**
 * switch screens for the next screen
 * @return nothing
 */
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

/**
 * Send the answer the user clicked on
 * @param letter (string) the letter of the answer
 *
 */
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

/**
 * Get the score and place of the player from the server and print it to the screens
 * @return nothing
 */
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

/**
 * Add suffix to the number
 * @param i the number we want to add the suffix to
 * @returns the number with the suffix
 */
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

/**
 * Get the title of the question and print it in the right place
 *
 */
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

/**
 * check if there is a need to move to the next part
 * @return nothing
 */
function check_move_to_next() {
	xmlrequest("check_move_next_page",
		function() {
			if (this.readyState == 4 && this.status == 200) {
				if (xmlstring_to_boolean(this.responseText)) {
					switch (state) {
						case "wait":
							get_title()
							switch_screens();
							state = "question";
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
							get_title()
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

/** @} */
