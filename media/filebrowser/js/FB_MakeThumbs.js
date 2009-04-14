addEvent(window, "load", function () {
    var re = /\bfb_makethumblink\b/;
    var links = document.getElementsByTagName("a");
    links_make_thumb = [];
    for (i=0, len=links.length; i<len; i++) {
        link = links[i]
        if (link.className.match(re)) {
            url_parts = link.href.split("?");
            url_parts.push("");
            query_params = url_parts[1].split("&");
            query_params.push("ajax");
            url_parts[1] = query_params.join("&");
            xmlhttp.open("POST", url_parts[0] + "?" + url_parts[1], false);
            xmlhttp.send(null);
            img = document.createElement("IMG");
            img.src = xmlhttp.responseText;
            img.alt = img.title = "View Image";
            link.appendChild(img);
            link.className = link.className.replace(re, "");
            link.href = xmlhttp.responseText.replace(
                /^(.+\/)_cache\/thumb_([^\/]+)\.png$/,
                "$1$2"
            );
        }
    }
});
