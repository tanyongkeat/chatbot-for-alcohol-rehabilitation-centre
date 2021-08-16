
function deb(string) {
    document.getElementById('debug').innerHTML = string;
}

function preventZoomOnInput() {
    var $objHead = $( 'head' );

    // define a function to disable zooming
    var zoomDisable = function() {
        $objHead.find( 'meta[name=viewport]' ).remove();
        $objHead.prepend( '<meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=0" />');
    };

    // ... and another to re-enable it
    var zoomEnable = function() {
        $objHead.find( 'meta[name=viewport]' ).remove();
        $objHead.prepend( '<meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=1" />');
    };

    // if the device is an iProduct, apply the fix whenever the users touches an input
    if( navigator.userAgent.length && /iPhone|iPad|iPod/i.test( navigator.userAgent ) ) {
        // define as many target fields as your like 
        $( "input, textarea" )
            .on( { 'touchstart' : function() { zoomDisable() } } )
            .on( { 'touchend' : function() { setTimeout( zoomEnable , 500 ) } } );
    }
}


function hideKeyboard() {
    //this set timeout needed for case when hideKeyborad
    //is called inside of 'onfocus' event handler
    setTimeout(function() {
  
      //creating temp field
      var field = document.createElement('input');
      field.setAttribute('type', 'text');
      //hiding temp field from peoples eyes
      //-webkit-user-modify is nessesary for Android 4.x
      field.setAttribute('style', 'position:absolute; top: 0px; opacity: 0; -webkit-user-modify: read-write-plaintext-only; left:0px;');
      document.body.appendChild(field);
  
      //adding onfocus event handler for out temp field
      field.onfocus = function(){
        //this timeout of 200ms is nessasary for Android 2.3.x
        setTimeout(function() {
  
          field.setAttribute('style', 'display:none;');
          setTimeout(function() {
            document.body.removeChild(field);
            document.body.focus();
          }, 14);
  
        }, 200);
      };
      //focusing it
      field.focus();
  
    }, 50);
  }