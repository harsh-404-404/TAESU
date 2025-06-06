tinymce.init({
    selector: '#editor',
    license_key: 'gpl',
    height: 500,
    menubar: true,
    menu: {
        file: {
            title: 'File',
            items: 'preview | importword exportpdf exportword | print | deleteallconversations'
        },

    },
    plugins: [ // CORRECTED PLUGIN DECLARATION
        'advlist', 'autolink', 'lists', 'link', 'image',
        'charmap', 'preview', 'anchor', 'searchreplace',
        'visualblocks', 'code', 'fullscreen', 'insertdatetime',
        'media', 'table', 'help', 'wordcount' // Individual plugin names
    ],
    toolbar: 'undo redo | formatselect | ' +
        'bold italic underline strikethrough | forecolor backcolor | alignleft aligncenter ' +
        'alignright alignjustify | bullist numlist outdent indent | ' +
        'removeformat | link image media table code | ' +
        'tabledelete | tableprops tablerowprops tablecellprops | ' +
        'tableinsertrowbefore tableinsertrowafter tabledeleterow | ' +
        'tableinsertcolbefore tableinsertcolafter tabledeletecol',
    placeholder: "Write anything about your day....",
    skin: 'custom',
    content_style: "body { background-image: url('/static/paper1.jpg'); background-size: 600px 700px; font-size:14pt; font-family: 'courier new';color:white;} .mce-content-body[data-mce-placeholder]:not(.mce-visualblocks)::before  { color: rgb(255 255 255) !important; }"
});
