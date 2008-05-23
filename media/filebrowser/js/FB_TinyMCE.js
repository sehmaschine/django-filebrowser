function FileSubmit(FileURL) {
    var win = tinyMCEPopup.getWindowArg("window");
    var editorID = tinyMCEPopup.getWindowArg("editorID");
    win.document.getElementById(tinyMCEPopup.getWindowArg("input")).value = FileURL;
    if (win.getImageData) {
        win.getImageData(FileURL);
    }
    win.tinyMCEPopup.setWindowArg('editor_id', editorID);
    tinyMCEPopup.close();
}

var FileBrowserDialogue = {
    init : function () {
        // Here goes your code for setting your custom things onLoad.
    },
    fileSubmit : function (FileURL) {
        var URL = FileURL;
        var win = tinyMCEPopup.getWindowArg("window");

        // insert information now
        win.document.getElementById(tinyMCEPopup.getWindowArg("input")).value = URL;

        // for image browsers: update image dimensions
        if (win.ImageDialog.getImageData) win.ImageDialog.getImageData();
        if (win.ImageDialog.showPreviewImage) win.ImageDialog.showPreviewImage(URL);

        // close popup window
        tinyMCEPopup.close();
    }
}

tinyMCEPopup.onInit.add(FileBrowserDialogue.init, FileBrowserDialogue);

