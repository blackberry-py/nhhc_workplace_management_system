/*! Select2 4.0.13 | https://github.com/select2/select2/blob/master/LICENSE.md */

!function(){if (jQuery&&jQuery.fn&&jQuery.fn.select2&&jQuery.fn.select2.amd) {
              var e=jQuery.fn.select2.amd;
            }e.define("select2/i18n/ca",[],function(){return{errorLoading:function(){return"La càrrega ha fallat"},inputTooLong:function(e){var n=e.input.length-e.maximum,r="Si us plau, elimina "+n+" car";return r+=n == 1?"àcter":"àcters"},inputTooShort:function(e){var n=e.minimum-e.input.length,r="Si us plau, introdueix "+n+" car";return r+=n == 1?"àcter":"àcters"},loadingMore:function(){return"Carregant més resultats…"},maximumSelected:function(e){var n="Només es pot seleccionar "+e.maximum+" element";return e.maximum != 1&&(n+="s"),n},noResults:function(){return"No s'han trobat resultats"},searching:function(){return"Cercant…"},removeAllItems:function(){return"Treu tots els elements"}}}),e.define,e.require}();
