
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

function removeError(node) {
    document.getElementById('error').removeChild(node.parentNode.parentNode);
}

function flashError(error_list) {
    if (!error_list || error_list.length == 0) return;

    document.getElementById('error').innerHTML = `
    <div>
        <span class="fa-solid fa-triangle-exclamation"></span>
        <div class='error-messages'>
            ${
                error_list.map(function(error_message) {
                    return `<div class="error-message">${error_message}</div>`
                }).join('')
            }
        </div>
        <span><a class="fa-solid fa-xmark" onclick='removeError(this)'></a></span>
    </div>
    `
}

function flashFlashed() {
    flashed = get_flashed();
    console.log(flashed);
    flashError(flashed);
}

function ajaxErrorHandle(response) {
    console.log(response);
    flashError(response.data.error_description);
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

  function detectBrowser() { 
    if((navigator.userAgent.indexOf("Opera") || navigator.userAgent.indexOf('OPR')) != -1 ) {
        return 'Opera';
    } else if(navigator.userAgent.indexOf("Chrome") != -1 ) {
        return 'Chrome';
    } else if(navigator.userAgent.indexOf("Safari") != -1) {
        return 'Safari';
    } else if(navigator.userAgent.indexOf("Firefox") != -1 ){
        return 'Firefox';
    } else if((navigator.userAgent.indexOf("MSIE") != -1 ) || (!!document.documentMode == true )) {
        return 'IE';//crap
    } else {
        return 'Unknown';
    }
} 