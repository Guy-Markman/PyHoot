/**
 * @file Files\new.js functions for game.html
 * @{
 */

/**
 * Check if test exist on the system
 */
function check_test_exist() {
	xmlrequest(
		"check_test_exist?quiz_name=" + document.getElementById("quiz_name").value,
		function() {
			if (this.readyState == 4 && this.status == 200) {
				if (xmlstring_to_boolean(this.responseText)) {
					document.getElementById("register_quiz").submit();
				} else {
					document.getElementById("title_register").innerHTML =
						"No such quiz!<br />Name of quiz:";
				}
			}
		}
	);
}

/** @} */
