#! /bin/bash





/data/venv/bin/python3 sasve_graphs.py


git add *
git commit -m "sdfsdfsd"
git push -u origin master


/data/venv/bin/python3 send_email.py
