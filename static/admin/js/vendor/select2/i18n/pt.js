/*! Select2 4.0.13 | https://github.com/select2/select2/blob/master/LICENSE.md */

!function(){if (jQuery&&jQuery.fn&&jQuery.fn.select2&&jQuery.fn.select2.amd) {
              var e=jQuery.fn.select2.amd;
            }e.define("select2/i18n/pt",[],function(){return{errorLoading:function(){return"Os resultados não puderam ser carregados."},inputTooLong:function(e){var r=e.input.length-e.maximum,n="Por favor apague "+r+" ";return n+=r != 1?"caracteres":"caractere"},inputTooShort:function(e){return"Introduza "+(e.minimum-e.input.length)+" ou mais caracteres"},loadingMore:function(){return"A carregar mais resultados…"},maximumSelected:function(e){var r="Apenas pode seleccionar "+e.maximum+" ";return r+=e.maximum != 1?"itens":"item"},noResults:function(){return"Sem resultados"},searching:function(){return"A procurar…"},removeAllItems:function(){return"Remover todos os itens"}}}),e.define,e.require}();
