# Documentation for Internal Communications
## Setup
Install python dependencies using `pip install -r requirements.txt`
Create an .env files with the following format:
```env
SOC_USERNAME=<soc username>
ULTRA_PW=<ultra96 password>
```

The following requires that the passwordless ssh into SOC has been set up as per `External-Communications/sshsetup.md`

Run the relay node on each laptop with for the given players using the following command
`python individual_component.py -m<player number> -p<relay port>`
For e.g. for player 1 components connecting to port 8081 on the ultra96: `python individual_component.py -m1 -p8081`
