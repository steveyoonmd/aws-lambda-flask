
'use strict';

// Doc
    var Doc = function () {
    }
    Doc.prototype.get = function (selectors) {
        return document.querySelector(selectors);
    }
    var doc = new Doc();

// Time
    var Time = function () {
        this.d = new Date();
    }
    Time.prototype.addDays = function (days) {
        this.d.setDate(this.d.getDate() + days);
    }
    Time.prototype.prevMonth = function () {
        var tmpDate = new Date(this.d.getFullYear(), this.d.getMonth(), 1);
        tmpDate.setMonth(tmpDate.getMonth() - 1);

        this.d.setMonth(this.d.getMonth() - 1);
        while (tmpDate.getMonth() !== this.d.getMonth()) {
            this.addDays(-1);
        }
    }
    Time.prototype.nextMonth = function () {
        var tmpDate = new Date(this.d.getFullYear(), this.d.getMonth(), 1);
        tmpDate.setMonth(tmpDate.getMonth() + 1);

        this.d.setMonth(this.d.getMonth() + 1);
        while (tmpDate.getMonth() !== this.d.getMonth()) {
            this.addDays(-1);
        }
    }
    Time.prototype.addMonths = function (months) {
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
    Time.prototype.prevYear = function () {
        var tmpMonth = this.d.getMonth();

        this.d.setFullYear(this.d.getFullYear() - 1);
        if (tmpMonth !== this.d.getMonth()) {
            this.addDays(-1);
        }
    }
    Time.prototype.nextYear = function () {
        var tmpMonth = this.d.getMonth();

        this.d.setFullYear(this.d.getFullYear() + 1);
        while (tmpMonth !== this.d.getMonth()) {
            this.addDays(-1);
        }
    }
    Time.prototype.addYears = function (years) {
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
    Time.prototype.toDateTimeStr = function () {
        var year = this.d.getFullYear().toString();
        var month = (this.d.getMonth() + 1) < 10 ? '0' + (this.d.getMonth() + 1).toString() : (this.d.getMonth() + 1).toString();
        var date = this.d.getDate() < 10 ? '0' + this.d.getDate().toString() : this.d.getDate().toString();
        var hour = this.d.getHours() < 10 ? '0' + this.d.getHours().toString() : this.d.getHours().toString();
        var minute = this.d.getMinutes() < 10 ? '0' + this.d.getMinutes().toString() : this.d.getMinutes().toString();
        var second = this.d.getSeconds() < 10 ? '0' + this.d.getSeconds().toString() : this.d.getSeconds().toString();
        
        return [year, month, date].join('-') + ' ' + [hour, minute, second].join(':');
    }
    Time.prototype.toUTCStr = function () {
        return this.d.toUTCString();
    }

// Cookie
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
            var time = new Time();
            time.addDays(days);

            expires = ' expires=' + time.toUTCStr() + ';';
        }

        document.cookie = name + '=' + encodeURIComponent(newValue) + ';' + expires + ' path=/;';
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

// Storage
    eStorage = {
        PERSIST: 1, // localStorage
        SESSION: 2, // sessionStorage
    }
