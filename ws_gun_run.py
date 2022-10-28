# wrapper for gunicorn running

from queries import *


# app run for gunicorn

gun_run = app.run(host='0.0.0.0', port=4444)



