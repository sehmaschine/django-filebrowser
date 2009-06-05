
function ProtectPath(path)
{
    path = path.replace( /\\/g, '\\\\') ;
    path = path.replace( /'/g, '\\\'') ;
    return path ;
}

function OpenFile( fileUrl )
{
    window.top.opener.SetUrl( encodeURI( fileUrl ).replace( '#', '%23' ) ) ;
    window.top.close() ;
    window.top.opener.focus() ;
}

// Build the link to view the folder.
// var sLink = '<a href="#" onclick="OpenFile(\'' + ProtectPath( fileUrl ) + '\');return false;">' ;

/*
function OpenFileBrowser( url, width, height )
{
    // oEditor must be defined.

    var iLeft = ( oEditor.FCKConfig.ScreenWidth  - width ) / 2 ;
    var iTop  = ( oEditor.FCKConfig.ScreenHeight - height ) / 2 ;

    var sOptions = "toolbar=no,status=no,resizable=yes,dependent=yes,scrollbars=yes" ;
    sOptions += ",width=" + width ;
    sOptions += ",height=" + height ;
    sOptions += ",left=" + iLeft ;
    sOptions += ",top=" + iTop ;

    window.open( url, 'FCKBrowseWindow', sOptions ) ;
}
*/