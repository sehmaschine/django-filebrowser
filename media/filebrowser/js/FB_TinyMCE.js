function FileSubmit(FileURL) {
    var win = tinyMCE.getWindowArg("window");
    var editorID = tinyMCE.getWindowArg("editorID");
    win.document.getElementById(tinyMCE.getWindowArg("input")).value = FileURL;
    if (win.getImageData) {
        win.getImageData(FileURL);
    }
    win.tinyMCE.setWindowArg('editor_id', editorID);
    tinyMCEPopup.close();
}
