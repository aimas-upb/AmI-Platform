for server in ami-daq-01 ami-daq-02 ami-daq-03 ami-daq-04 ami-daq-05 ami-crunch-02 ami-crunch-04 ami-crunch-05 ami-crunch-06
do
    echo "Redeploying $server..."
    ssh root@$server.local 'su -c "cd ~/AmI-Platform; ./deploy.sh --fresh" ami'
done
