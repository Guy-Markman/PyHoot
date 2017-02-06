PyHoot
Kahoot clone based on Python, final project for Gvahim

File:
https://docs.google.com/document/d/1LPCgrDlXF44W5gIg_f8bILYIs6acdJ8r-IFdwjgE3eI/edit?ts=58488d76#heading=h.n2jnyow8d3tg

Arguements:
		-h, --help            show this help message and exit
		--address ADDRESS [ADDRESS ...]
							The address(es) we will connect to, default
							['localhost:8080']
		--buff-size BUFF_SIZE
							Buff size for each time, default 1024
		--base BASE           Base directory
		--io-mode {select,poll}
							IO that will be used, default select.
							In windows only select availiable.
		--log-level {DEBUG,INFO,WARNING,CRITICAL,ERROR}
							Log level
		--log-file FILE       Logfile to write to, otherwise will log to console.

TODO:
- [X] Make server send files
- [ ] Test server sending images and text files
- [ ] Clock service
- [ ] Cokie service
- [ ] Creat XML class
- [ ] Hide\Find string in picture
