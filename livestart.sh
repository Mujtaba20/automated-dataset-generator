pm2 start ddc
pm2 delete ddc
pm2 start app.py --name ddc
pm2 logs
