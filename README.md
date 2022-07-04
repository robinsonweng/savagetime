# This branch is for restful version website

(This repo is not finish yet)

# Usage

## Run as test server
1. Clone the repository<br>
`git clone https://github.com/robinsonweng/savagetime/tree/restful`

2. Create a python virtual enviroment using virtualvenv<br>
`virtualvenv venv`

3. Load the enviroment<br>
`source venv`

4. Install python dependency<br>
`pip install -r requirements.txt`

5. Run the script<br>
`./script/run.sh`

## deploy on uwsgi
`uwsgi -ini uwsgi.ini`


## Start nginx stream service
Link config folder under local nginx config file
`cd savage_nginx_conf`
`./link_this_dir.sh`