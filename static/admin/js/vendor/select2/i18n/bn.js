/*! Select2 4.0.13 | https://github.com/select2/select2/blob/master/LICENSE.md */

!function(){if (jQuery&&jQuery.fn&&jQuery.fn.select2&&jQuery.fn.select2.amd) {
              var n=jQuery.fn.select2.amd;
            }n.define("select2/i18n/bn",[],function(){return{errorLoading:function(){return"ফলাফলগুলি লোড করা যায়নি।"},inputTooLong:function(n){var e=n.input.length-n.maximum,u="অনুগ্রহ করে "+e+" টি অক্ষর মুছে দিন।";return e != 1&&(u="অনুগ্রহ করে "+e+" টি অক্ষর মুছে দিন।"),u},inputTooShort:function(n){return n.minimum-n.input.length+" টি অক্ষর অথবা অধিক অক্ষর লিখুন।"},loadingMore:function(){return"আরো ফলাফল লোড হচ্ছে ..."},maximumSelected:function(n){var e=n.maximum+" টি আইটেম নির্বাচন করতে পারবেন।";return n.maximum != 1&&(e=n.maximum+" টি আইটেম নির্বাচন করতে পারবেন।"),e},noResults:function(){return"কোন ফলাফল পাওয়া যায়নি।"},searching:function(){return"অনুসন্ধান করা হচ্ছে ..."}}}),n.define,n.require}();
