function FileSubmit(FileURL, ThumbURL) {
    // window.name is the name of the input-field
    // below is the construction of the preview:
    // <label for="id_image_overview">Label:</label>
    // INPUT-FIELD
    // <input onchange='javscript:FileBrowser.fieldChange("id_...");' id="id_..." class="vTextField" name="..." value="" type="text">
    // SEARCH ICON
    // <a href='javascript:FileBrowser.show("id_...", "/");'><img src="/media/admin/filebrowser/img/icon_search.png"></a>
    // IMAGE PREVIEW OR ICON (FOR OTHER DOCUMENT-TYPES)
    // <p style="display: block;" class="help"><a target="_blank" href="link/to/image"><img src="/path/to/thumb" id="image_id_..."></a></p>
    
    var wname=window.name.split("___").join(".");
    // get input field
    elem = opener.document.getElementById(wname);
    elem.value = FileURL;
    // get ID for the preview-image
    imgID = 'image_' + wname;
    
    p_elem = ""
    p_elem = opener.document.getElementById(imgID).parentNode;
    p_elem_fc = opener.document.getElementById(imgID).parentNode.firstChild;
    if (p_elem.nodeName != "P") {
        p_elem = opener.document.getElementById(imgID).parentNode.parentNode;
        p_elem_fc = opener.document.getElementById(imgID).parentNode.parentNode.firstChild;
    }
    if (ThumbURL && ThumbURL != "/media/img/filebrowser/filebrowser_Thumb.gif") {
        var temp_link = opener.document.createElement("a");
        temp_link.setAttribute("href", FileURL);
        temp_link.setAttribute("target", "_blank");
        var temp_image = opener.document.createElement("img");
        temp_image.setAttribute("id", imgID);
        temp_image.setAttribute("src", ThumbURL);
        temp_link.appendChild(temp_image);
        p_elem.setAttribute("style", "display:block");
        p_elem.removeChild(p_elem_fc);
        p_elem.appendChild(temp_link);
    } else if (ThumbURL == "/media/img/filebrowser/filebrowser_Thumb.gif") {
        opener.document.getElementById(imgID).parentNode.setAttribute("style", "display:block");
        opener.FileBrowser.removePreview(imgID);
    } else {
        opener.document.getElementById(imgID).parentNode.setAttribute("style", "display:none");
    }
    this.close();
}

