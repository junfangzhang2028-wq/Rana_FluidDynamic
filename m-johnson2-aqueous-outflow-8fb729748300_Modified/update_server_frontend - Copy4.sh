#!/bin/bash
HOST=aqueousoutflow.ads.northwestern.edu
ssh -t rsf895@$HOST '
sudo rm /home/rsf895/frontend/*
sudo rm /var/www/html/*'

scp ./aq-ui-dist/frontend/* rsf895@$HOST:/home/rsf895/frontend
ssh -t rsf895@$HOST '
sudo scp /home/rsf895/frontend/* /var/www/html
sudo systemctl restart httpd24-httpd'