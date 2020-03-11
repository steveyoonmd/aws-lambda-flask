'use strict';

// Doc
let Doc = function () {
};
Doc.prototype.get = function (selectors) {
    return document.querySelector(selectors);
};
let doc = new Doc();

// DateTime
let DateTime = function () {
    this.date = new Date();
};
DateTime.prototype.addDays = function (days) {
    this.date.setDate(this.date.getDate() + days);
};
DateTime.prototype.prevMonth = function () {
    let tmpDate = new Date(this.date.getFullYear(), this.date.getMonth(), 1);
    tmpDate.setMonth(tmpDate.getMonth() - 1);

    this.date.setMonth(this.date.getMonth() - 1);
    while (tmpDate.getMonth() !== this.date.getMonth()) {
        this.addDays(-1);
    }
};
DateTime.prototype.nextMonth = function () {
    let tmpDate = new Date(this.date.getFullYear(), this.date.getMonth(), 1);
    tmpDate.setMonth(tmpDate.getMonth() + 1);

    this.date.setMonth(this.date.getMonth() + 1);
    while (tmpDate.getMonth() !== this.date.getMonth()) {
        this.addDays(-1);
    }
};
DateTime.prototype.addMonths = function (months) {
    if (months === 0) {
    } else if (months < 0) {
        for (let i = 0; i > months; --i) {
            this.prevMonth();
        }
    } else if (months > 0) {
        for (let i = 0; i < months; ++i) {
            this.nextMonth();
        }
    }
};
DateTime.prototype.prevYear = function () {
    let tmpMonth = this.date.getMonth();

    this.date.setFullYear(this.date.getFullYear() - 1);
    if (tmpMonth !== this.date.getMonth()) {
        this.addDays(-1);
    }
};
DateTime.prototype.nextYear = function () {
    let tmpMonth = this.date.getMonth();

    this.date.setFullYear(this.date.getFullYear() + 1);
    while (tmpMonth !== this.date.getMonth()) {
        this.addDays(-1);
    }
};
DateTime.prototype.addYears = function (years) {
    if (years === 0) {
    } else if (years < 0) {
        for (let i = 0; i > years; --i) {
            this.prevYear();
        }
    } else if (years > 0) {
        for (let i = 0; i < years; ++i) {
            this.nextYear();
        }
    }
};
DateTime.prototype.toDateTimeStr = function () {
    let padZero = function (num) {
        return (num < 10) ? '0' + num.toString() : num.toString();
    }

    let year = this.date.getFullYear();
    let month = padZero(this.date.getMonth() + 1);
    let dayOfMonth = padZero(this.date.getDate());
    let hour = padZero(this.date.getHours());
    let minute = padZero(this.date.getMinutes());
    let second = padZero(this.date.getSeconds());

    return [year, month, dayOfMonth].join('-') + ' ' + [hour, minute, second].join(':');
};
DateTime.prototype.toUTCStr = function () {
    return this.date.toUTCString();
};

// Cookie
let Cookie = function () {
};
Cookie.prototype.get = function (name, defaultValue) {
    let documentCookie = '; ' + document.cookie;
    let cookieSplit = documentCookie.split('; ' + name + '=');

    return (cookieSplit.length === 2) ? cookieSplit.pop().split('; ').shift() : defaultValue;
};
Cookie.prototype.set = function (name, value, days) {
    let expires = '';
    if (days > 0) {
        let dateTime = new DateTime();
        dateTime.addDays(days);

        expires = ' expires=' + dateTime.toUTCStr() + ';';
    }

    document.cookie = name + '=' + encodeURIComponent(value) + ';' + expires + ' path=/;';
};
Cookie.prototype.del = function (name) {
    document.cookie = name + '=; path=/;';
};
let cookie = new Cookie();

// XMLHttp
let eHttp = {
    GET: 'GET',
    POST: 'POST',
    JSON: 'JSON',
    UPLOAD: 'UPLOAD'
};

let XMLHttp = function () {
    this.xhr = new XMLHttpRequest();
    this.xhr.addEventListener('error', function () {
        window.alert('XMLHttp.NetworkError');
    });

    this.prevCallback = null;
};
XMLHttp.prototype.request = function (type, url, data, withCredentials, callback) {
    if (typeof this.prevCallback === 'function') {
        this.xhr.removeEventListener('load', this.prevCallback);
        this.prevCallback = null;
    }

    this.xhr.addEventListener('load', callback);
    this.prevCallback = callback;

    let content_type = '';
    let body = null;

    if (type === eHttp.GET) {
        if (data !== null) {
            url += '?' + (new URLSearchParams(data)).toString();
        }
        content_type = 'application/x-www-form-urlencoded';
        body = null;
    } else if (type === eHttp.POST) {
        content_type = 'application/x-www-form-urlencoded';
        body = (new URLSearchParams(data)).toString();
    } else if (type === eHttp.JSON) {
        content_type = 'application/json';
        body = JSON.stringify(data);
    } else if (type === eHttp.UPLOAD) {
        // browser should put content_type by itself when upload
        body = data;
    }

    this.xhr.open(type === eHttp.GET ? 'GET' : 'POST', url, true);

    if (type === eHttp.UPLOAD) {
        // When you send multipart/form-data to AWS Lambda via AWS API Gateway,
        // Python receives the multipart body as utf-8 string, even if it's an image file.
        // For Python, the multipart body needs to be encoded in base64.
        // 1. AWS API Gateway -> Resources -> Create Method -> Use Lambda Proxy integration
        // 2. AWS API Gateway -> Settings -> Binary Media Types -> multipart/form-data
        // 3. Browser -> XMLHttpRequest -> xhr.setRequestHeader('Accept', 'multipart/form-data');
        this.xhr.setRequestHeader('Accept', 'multipart/form-data');
    } else {
        this.xhr.setRequestHeader('Content-Type', content_type);
    }

    if (withCredentials === true) {
        this.xhr.withCredentials = true;
        this.xhr.setRequestHeader('x-forced-preflight', 'true');
    }

    this.xhr.send(body);
};
let xmlHttp = new XMLHttp();

// WebSock
let WebSock = function () {
    this.ws = null;
};
WebSock.prototype.connect = function (wsServerURL, protocol, openCallback, messageCallback) {
    this.ws = new WebSocket(wsServerURL, protocol);

    this.ws.addEventListener('error', function (evt) {
        window.alert('WebSock.NetworkError');
    });
    this.ws.addEventListener('open', openCallback);
    this.ws.addEventListener('message', messageCallback);
};
WebSock.prototype.send = function (data) {
    if (this.ws === null || this.ws.readyState !== this.ws.OPEN) {
        return;
    }

    this.ws.send(data);
};
WebSock.prototype.disconnect = function (evt) {
    if (this.ws === null || this.ws.readyState !== this.ws.OPEN) {
        return;
    }

    this.ws.close();
};
let webSock = new WebSock();

// Storage
let eStorage = {
    SESSION: 1, // sessionStorage
    LOCAL: 2 // localStorage
};

let Storage = function () {
};
Storage.prototype.get = function (type, key, defaultValue) {
    let value = (type === eStorage.SESSION) ? sessionStorage.getItem(key) : localStorage.getItem(key);
    return (value === null) ? defaultValue : value;
};
Storage.prototype.set = function (type, key, value) {
    if (type === eStorage.SESSION) {
        sessionStorage.setItem(key, value);
    } else if (type === eStorage.PERSIST) {
        localStorage.setItem(key, value);
    }
};
Storage.prototype.remove = function (type, key) {
    if (type === eStorage.SESSION) {
        sessionStorage.removeItem(key);
    } else if (type === eStorage.PERSIST) {
        localStorage.removeItem(key);
    }
};
let storage = new Storage();

let navHTML = './lib_nav.html';
let footerHTML = './lib_footer.html';
let messageHTML = './lib_message.html';

let loadHTML = function (styleHTML, showNav, callback) {
    xmlHttp.request(eHttp.GET, styleHTML, null, true, function () {
        doc.get('head').innerHTML += this.responseText;

        xmlHttp.request(eHttp.GET, navHTML, null, true, function () {
            if (showNav) {
                doc.get('nav').innerHTML = this.responseText;

                doc.get('.nav-icon').addEventListener('click', function () {
                    doc.get('nav').classList.add('resp');
                });
            }

            xmlHttp.request(eHttp.GET, footerHTML, null, true, function () {
                doc.get('footer').innerHTML = this.responseText;
                doc.get('.copyright-year').innerHTML = (new Date()).getFullYear();

                xmlHttp.request(eHttp.GET, messageHTML, null, true, function () {
                    doc.get('.msg-container').innerHTML = this.responseText;

                    doc.get('.msg-container').addEventListener('click', function () {
                        this.style.display = 'none';
                    });

                    let baseURL = '';
                    if (window.location.href.indexOf('/default') > -1) {
                        baseURL = '/default';
                    }

                    callback(baseURL);
                });
            });
        });
    });
};

let parseRespText = function (_this) {
    console.log(_this.responseText);

    if (_this.status !== 200) {
        window.alert('XMLHttp.Status = ' + _this.status);
        return null;
    }

    let respText = _this.responseText;
    if (respText[0] !== '{' && respText[0] !== '[') {
        return null;
    }

    let parsed = null;
    try {
        parsed = JSON.parse(respText);
    } catch (ex) {
        console.log(ex);
    }

    if (parsed === null) {
        return null;
    }

    if (('err' in parsed) === false) {
        return null;
    }

    if (parsed.err === 0) {
        return parsed;
    }

    let errStr = parsed.err.toString();
    let errMsg = (errStr in errorMessages) ? errorMessages[errStr] : errStr;
    window.alert(errMsg);

    if ('url' in parsed && parsed.url !== '') {
        window.location.href = parsed.url;
    }

    return null;
};
