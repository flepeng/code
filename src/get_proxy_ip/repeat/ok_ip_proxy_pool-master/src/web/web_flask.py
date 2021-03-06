from flask import Flask, jsonify

from src.database.sqlite_opt import sqlite_opt

app = Flask(__name__)


@app.route('/')
def index():
    """δΈ»ι‘΅
    """
    return '''
        <h1>πWelcome to Home Pageπ</h1>
        <h1>πββοΈπ€·ββοΈπββοΈπ€·ββοΈπββοΈπ€·ββοΈπββοΈπ€·ββοΈπββοΈπ€·ββοΈπββοΈπ€·ββοΈπββοΈπ€·ββοΈ</h1>
        <h2>APIs:</h2>
        <h3>Get an usable proxy:</h3>
        <p>/get</p>
        <h3>Get all usable proxies:</h3>
        <p>/get_all</p>
    '''


@app.route('/get')
def get_proxy():
    """θ·εεδΈͺδ»£η
    """
    proxy = sqlite_opt.get_one_in_page()
    if proxy:
        return jsonify({
            'code': 200,
            'proxy': proxy.url
        })
    else:
        return jsonify({'code': 500, 'msg': 'server error'})


@app.route('/get_all')
def get_all_proxy():
    """θ·εε¨ι¨(ε―η¨η)δ»£η
    """
    proxy_list = sqlite_opt.get_all_in_page()
    if proxy_list:
        return jsonify({
            'code': 200,
            'proxies': [proxy.url for proxy in proxy_list]
        })
    else:
        return jsonify({'code': 500, 'msg': 'server error'})
