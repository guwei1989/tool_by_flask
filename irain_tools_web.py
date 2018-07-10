#!/usr/local/bin/python
# coding: utf-8
import sys

from flask import Flask, render_template
import src.v3
import src.job
import src.frp

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False

src.v3.mount_on(app, '/api/v3')
src.job.mount_on(app, '/api/job')
src.frp.mount_on(app, '/api/frp')


@app.route('/')
def homepage():
    return render_template('base.html')


def run():
    port = 9494 if len(sys.argv) == 1 else int(sys.argv[1])
    app.run('0.0.0.0', port, threaded=True)


if __name__ == '__main__':
    run()
