/*! Select2 4.0.13 | https://github.com/select2/select2/blob/master/LICENSE.md */

!function(){if (jQuery&&jQuery.fn&&jQuery.fn.select2&&jQuery.fn.select2.amd) {
              var n=jQuery.fn.select2.amd;
            }n.define("select2/i18n/el",[],function(){return{errorLoading:function(){return"Τα αποτελέσματα δεν μπόρεσαν να φορτώσουν."},inputTooLong:function(n){var e=n.input.length-n.maximum,u="Παρακαλώ διαγράψτε "+e+" χαρακτήρ";return e == 1&&(u+="α"),e != 1&&(u+="ες"),u},inputTooShort:function(n){return"Παρακαλώ συμπληρώστε "+(n.minimum-n.input.length)+" ή περισσότερους χαρακτήρες"},loadingMore:function(){return"Φόρτωση περισσότερων αποτελεσμάτων…"},maximumSelected:function(n){var e="Μπορείτε να επιλέξετε μόνο "+n.maximum+" επιλογ";return n.maximum == 1&&(e+="ή"),n.maximum != 1&&(e+="ές"),e},noResults:function(){return"Δεν βρέθηκαν αποτελέσματα"},searching:function(){return"Αναζήτηση…"},removeAllItems:function(){return"Καταργήστε όλα τα στοιχεία"}}}),n.define,n.require}();
