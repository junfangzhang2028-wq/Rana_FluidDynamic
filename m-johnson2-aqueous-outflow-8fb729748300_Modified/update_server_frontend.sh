#!/bin/bash
HOST=aqueousoutflow.ads.northwestern.edu
ssh -t $HOST '
sudo rm /home/njf390/frontend/*
sudo rm /var/www/html/*'
scp ./aq-ui-dist/frontend/* $HOST:/home/njf390/frontend
ssh -t $HOST '
sudo scp /home/njf390/frontend/* /var/www/html
sudo systemctl restart httpd24-httpd'