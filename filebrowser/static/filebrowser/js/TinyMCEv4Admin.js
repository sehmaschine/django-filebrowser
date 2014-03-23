tinyMCE.init({

    // see http://www.tinymce.com/wiki.php
    //
    // docs/fieldswidgets.rst - Using the FileBrowseField with TinyMCE
    // class Media:
    //     js = ['/path/to/your/tinymce/tinymce.min.js',
    //           '/path/to/your/tinymce_setup.js']

    selector:'textarea',
    plugins: [
        "hr link image charmap paste print preview anchor pagebreak spellchecker searchreplace visualblocks visualchars code fullscreen",
        "insertdatetime media nonbreaking save table emoticons template textcolor",
    ],
    toolbar1: "undo removeformat blockquote redo subscript superscript | cut copy paste | bold italic underline strikethrough | alignleft aligncenter alignright alignjustify",
    toolbar2: "bullist numlist outdent indent | link image media | print preview | forecolor backcolor emoticons ",
    image_advtab: true,
    skin : 'lightgray',

    file_browser_callback: function(input_id, input_value, type, win){
        var cmsURL = '/admin/filebrowser/browse/?pop=4';
        cmsURL = cmsURL + '&type=' + type;

        tinymce.activeEditor.windowManager.open({
            file: cmsURL,
            width: 800,  // Your dimensions may differ - toy around with them!
            height: 500,
            resizable: 'yes',
            scrollbars: 'yes',
            inline: 'yes',  // This parameter only has an effect if you use the inlinepopups plugin!
            close_previous: 'no'
        }, {
            window: win,
            input: input_id,
        });
        return false;
    },
});
