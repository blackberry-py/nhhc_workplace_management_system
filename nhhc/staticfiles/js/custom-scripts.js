
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
function ntfy(message) {
  var toast = new Toastify({
    text: message,
    duration: 3000,
    close: true,
    gravity: "top", // `top` or `bottom`
    position: "center", // `left`, `center` or `right`
    stopOnFocus: true, // Prevents dismissing of toast on hover
    style: {
      background: "linear-gradient(to right, #00b09b, #96c93d)",
    },
    callback: reloadPage(),
  })
  toast.showToast();
  console.info('Getting Ready to Reload Page')
};



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


function saveAnnouncementDraft(title, message, message_type) {
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

// SECTION - SNACKBAR Notification
/* Set the width of the sidebar to 250px and the left margin of the page content to 250px */

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
        var request = $.post("/z", sentData, (data, status) => {
          Swal.fire({
            title: "Success!",
            icon: "success" ,
            html: `<h1>Employee Hired.</h1>\n ${data}`,
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

function dismissLoadSpinner(){
  document.getElementById('load-cover').style.display = "none";
  document.getElementById('body-hide').style.display = "block";
}
