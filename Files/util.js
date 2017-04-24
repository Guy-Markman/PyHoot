function xmlrequest(url, state_change) {
                var xhttp = new XMLHttpRequest();
                if (state_change !== null) {
                    xhttp.onreadystatechange = state_change;
                }
                xhttp.open("GET", url, true);
                xhttp.send();
            }
function parse_xml_from_string(xml_string){
	parser = new DOMParser();
	return parser.parseFromString(xml_string, "text/xml");
}