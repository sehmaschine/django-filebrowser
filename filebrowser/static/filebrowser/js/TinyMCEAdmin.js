function CustomFileBrowser(field_name, url, type, win) {

    var cmsURL = "/admin/filebrowser/browse/?pop=2";
    cmsURL = cmsURL + "&type=" + type;
    
    tinyMCE.activeEditor.windowManager.open({
        file: cmsURL,
        width: 820,  // Your dimensions may differ - toy around with them!
        height: 500,
        resizable: "yes",
        scrollbars: "yes",
        inline: "no",  // This parameter only has an effect if you use the inlinepopups plugin!
        close_previous: "no"
    }, {
        window: win,
        input: field_name,
        editor_id: tinyMCE.selectedInstance.editorId
    });
    return false;
}


tinyMCE.init({
    mode: "textareas",
    theme: "advanced",
    language: "en",
    skin: "o2k7",
    browsers: "gecko",
    dialog_type: "modal",
    object_resizing: true,
    cleanup_on_startup: true,
    forced_root_block: "p",
    remove_trailing_nbsp: true,
    theme_advanced_toolbar_location: "top",
    theme_advanced_toolbar_align: "left",
    theme_advanced_statusbar_location: "none",
    theme_advanced_buttons1: "formatselect,bold,italic,underline,bullist,numlist,undo,redo,link,unlink,image,code,fullscreen,pasteword,media,charmap",
    theme_advanced_buttons2: "",
    theme_advanced_buttons3: "",
    theme_advanced_path: false,
    theme_advanced_blockformats: "p,h2,h3,h4,h5,h6",
    width: '700',
    height: '200',
    plugins: "advimage,advlink,fullscreen,visualchars,paste,media,template,searchreplace",
    advimage_styles: "Linksbündig neben Text=img_left;Rechtsbündig neben Text=img_right;Eigener Block=img_block",
    advlink_styles: "internal (sehmaschine.net)=internal;external (link to an external site)=external",
    advimage_update_dimensions_onchange: true,
    file_browser_callback: "CustomFileBrowser",
    relative_urls: false,
    valid_elements : "" +
    "-p," + 
    "a[href|target=_blank|class]," +
    "-strong/-b," +
    "-em/-i," +
    "-u," + 
    "-ol," + 
    "-ul," + 
    "-li," + 
    "br," + 
    "img[class|src|alt=|width|height]," + 
    "-h2,-h3,-h4," + 
    "-pre," +
    "-code," + 
    "-div",
    extended_valid_elements: "" + 
    "a[name|class|href|target|title|onclick]," + 
    "img[class|src|border=0|alt|title|hspace|vspace|width|height|align|onmouseover|onmouseout|name]," + 
    "br[clearfix]," + 
    "-p[class<clearfix?summary?code]," + 
    "h2[class<clearfix],h3[class<clearfix],h4[class<clearfix]," + 
    "ul[class<clearfix],ol[class<clearfix]," + 
    "div[class],"
});


