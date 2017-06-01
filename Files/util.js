/**
 * @file Files\util.js Implementation of @ref PyHoot.util
 * Util file
 * @defgroup front_end Frontend implementation
 * @defgroup front_end.util Frontend implementation from Util files
 * @addtogroup front_end
 * @addtogroup front_end.util
 * @{
 */

/**
 * XMLHttpRequest
 * @return Nothing
 */
function xmlrequest(url, state_change) {
	var xhttp = new XMLHttpRequest();
	if (state_change !== null) {
		xhttp.onreadystatechange = state_change;
	}
	xhttp.open("GET", url, true);
	xhttp.send();
}

/**
 * Create xml file from xml string
 */
function parse_xml_from_string(xml_string) {
	parser = new DOMParser();
	return parser.parseFromString(xml_string, "text/xml");
}

/**
 * Create boolean from xml string
 */
function xmlstring_to_boolean(xmlstring) {
	return parse_xml_from_string(xmlstring).getElementsByTagName("Root")[0].getAttribute("answer") == "True";

}

/** @} */
