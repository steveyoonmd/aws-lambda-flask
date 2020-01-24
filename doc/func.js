
'use strict';

var Doc = function () {
}
Doc.prototype.get = function (selectors) {
    return document.querySelector(selectors);
}
var doc = new Doc();

var Cookie = function () {
}
Cookie.prototype.get = function (name, defaultValue) {
    var documentCookie = '; ' + document.cookie;
    var pairs = documentCookie.split('; ' + name + '=');

    if (pairs.length === 2) {
      return pairs.pop().split('; ').shift();
    }

    return defaultValue;
}
Cookie.prototype.set = function (name, newValue, days) {
    var expires = '';
    if (days > 0) {
        var date = new Date();
        date.setDate(date.getDate() + days);

        expires = ' expires=' + date.toUTCString() + ';';
    }

    document.cookie = name + '=' + encodeURIComponent(newValue) + ';' + expires + ' path=/;';
}
Cookie.prototype.del = function (name) {
    document.cookie = name + '=; path=/;';
}
var cookie = new Cookie();

var eHttp = {
    GET: 'GET',
    POST: 'POST',
    JSON: 'JSON',
    UPLOAD: 'UPLOAD'
}

var XMLHttp = function () {
    this.xhr = new XMLHttpRequest();
    this.xhr.addEventListener('error', function () {
        alert('XMLHttp.NetworkError');
    });

    this.prevCallback = null;
}
XMLHttp.prototype.request = function (type, url, data, withCredentials, callback) {
    if (typeof this.prevCallback === 'function') {
        this.xhr.removeEventListener('load', this.prevCallback);
        this.prevCallback = null;
    }
    
    this.xhr.addEventListener('load', callback);
    this.prevCallback = callback;

    var method = '';
    var body = null;

    if (type === eHttp.GET) {
        method = 'GET';
        if (data !== null) {
            url += '?' + (new URLSearchParams(data)).toString();
        }
        body = null;
    } else if (type === eHttp.POST) {
        method = 'POST';
        body = data;
    } else if (type === eHttp.JSON) {
        method = 'POST';
        body = JSON.stringify(data);
    } else if (type === eHttp.UPLOAD) {
        method = 'POST';
        body = data;
    }

    this.xhr.open(method, url, true);
    if (type == eHttp.JSON) {
        this.xhr.setRequestHeader('Content-Type', 'application/json');
    }
    if (withCredentials === true) {
        this.xhr.withCredentials = true;
        this.xhr.setRequestHeader('x-forced-preflight', 'true');
    }
    this.xhr.send(body);
}
var xmlHttp = new XMLHttp();
