var FileBrowserDialogue = {
    init : function () {
        // remove tinymce stylesheet.
        var allLinks = document.getElementsByTagName("link");
        allLinks[allLinks.length-1].parentNode.removeChild(allLinks[allLinks.length-1]);
    },
    fileSubmit : function (FileURL) {
        var URL = FileURL;
        var win = tinyMCEPopup.getWindowArg("window");
        
        // insert information now
        win.document.getElementById(tinyMCEPopup.getWindowArg("input")).value = URL;
        
        // for image browsers: update image dimensions
        if (win.ImageDialog) {
            img = new Image();
            img.src = FileURL;
            win.ImageDialog.updateImageData(img, '');
        } 
        
        // close popup window
        tinyMCEPopup.close();
    }
}

tinyMCEPopup.onInit.add(FileBrowserDialogue.init, FileBrowserDialogue);

