function FileSubmit(FilePath, FileURL, FileType) {
    
    // var input_id=window.name.split("___").join(".");
    var input_id=window.name.replace(/____/g,'-').split("___").join(".");
    var preview_id = 'preview_' + input_id;
    var previewlink_id = 'previewlink_' + input_id;
    input = opener.document.getElementById(input_id);
    // set new value for input field
    input.value = FilePath;
    this.close();
}

