var FileBrowser = {
    // this is set automatically
    admin_media_prefix: '',
    // change this
    thumb_prefix: 'thumb_',
    no_thumb: 'filebrowser/img/no_thumb.gif',
    
    init: function() {
        // Deduce admin_media_prefix by looking at the <script>s in the
        // current document and finding the URL of *this* module.
        var scripts = document.getElementsByTagName('script');
        for (var i=0; i<scripts.length; i++) {
            if (scripts[i].src.match(/AddFileBrowser/)) {
                var idx = scripts[i].src.indexOf('filebrowser/js/AddFileBrowser');
                FileBrowser.admin_media_prefix = scripts[i].src.substring(0, idx);
                break;
            }
        }
        FileBrowser.no_thumb = FileBrowser.admin_media_prefix + FileBrowser.no_thumb;
        // Get all p elements with help_text="FileBrowser ..."
        // and add FileBrowserIcon as well as Image Preview
        var help = document.getElementsBySelector('p.help');
        for (var i=0; i<help.length; i++) {
            // check if p contains the text "FileBrowser"
            if (help[i].firstChild.data.substr(0,11) == "FileBrowser") {
                FileBrowser.addFileBrowseField(help[i]);
            }
        }
    },
    // get Thumbnail
    getThumb: function(fileSRC) {
        thumbnail = "";
        if (fileSRC) {
            file_name = fileSRC.split("/");
            file_name_length = file_name.length - 1;
            thumb_name = FileBrowser.thumb_prefix + file_name[file_name_length];
            thumb_src = fileSRC.replace(file_name[file_name_length], thumb_name);
            thumbnailIMG = new Image();
            thumbnailIMG.src = encodeURI(thumb_src);
            file_extension = file_name[file_name_length].split(".")[1];
            if (file_extension && file_extension.toLowerCase() != "jpg" && file_extension.toLowerCase() != "gif" && file_extension.toLowerCase() != "png") {
                thumbnail = "";
            } else {
                thumbnail = thumbnailIMG.src;
            }
        }
        return thumbnail;
    },
    // get help path
    getHelpPath: function(help) {
        if (help.firstChild.data.indexOf('/') >= 11) {
            helpPath = help.firstChild.data.substr(help.firstChild.data.indexOf('/'));
        } else {
            helpPath = '/';
        }
        return helpPath;
    },
    // add FileBrowseField
    addFileBrowseField: function(help) {
        // check if there's an image in the input-field before the help_text
        fileSRC = help.previousSibling.previousSibling.value;
        thumbnail = FileBrowser.getThumb(fileSRC);
        // FileBrowser: Path
        helpPath = FileBrowser.getHelpPath(help);
        // Link to FileBrowser (search_icon)
        var inputfield_id = help.previousSibling.previousSibling.getAttribute('id');
        var fb_link = quickElement('a', help.parentNode, '', 'href', 'javascript:FileBrowser.show("'+inputfield_id+'", "'+helpPath+'");');
        var fb_icon = quickElement('img', fb_link, '', 'src', FileBrowser.admin_media_prefix + 'filebrowser/img/icon_search.png');
        // Image Preview
        if (thumbnail) {
            var img_preview = quickElement('p', help.parentNode, '', 'class', 'help', 'style', 'display:block;');
            var img_link = quickElement('a', img_preview, '', 'href', fileSRC, 'target', '_blank');
            var image = quickElement('img', img_link, '', 'src', thumbnail, 'id', 'image_'+inputfield_id, 'class', 'preview', 'onError', 'FileBrowser.removePreview("image_'+inputfield_id+'")');
        } else {
            var img_preview = quickElement('p', help.parentNode, '', 'class', 'help', 'style', 'display:none;');
            var image = quickElement('img', img_preview, '', 'src', '', 'id', 'image_'+inputfield_id, 'class', 'preview');
        }
        // add on change handle for input_fields
        help.previousSibling.previousSibling.setAttribute('onchange', 'javscript:FileBrowser.fieldChange("'+inputfield_id+'");');
        // remove help_text
        help.parentNode.removeChild(help);
    },
    // change image_preview if input field value is changed
    fieldChange: function(id) {
        var inputfield = document.getElementById(id);
        if (inputfield.value == "") {
            inputfield.parentNode.lastChild.setAttribute('style', 'display: none;');
        } else {
            imgSRC = inputfield.value;
            thumbnail = FileBrowser.getThumb(imgSRC);
            inputfield.parentNode.lastChild.firstChild.setAttribute('src', thumbnail);
            inputfield.parentNode.lastChild.setAttribute('style', 'display: block;');
        }
    },
    // show FileBrowser
    show: function(id, helpPath) {
        var href = "/admin/filebrowser" + helpPath + "?pop=1";
        var id2=String(id).split(".").join("___");
        FBWindow = window.open(href, String(id2), 'height=600,width=840,resizable=yes,scrollbars=yes');
        FBWindow.focus();
    },
    removePreview: function(id) {
        document.getElementById(id).setAttribute('src', FileBrowser.no_thumb);
        this_img = document.getElementById(id);
        parent_node = document.getElementById(id).parentNode.parentNode;
        parent_link = document.getElementById(id).parentNode;
        // if there's a link, remove the link and append the new child
        if (parent_link.nodeName == "A") {
            document.getElementById(id).parentNode.parentNode.removeChild(parent_link);
            parent_node.appendChild(this_img);
        }
    }
}

addEvent(window, 'load', FileBrowser.init);

