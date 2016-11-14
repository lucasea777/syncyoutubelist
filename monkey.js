// ==UserScript==
// @name         synclist
// @namespace    https://www.youtube.com/*
// @version      1.0.0
// @description  FaceHack
// @author       Luks Sky Walker
// @match        https://www.youtube.com/*
// @grant        GM_setValue
// @grant        GM_getValue
// @grant        GM_xmlhttpRequest
// @connect      127.0.0.1
// @require      http://code.jquery.com/jquery-latest.js
// @require      http://cdnjs.cloudflare.com/ajax/libs/toastr.js/latest/toastr.min.js
// @run-at       document-start
// ==/UserScript==
(function() {
    'use strict';
    toastr.options.timeOut = 0;
    toastr.options.extendedTimeOut = 0;
    toastr.options.closeButton = true;
    var mievento;
    // Your code here...
    console.log("script running!");
    function main() {
        console.log("main!");
        function send(action, data={}, callback=undefined) {
            console.log("sending");
            GM_xmlhttpRequest({
                method: "GET",
                url: `http://127.0.0.1:8181/${action}?${$.param(data)}`,
                onload: function(response) {
                    console.log(response);
                    if(callback !== undefined)
                        callback(response);
                },
                onerror: function(response) {
                    console.log(response);
                    if(callback !== undefined)
                        callback(response);
                }
            });
        }
        /*function onlistchanged(fun) {
            var target = $("#appbar-main-guide-notification-container")[0];
            var observer = new MutationObserver(mutations => fun());
            observer.observe(target, { attributes: true, childList: true });
        }*/

        function setupbar() {
            $("#upload-btn").remove();
            $("body").append($("<link />", {
                rel: "stylesheet",
                href: "//cdnjs.cloudflare.com/ajax/libs/toastr.js/latest/toastr.min.css"
            }));
            //toastr.success("hi");
            var bar = $("#yt-masthead-user");
            bar.prepend($('<a />', {
                class: 'yt-uix-button yt-uix-sessionlink yt-uix-button-default yt-uix-button-size-default',
                id: "my-button",
                click: function(e){
                    send("sync", {}, undefined);
                },
                css: {
                    "margin-right": "10px"
                }
            }).append($('<span />', {
                class: 'yt-uix-button-content',
                text: "Sync"
            })));
            bar.prepend($('<a />', {
                class: 'yt-uix-sessionlink yt-uix-button-default yt-uix-button-size-default',
                id: "my-data",
                css: {
                    "margin-right": "10px",
                    "background": "white"
                }
            }).append($('<span />', {
                class: 'yt-uix-button-content',
                text: "data.."
            })));
        }
        function changebar({status, lastsync="", button:{enabled, name, action}={}, todownload="", cancelled=false}) {
            $("#my-data").text(`${status}${parseInt(todownload) !== 0 ? ' ('+todownload+')' : ''}, ${lastsync} ${cancelled ? 'cancelled' : ''}`);
            var my_button = $("#my-button");
            if (action !== undefined)
                my_button.off("click");
                my_button.click(action);
            if (enabled !== undefined)
                if (enabled)
                    my_button[0].removeAttribute("disabled");
                else
                    my_button[0].setAttribute("disabled", true);
            if (name !== undefined)
                $("#my-button span").text(name);
        }
        function ondata(data) {
            console.log(data);
            changebar({
                status: data.sync_status,
                button: {
                    enabled: data.penin,
                    name: (data.sync_status == "listo" ? "Sync" : "Cancel"),
                    action: () => send(data.sync_status == "listo" ? "sync" : "stop")
                },
                lastsync: data.lastsync,
                todownload: data.todownload,
                cancelled: data.cancelled
            });
            if (data.exception !== undefined  && data.exception !== null)
                toastr.error(data.exception[0], data.exception[1]);
        }
        setupbar();
        //onlistchanged(() => send("sync", {}));
        var poll_count = -1;
        function poll() {
            send("poll", {poll_count: poll_count}, function(response){
                if(response.status == 200){
                    console.log(response);
                    var data = JSON.parse(response.responseText);
                    poll_count = data.poll_count;
                    ondata(data);
                    poll();
                } else {
                    changebar({status:"conn error, retrying"});
                    setTimeout(() => poll(), 7000);
                }
            });
        }
        poll();
    }
    setTimeout(main, 3000);
    //window.onload = main;
})();