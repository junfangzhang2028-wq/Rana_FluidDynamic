#!/bin/bash
HOST=aqueousoutflow.ads.northwestern.edu
ssh -t rsf895@$HOST '
sudo rm /home/njf390/frontend/*
sudo rm /var/www/html/*'
scp ./aq-ui-dist/frontend/* rsf895@$HOST:/home/njf390/frontend
ssh -t rsf895@$HOST '
sudo scp /home/njf390/frontend/* /var/www/html
sudo systemctl restart httpd24-httpd'