/*  ---------------------------------------------------
    Template Name: Dreams
    Description: Dreams wedding template
    Author: Colorib
    Author URI: https://colorlib.com/
    Version: 1.0
    Created: Colorib
---------------------------------------------------------  */

'use strict';


// Preloader Logic


  
(function ($) {

    /*------------------
        Preloader
    --------------------*/
    document.addEventListener("DOMContentLoaded", () => {
        // Simulate an API request or any async operation
        setTimeout(() => {
            hideLoader();
            showContent();
        }, 3000); // Replace with your actual data loading logic and time
      
        function hideLoader() {
            $("#loader-3").fadeOut(1800)
        }
      
        function showContent() {
            $("#body-hide").fadeIn(1600)
        }
      });

    //   function dismissLoadSpinner(){
    //     document.getElementById('load-cover').style.display = "none";
    //     document.getElementById('body-hide').style.display = "block";
    //   }
        /*------------------
            Portfolio filter
        --------------------*/
        $('.portfolio__filter li').on('click', function () {
            $('.portfolio__filter li').removeClass('active');
            $(this).addClass('active');
        });
        if ($('.portfolio__gallery').length > 0) {
            var containerEl = document.querySelector('.portfolio__gallery');
            var mixer = mixitup(containerEl);
        }
    });

    /*------------------
        Background Set
    -------*/
    $('.set-bg').each(function () {
        var bg = $(this).data('setbg');
        $(this).css('background-image', 'url(' + bg + ')');
    });

    //Masonary
    $('.work__gallery').masonry({
        itemSelector: '.work__item',
        columnWidth: '.grid-sizer',
        gutter: 10
    });

    /*------------------
		Navigation
	--------------------*/
    $(".mobile-menu").slicknav({
        prependTo: '#mobile-menu-wrap',
        allowParentLinks: true
    });

    /*------------------
		Hero Slider
	--------------------*/
    if ($('.hero_slider')){
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

    var dot = $('.hero__slider .owl-dot');
    dot.each(function () {
        var index = $(this).index() + 1;
        if (index < 10) {
            $(this).html('0').append(index);
        } else {
            $(this).html(index);
        }
    });

    /*------------------
        Testimonial Slider
    --------------------*/
    $(".testimonial__slider").owlCarousel({
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
                items: 3
            },
            768: {
                items: 2
            },
            320: {
                items: 1
            }
        }
    });

    /*------------------
        Latest Slider
    --------------------*/
    $(".latest__slider").owlCarousel({
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
                items: 3
            },
            768: {
                items: 2
            },
            320: {
                items: 1
            }
        }
    });

    /*------------------
        Logo Slider
    --------------------*/
    $(".logo__carousel").owlCarousel({
        loop: true,
        margin: 100,
        items: 6,
        dots: false,
        smartSpeed: 1200,
        autoHeight: false,
        autoplay: true,
        responsive: {
            992: {
                items: 5
            },
            768: {
                items: 4
            },
            480: {
                items: 3
            },
            320: {
                items: 2
            }
        }
    });

    /*------------------
        Video Popup
    --------------------*/
    $('.video-popup').magnificPopup({
        type: 'iframe'
    });

    /*------------------
        Counter
    --------------------*/
    $('.counter_num').each(function () {
        $(this).prop('Counter', 0).animate({
            Counter: $(this).text()
        }, {
            duration: 4000,
            easing: 'swing',
            step: function (now) {
                $(this).text(Math.ceil(now));
            }
        });
    })(jQuery);



// SECTIION - Client Submission Filtering & Pagination
const $submissions = $(".client-submission")
const $page = document.querySelector('.page');
const $pagination = document.querySelector('.pagination');
const $paginationList = document.querySelector('.pagination__list');
const $submissionSearch = document.getElementById('searchbar');
const itemTotal = 10;

// hide all
function hideAll() {
  $submissions.each((field) => {
    field.hidden = true
  })
}
function togglePaginationNavigtationVisibility() {
  var paginationNavigation = document.getElementById("pagination-navigation")
  if (paginationNavigation.style.display === "none") {
    paginationNavigation.style.display = "block";
  } else {
    paginationNavigation.style.display = "none";
  }
}
if ($submissionSearch) {
  $submissionSearch.addEventListener('input', togglePaginationNavigtationVisibility)
}


$(document).ready(function () {
  const tabs = $('.tab').click(function () {
    if (this.id == 'all') {
      $('.client-submission').fadeIn(450);
    } else {
      this.classList.add('active');
      tabs.not(this).removeClass('active');
      const el = $('.' + this.id).fadeIn(450);
      $('.client-submission').not(el).hide();
    }
  });
});
if ($submissionSearch) {
  var options = {
    valueNames: ['first-name', 'last-name', 'desired-service', 'phone']
  };
  var submissionList = new List('list-looker', options)
}



// SECTION - JQUERY AJAX Post Request to update
function reloadPage() {
  document.location.reload()
  setTimeout(document.location.reload(), 3000)

}



function SuccessfulUpdate() {
  notifications.snackbar('Submission Marked as Reviewed');
}

function markSubmissionAsReviewed(pk) {
  let data = {
    "pk": pk
  }
  data = JSON.stringify(data)
  $.ajax({
    url: '/reviewed',
    data: data,
    type: 'POST',
    success: ntfy("Submission Marked as Reviewed")
  });
};



function rejectApplicant(pk) {
  let data = {
    "pk": pk
  }
  console.log(`Hiring Applicant with primary key ${pk}`);

  var request = $.post('/rejected', data).done((response) => {
    if (response.success) {
      console.log(response)
      swal('SUCCESS!', response, 'success').then(() => {
        window.location.reload();
      })
    } else {
      console.error(`Done Response: ${response}`)
      swal('ERROR: Applicant Not Rejected', `Applicant Not Rejected: ${response.message}`, 'error');
    }
  })
    .fail((xhr, status, error) => {
      console.error(response)
      swal("Error: Applicant Not Rejected", `Error Rejecting Applicant:\n${error}\n \nStatus Code: ${status}`, "error");
    });
};


function rejectApplicant(pk) {
  let data = {
    "pk": pk
  }
  data = JSON.stringify(data)
  $.ajax({
    url: '/rejected',
    data: data,
    type: 'POST',
    success: ntfy('Application Rejected')
  });
};





function postAnnouncement(title, message, message_type) {
  let data = {
    "title": title,
    "message": message,
    "message_type": message_type
  }
  data = JSON.stringify(data)
  $.ajax({
    url: '/create-announcement-draft',
    data: data,
    type: 'POST',
    success: ntfy("Draft Created")
  }
  )
};
// !SECTION

// SECTION - Dangerous Action Confirmation Notifications

function confirmTermination(pk) {
  let sentData = {
    "pk": pk
  }
  console.log(`Sending Termination Request with Employee ID ${pk}`);

  Swal.fire({
    title: "Confirm Termination",
    html:"<p>You are about to terminate employment for this employee.\n It will lock them out of their account and archive their compliance profile.</p> <p><strong>Note: </strong>Archived profiles will still have the documents available, but cannot be modified.</p>  <br/> <p><strong>Please type \"terminate\" to confirm employment termination</strong></p> ",
    showCancelButton: true,
    icon: "warning",
    input: "text",
    confirmButtonText: "Terminate",
    showLoaderOnConfirm: true,
    preConfirm: (input) => {
      if (input === "terminate"){
        try {
          var request = $.post("/terminate", sentData, (data, status) => {
            Swal.fire({
              title: "Employment Terminated!",
              icon: "success" ,
              text: `Employee Terminated. They have been notified via email.`,
              didClose: () => { window.location.reload() }
            });
          })
        } catch (error) {
          Swal.showValidationMessage(`Request failed: ${error}`);
        }
      } else {
        Swal.showValidationMessage('Please type "terminate" exactly to confirm')
      }},
    allowOutsideClick: () => !Swal.isLoading(),
  })
}



function confirmHire(pk) {
  let sentData = {
    "pk": pk
  }
  console.log(`Hiring Applicant with primary key ${pk}`);

  Swal.fire({
    title: "Confirm Hire",
    html:"You are about to start employment and create and employment profile.",
    showCancelButton: true,
    icon: "warning",
    confirmButtonText: "Hire",
    showLoaderOnConfirm: true,
    preConfirm: () => {
      try {
        var request = $.post("/hired", sentData, (data, status) => {
          Swal.fire({
            title: "Success!",
            icon: "success" ,
            html: `<h1>Employee Hired.</h1>\n ${data}`,
            didClose: () => { window.location.href(`/employee/${data.employee_id}`) }
          });
        })
      } catch (error) {
        Swal.showValidationMessage(`Request failed: ${error}`);
      }
    },
    allowOutsideClick: () => !Swal.isLoading(),
  })
}

function confirmRejection(pk) {
  let sentData = {
    "pk": pk
  }
  console.log(`Rejecting Applicant with primary key ${pk}`);

  Swal.fire({
    title: "Confirm Rejection",
    text:"You are about to reject this applicant. This will send a email of notifying the applicant",
    showCancelButton: true,
    icon: "warning",
    confirmButtonText: "Reject",
    showLoaderOnConfirm: true,
    preConfirm: () => {
      try {
        var request = $.post("/rejected", sentData, (data, status) => {
          Swal.fire({
            title: "Applicant Rejected",
            icon: "info" ,
            text: `Applicant rejected. \n They have been  notified by email`,
            didClose: () => { window.location.reload() }
          });
        })
      } catch (error) {
        Swal.showValidationMessage(`Request failed: ${error}`);
      }
    },
    allowOutsideClick: () => !Swal.isLoading(),
  })
}

function  confirmAnnouncementDraft(title, message, message_type) {
    let announcementDraftData = {
      "title": title,
      "message": message,
      "message_type": message_type
    }
    console.log(`Attempting to Save Draft`);
    Swal.fire({
        title: "Confirm Draft Creation",
        text:"Confirm you wish to save this annoucement as a draft. It will not be seen by until it has been posted",
        showCancelButton: true,
        icon: "warning",
        confirmButtonText: "Save Draft",
        showLoaderOnConfirm: true,
        preConfirm: () => {
            try{
            $.post('/create-announcement-draft', announcementDraftData, (data, status) => {
                Swal.fire({
                    title: "Announcement Saved!",
                    icon: "info" ,
                    text: `Announcement has been saved. It can be found in the draft tab of the announcements page`,
                    didClose: () => { window.location.reload() }
                })
            })} catch (error) {
                Swal.showValidationMessage(`
                Request failed: ${error}
              `);
            }
            },   allowOutsideClick: () => !Swal.isLoading()
        }

    )


        }})
/*
    data = JSON.stringify(data)
    $.ajax({
      url: '/create-announcement-draft',
      data: data,
      type: 'POST',
      success: ntfy("Draft Created")
    }
    ) */
  };

console.log('Main JS')
