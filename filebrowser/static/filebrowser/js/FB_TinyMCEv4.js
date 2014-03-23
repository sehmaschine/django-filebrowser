var FileBrowserDialogue = {
    fileSubmit : function (FileURL) {
        parentWin = (!window.frameElement && window.dialogArguments) || opener || parent || top;
        tinymce = tinyMCE = parentWin.tinymce;
        self.editor = tinymce.EditorManager.activeEditor;
        self.params = self.editor.windowManager.getParams();
        parentWin.document.getElementById(self.params.input).value = FileURL;
        self.editor.windowManager.close(parentWin);
    },
}
