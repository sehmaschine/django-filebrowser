/**
 * Function to post the selected file back to TinyMCE
 */
var FileBrowserDialogue = {
    fileSubmit : function (FileURL) {
        window.parent.postMessage({
            mceAction: 'FileSelected',
            content: FileURL
        }, window);
    }
}
