# This branch is for restful version website

(This repo is not finish yet)

# Architecture

```mermaid
    graph TD;
        A[User] -->|Send Request| B(Django);
        B -->|stream request| C[nginx];
        B <--> |video, series metadata| D[Database];
        B -->|upload video files| E[Local file];
        E --> |load from local|C;
        C --> |stream url|B ;
        B -->|stream url that will expire| A;
```

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

Then run scrpit to start nginx
`cd scrpit`
`./nginx_start.sh`