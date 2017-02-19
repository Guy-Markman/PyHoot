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
        --io-mode {select, poll}
                            IO that will be used, default select.
                            In windows only select available.
        --log-level {DEBUG,INFO,WARNING,CRITICAL,ERROR}
                            Log level
        --log-file FILE       Logfile to write to, otherwise will log to console.

TODO:
- [X] Make server send files
- [X] Create XML class
- [X] Quiz editor (independent)
- [X] Add support to services
- [ ] Registrater players
- [ ] Show question on the screen and move to the next part (timer)
- [ ] Get answers and analyze them
- [ ] Update database of player with score
- [ ] Show answer and leaderboard
- [ ] End of game
- [ ] Hide\ Find string in picture
