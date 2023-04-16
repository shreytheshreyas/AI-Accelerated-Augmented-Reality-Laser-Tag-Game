# Documentation for External Communications
## Set up
* Set up SSH to Ultra96 via tunnel as shown in `sshsetup.md`.
* Copy files to Ultra96 using the command `scp Ultra96 ult:~/dev/`
* SSH into Ultra 96 using `ssh ult` and login to root using the command `su -l`
* Go into `/home/xilinx/dev/Ultra96` folder and install python dependencies using `pip install -r requirements.txt`

## Running Ultra96
* SSH into Ultra 96 using `ssh ult` and login to root using the command `su -l`
* Go into `/home/xilinx/dev/Ultra96` folder 
* Run `python Ultra96.py <relay_port> <eval_addr> <eval_port>`
* When Relay Nodes are connected and components are connected, press `<Enter>` to start the connection to Eval Server



