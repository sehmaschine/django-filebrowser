function CustomFileBrowser(field_name, url, type, win) {
    // alert("Field_Name: " + field_name + "\nURL: " + url + "\nType: " + type + "\nWin: " + win); // debug/testing
    var fileBrowserWindow = new Array();

    fileBrowserWindow['title'] = 'File Browser';
    fileBrowserWindow['file'] = "/admin/filebrowser/?pop=2";
    fileBrowserWindow['width'] = '820';
    fileBrowserWindow['height'] = '600';
    fileBrowserWindow['close_previous'] = 'no';
    tinyMCE.openWindow(fileBrowserWindow, {
      window : win,
      input : field_name,
      resizable : 'yes',
      scrollbars : 'yes',
      inline : 'yes',
      editorID: tinyMCE.getWindowArg('editor_id')
    });
    return false;
  }

function myCustomSetupContent(editor_id, body, doc) {
    if (body.innerHTML == "") {
        body.innerHTML = "<p>xxx</p>";
    }
}

tinyMCE.init({
    mode: "textareas",
    theme : "advanced",
    language : "de",
    theme_advanced_toolbar_location : "top",
    theme_advanced_toolbar_align : "left",
    theme_advanced_statusbar_location : "",
    theme_advanced_buttons1 : "formatselect,bold,italic,underline,bullist,numlist,undo,redo,link,unlink,image,code,fullscreen",
    theme_advanced_buttons2 : "",
    theme_advanced_buttons3 : "",
    theme_advanced_path : false,
    theme_advanced_blockformats : "p,h2,h3",
    width: '500',
    height: '200',
    editor_css : "/media/css/tinymce/ui_admin.css",
    content_css : "/media/css/tinymce/content_admin.css",
    popups_css : "/media/css/tinymce/popup_admin.css",
    plugins : "advimage,advlink,fullscreen",
    advimage_styles : "Linksbündig neben Text=img_left;Rechtsbündig neben Text=img_right;Eigener Block=img_block",
    advlink_styles : "intern (innerhalb von skipclass.at)=internal;extern (Link zu einer externen Seite)=external",
    advimage_update_dimensions_onchange: true,
    file_browser_callback : "CustomFileBrowser",
    relative_urls : false
});
