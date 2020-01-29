
'use strict';

// Doc
    var Doc = function () {
    }
    Doc.prototype.get = function (selectors) {
        return document.querySelector(selectors);
    }
    var doc = new Doc();

// DateTime
    var DateTime = function () {
        this.date = new Date();
    }
    DateTime.prototype.addDays = function (days) {
        this.date.setDate(this.date.getDate() + days);
    }
    DateTime.prototype.prevMonth = function () {
        var tmpDate = new Date(this.date.getFullYear(), this.date.getMonth(), 1);
        tmpDate.setMonth(tmpDate.getMonth() - 1);

        this.date.setMonth(this.date.getMonth() - 1);
        while (tmpDate.getMonth() !== this.date.getMonth()) {
            this.addDays(-1);
        }
    }
    DateTime.prototype.nextMonth = function () {
        var tmpDate = new Date(this.date.getFullYear(), this.date.getMonth(), 1);
        tmpDate.setMonth(tmpDate.getMonth() + 1);

        this.date.setMonth(this.date.getMonth() + 1);
        while (tmpDate.getMonth() !== this.date.getMonth()) {
            this.addDays(-1);
        }
    }
    DateTime.prototype.addMonths = function (months) {
        if (months === 0) {
        } else if (months < 0) {
            for (var i = 0; i > months; --i) {
                this.prevMonth();
            }
        } else if (months > 0) {
            for (var i = 0; i < months; ++i) {
                this.nextMonth();
            }
        }
    }
    DateTime.prototype.prevYear = function () {
        var tmpMonth = this.date.getMonth();

        this.date.setFullYear(this.date.getFullYear() - 1);
        if (tmpMonth !== this.date.getMonth()) {
            this.addDays(-1);
        }
    }
    DateTime.prototype.nextYear = function () {
        var tmpMonth = this.date.getMonth();

        this.date.setFullYear(this.date.getFullYear() + 1);
        while (tmpMonth !== this.date.getMonth()) {
            this.addDays(-1);
        }
    }
    DateTime.prototype.addYears = function (years) {
        if (years === 0) {
        } else if (years < 0) {
            for (var i = 0; i > years; --i) {
                this.prevYear();
            }
        } else if (years > 0) {
            for (var i = 0; i < years; ++i) {
                this.nextYear();
            }
        }
    }
    DateTime.prototype.toDateTimeStr = function () {
        var padZero = function (num) {
            return (num < 10) ? '0' + num.toString() : num.toString();
        }

        var year = this.date.getFullYear();
        var month = padZero(this.date.getMonth() + 1);
        var dayOfMonth = padZero(this.date.getDate());
        var hour = padZero(this.date.getHours());
        var minute = padZero(this.date.getMinutes());
        var second = padZero(this.date.getSeconds());

        return [year, month, dayOfMonth].join('-') + ' ' + [hour, minute, second].join(':');
    }
    DateTime.prototype.toUTCStr = function () {
        return this.date.toUTCString();
    }

// Cookie
    var Cookie = function () {
    }
    Cookie.prototype.get = function (name, defaultValue) {
        var documentCookie = '; ' + document.cookie;
        var cookieSplit = documentCookie.split('; ' + name + '=');

        if (cookieSplit.length === 2) {
            return cookieSplit.pop().split('; ').shift();
        }

        return defaultValue;
    }
    Cookie.prototype.set = function (name, value, days) {
        var expires = '';
        if (days > 0) {
            var dateTime = new DateTime();
            dateTime.addDays(days);

            expires = ' expires=' + dateTime.toUTCStr() + ';';
        }

        document.cookie = name + '=' + encodeURIComponent(value) + ';' + expires + ' path=/;';
    }
    Cookie.prototype.del = function (name) {
        document.cookie = name + '=; path=/;';
    }
    var cookie = new Cookie();

// XMLHttp
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

// WebSock
    var WebSock = function () {
        this.ws = null;
    }
    WebSock.prototype.connect = function (wsServerURL, protocol, openCallback, messageCallback) {
        this.ws = new WebSocket(wsServerURL, protocol);

        this.ws.addEventListener('open', openCallback);
        this.ws.addEventListener('message', messageCallback);
        
        this.ws.addEventListener('error', function () {
            alert('WebSock.NetworkError');
        })
    }
    WebSock.prototype.send = function (data) {
        if (this.ws === null || this.ws.readyState !== this.ws.OPEN) {
            return;
        }

        this.ws.send(data);
    }
    WebSock.prototype.disconnect = function (data) {
        if (this.ws === null || this.ws.readyState !== this.ws.OPEN) {
            return;
        }

        this.ws.close();
    }
    var webSock = new WebSock();

// Storage
    var eStorage = {
        SESSION: 1, // sessionStorage
        LOCAL: 2 // localStorage
    }
    
    var Storage = function () {
    }
    Storage.prototype.get = function (type, key, defaultValue) {
        var value = (type === eStorage.SESSION) ? sessionStorage.getItem(key) : localStorage.getItem(key);
        return (value === null) ? defaultValue : value;
    }
    Storage.prototype.set = function (type, key, value) {
        if (type === eStorage.SESSION) {
            sessionStorage.setItem(key, value);
        } else if (type === eStorage.LOCAL) {
            localStorage.setItem(key, value);
        }
    }
    Storage.prototype.remove = function (type, key) {
        if (type === eStorage.SESSION) {
            sessionStorage.removeItem(key);
        } else if (type === eStorage.LOCAL) {
            localStorage.removeItem(key);
        }
    }
    var storage = new Storage();
