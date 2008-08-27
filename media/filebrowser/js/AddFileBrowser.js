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
        // FileBrowser.no_thumb = FileBrowser.admin_media_prefix + FileBrowser.no_thumb;
        // // Get all p elements with help_text="FileBrowser ..."
        // // and add FileBrowserIcon as well as Image Preview
        // var help = document.getElementsBySelector('p.help');
        // for (var i=0; i<help.length; i++) {
        //     // check if p contains the text "FileBrowser"
        //     if (help[i].firstChild.data.substr(0,11) == "FileBrowser") {
        //         FileBrowser.addFileBrowseField(help[i]);
        //     }
        // }
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
}

addEvent(window, 'load', FileBrowser.init);

