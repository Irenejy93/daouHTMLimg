#! /bin/bash

/data/venv/bin/python3 graphgenerator.py


git add *
git commit -m "GraphGenerator"
git push -u origin master


/data/venv/bin/python3 mail_sender_graph.py

