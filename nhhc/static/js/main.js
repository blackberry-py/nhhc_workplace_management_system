const script = document.createElement('script');
script.src = 'https://ajax.googleapis.com/ajax/libs/jquery/1.6.3/jquery.min.js';
document.getElementsByTagName('head')[0].appendChild(script);


console.log('Added JQuery');


(function ($) {
    /* -----------------
        Top Level Vars
    ------------------*/


    if ($('#searchbar')) {
        const options = {
            valueNames: ['first-name', 'last-name', 'desired-service', 'phone'],
        };
        const submissionList = new List('list-looker', options);
    }
    /* ------------------
          Preloader
      --------------------*/
    document.addEventListener('DOMContentLoaded', () => {
        setTimeout(() => {
            hideLoader();
            showContent();
        }, 3000);

        function hideLoader() {
            $('#loader-3').fadeOut(1800);
        }

        function showContent() {
            $('#body-hide').fadeIn(1600);
        }
    });

    /* ------------------
              Portfolio filter
          --------------------*/
    $('.portfolio__filter li').on('click', function () {
        $('.portfolio__filter li').removeClass('active');
        $(this).addClass('active');
    });
    if ($('.portfolio__gallery').length > 0) {
        const containerEl = document.querySelector('.portfolio__gallery');
        const mixer = mixitup(containerEl);
    }

    /* ------------------
          Background Set
      -------*/
    $('.set-bg').each(function () {
        const bg = $(this).data('setbg');
        $(this).css('background-image', 'url(' + bg + ')');
    });

    // Masonary
    $('.work__gallery').masonry({
        itemSelector: '.work__item',
        columnWidth: '.grid-sizer',
        gutter: 10,
    });

    /* ------------------
Hero Slider
--------------------*/
    if ($('.hero_slider')) {
        $('.hero__slider').owlCarousel({
            loop: true,
            dots: true,
            mouseDrag: false,
            animateOut: 'fadeOut',
            animateIn: 'fadeIn',
            items: 1,
            margin: 0,
            smartSpeed: 1200,
            autoHeight: false,
            autoplay: true,
        });
    }

    const dot = $('.hero__slider .owl-dot');
    dot.each(function () {
        const index = $(this).index() + 1;
        if (index < 10) {
            $(this).html('0').append(index);
        } else {
            $(this).html(index);
        }
    });

    /* ------------------
          Testimonial Slider
      --------------------*/
    $('.testimonial__slider').owlCarousel({
        loop: true,
        margin: 0,
        items: 3,
        dots: true,
        dotsEach: 2,
        smartSpeed: 1200,
        autoHeight: false,
        autoplay: true,
        responsive: {
            992: {
                items: 3,
            },
            768: {
                items: 2,
            },
            320: {
                items: 1,
            },
        },
    });

    /* ------------------
          Latest Slider
      --------------------*/
    $('.latest__slider').owlCarousel({
        loop: true,
        margin: 0,
        items: 3,
        dots: true,
        dotsEach: 2,
        smartSpeed: 1200,
        autoHeight: false,
        autoplay: true,
        responsive: {
            992: {
                items: 3,
            },
            768: {
                items: 2,
            },
            320: {
                items: 1,
            },
        },
    });

    /* ------------------
          Logo Slider
      --------------------*/
    $('.logo__carousel').owlCarousel({
        loop: true,
        margin: 100,
        items: 6,
        dots: false,
        smartSpeed: 1200,
        autoHeight: false,
        autoplay: true,
        responsive: {
            992: {
                items: 5,
            },
            768: {
                items: 4,
            },
            480: {
                items: 3,
            },
            320: {
                items: 2,
            },
        },
    });

    /*------------------
            Counter
        --------------------*/
    $(".counter_num").each(function () {
        $(this)
            .prop("Counter", 0)
            .animate({
                Counter: $(this).text(),
            }, {
                duration: 4000,
                easing: "swing",
                step: function (now) {
                    $(this).text(Math.ceil(now));
                },
            });
    })

// const tabs = document.querySelectorAll('.tab')
// const allArray = Array.from(all)

// tabs.forEach(tab => {
//   tab.addEventListener('click', () => {
//     tabs.forEach(tab => tab.classList.remove('active'))
//     tab.classList.add('active')

//     const tabId = tab.id

//     allArray.forEach(div => {
//       div.classList.remove('show', 'remove')

//       if (tabId === 'all') {
//         div.classList.add('show')
//       } else if (tabId === 'draft' &&!div.classList.contains('draft')) {
//         div.classList.add('remove')
//       } else if (tabId === 'active' &&!div.classList.contains('active')) {
//         div.classList.add('remove')
//       } else if (tabId === 'deleted' &&!div.classList.contains('deleted')) {
//         div.classList.add('remove')
//       }
//     })
//   })
// })

}(jQuery));;



// SECTION - JQUERY AJAX Post Request to update
var reloadPage = function () {
    document.location.reload();
    setTimeout(document.location.reload(), 3000);
}

$(document).ready(function () {
    function ntfy(title, message, type) {
        $.toast({
            title: title,
            messge: message,
            type: type,
            duration: 7000
        })
    }
})


$(document).ready(function () {
    function markSubmissionAsReviewed(pk) {
        let data = {
            pk: pk,
        };
        data = JSON.stringify(data);
        $.ajax({
            url: "/reviewed",
            data: data,
            type: "POST",
            success: ntfy(title = "Client Interest Updated", message = "Submission Marked as Reviewed", type = "success")
        })
    }
});

// function rejectApplicant(pk) {
//     let data = {
//         pk: pk,
//     };
//     console.log(`Hiring Applicant with primary key ${pk}`);

//     var request = $.post("/applicant/reject/", data)
//         .done((response) => {
//             if (response.success) {
//                 console.log(response);
//                 swal("SUCCESS!", response, "success").then(() => {
//                     window.location.reload();
//                 });
//             } else {
//                 console.error(`Done Response: ${response}`);
//                 swal(
//                     "ERROR: Applicant Not Rejected",
//                     `Applicant Not Rejected: ${response.message}`,
//                     "error"
//                 );
//             }
//         })
//         .fail((xhr, status, error) => {
//             console.error(response);
//             swal(
//                 "Error: Applicant Not Rejected",
//                 `Error Rejecting Applicant:\n${error}\n \nStatus Code: ${status}`,
//                 "error"
//             );
//         });
// }
// (function ($) {

    // function confirmSaveAsADraft(title, message, message_type) {
    //     let data = {
    //         csrfmiddlewaretoken: $('input[name=csrfmiddlewaretoken]').val(),
    //         title: title,
    //         message: message,
    //         message_type: message_type,
    //     };
    //     data = JSON.stringify(data);
    //     Swal.fire({
    //         title: "Confirm Save as A Draft",
    //         html: '<p>You are about to save this annoucement as <strong>Draft</strong>.\n It will <strong>Not Be Seen</strong> by anyone who is not a CareNett Admin User. </p> ',
    //         showCancelButton: true,
    //         icon: "warning",
    //         input: "text",
    //         confirmButtonText: "Save Draft",
    //         showLoaderOnConfirm: true,
    //         preConfirm: (input) => {
    //             try {
    //                 $.ajax({
    //                     url: "/create-announcement-draft",
    //                     data: data,
    //                     type: "POST",
    //                     success: ntfy(title = "Saved!", message = "New Announcement Draft Saved", type = "success"),
    //                 });
    //             } catch (error) {
    //                 Swal.showValidationMessage(`Request failed: ${error}`);

    //             }


    //         }, allowOutsideClick: () => !Swal.isLoading(),

    //     })
    // }

        // function postAnnouncement(title, message, message_type) {
        //     let data = {
        //         csrfmiddlewaretoken: $('input[name=csrfmiddlewaretoken]').val(),
        //         title: title,
        //         message: message,
        //         message_type: message_type,
        //     };
        //     data = JSON.stringify(data);
        //     $.ajax({
        //         url: "/create-announcement-draft",
        //         data: data,
        //         type: "POST",
        //         success: ntfy("Draft Created"),
        //     });
        // }
        // !SECTION

        /*-------------------------
        // SECTION - Modal Ajax Notification - Sweet Alert2 Library

        -----------------------------*/

        // function confirmTermination(pk) {
        //     let sentData = {
        //         csrfmiddlewaretoken: $('input[name=csrfmiddlewaretoken]').val(),
        //         pk: pk,
        //     };
        //     console.log(`Sending Termination Request with Employee ID ${pk}`);

        //     Swal.fire({
        //         title: "Confirm Termination",
        //         html: '<p>You are about to terminate employment for this employee.\n It will lock them out of their account and archive their compliance profile.</p> <p><strong>Note: </strong>Archived profiles will still have the documents available, but cannot be modified.</p>  <br/> <p><strong>Please type "terminate" to confirm employment termination</strong></p> ',
        //         showCancelButton: true,
        //         icon: "warning",
        //         input: "text",
        //         confirmButtonText: "Terminate",
        //         showLoaderOnConfirm: true,
        //         preConfirm: (input) => {
        //             if (input === "terminate") {
        //                 try {
        //                     var request = $.post("/employee/terminate/", sentData, (data, status) => {
        //                         Swal.fire({
        //                             title: "Employment Terminated!",
        //                             icon: "success",
        //                             text: `Employee Terminated. They have been notified via email.`,
        //                             didClose: () => {
        //                                 window.location.reload();
        //                             },
        //                         });
        //                     });
        //                 } catch (error) {
        //                     Swal.showValidationMessage(`Request failed: ${error}`);
        //                 }
        //             } else {
        //                 Swal.showValidationMessage(
        //                     'Please type "terminate" exactly to confirm'
        //                 );
        //             }
        //         },
        //         allowOutsideClick: () => !Swal.isLoading(),
        //     });
        // }

        // function confirmHire(pk) {
        //     let sentData = {
        //         csrfmiddlewaretoken: $('input[name=csrfmiddlewaretoken]').val(),
        //         pk: pk,
        //     };
        //     console.log(`Hiring Applicant with primary key ${pk}`);

        //     Swal.fire({
        //         title: "Confirm Hire",
        //         html: "You are about to start employment and create and employment profile.",
        //         showCancelButton: true,
        //         icon: "warning",
        //         confirmButtonText: "Hire",
        //         showLoaderOnConfirm: true,
        //         preConfirm: () => {
        //             try {
        //                 var request = $.post("/applicant/hire/", sentData, (data, status) => {
        //                     Swal.fire({
        //                         title: "Success!",
        //                         icon: "success",
        //                         html: `<h1>Employee Hired.</h1>\n ${data}`,
        //                         didClose: () => {
        //                             window.location.href(`/employee/${data.employee_id}`);
        //                         },
        //                     });
        //                 });
        //             } catch (error) {
        //                 Swal.showValidationMessage(`Request failed: ${error}`);
        //             }
        //         },
        //         allowOutsideClick: () => !Swal.isLoading(),
        //     });
        // }

        // function confirmRejection(pk) {
        //     let sentData = {
        //         csrfmiddlewaretoken: $('input[name=csrfmiddlewaretoken]').val(),
        //         pk: pk,
        //     };
        //     console.log(`Rejecting Applicant with primary key ${pk}`);

        //     Swal.fire({
        //         title: "Confirm Rejection",
        //         text: "You are about to reject this applicant. This will send a email of notifying the applicant",
        //         showCancelButton: true,
        //         icon: "warning",
        //         confirmButtonText: "Reject",
        //         showLoaderOnConfirm: true,
        //         preConfirm: () => {
        //             try {
        //                 var request = $.post("/applicant/reject/", sentData, (data, status) => {
        //                     Swal.fire({
        //                         title: "Applicant Rejected",
        //                         icon: "info",
        //                         text: `Applicant rejected. \n They have been  notified by email`,
        //                         didClose: () => {
        //                             window.location.reload();
        //                         },
        //                     });
        //                 });
        //             } catch (error) {
        //                 Swal.showValidationMessage(`Request failed: ${error}`);
        //             }
        //         },
        //         allowOutsideClick: () => !Swal.isLoading(),
        //     });
        // }

        /*-----------------------
             Form Auto Copy Phone Number to SMS Contact
             _______________________*/


    // } (jQuery));;
    console.log("Main JS");
