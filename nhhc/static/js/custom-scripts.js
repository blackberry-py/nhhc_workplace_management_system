
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

function hireApplicant(pk) {
  let data = {
    "pk": pk
  }
  console.log(`Hiring Applicant with primary key ${pk}`);

  var request = $.post('/hired', data).done((response) => {
    if (response.success){
    console.log(response)
      swal('SUCCESS!', response, 'success').then(() => {
        window.location.reload();
      })
    } else {
      console.error(`Done Response: ${response}`)
      swal('ERROR: Applicant Not Hired', `Applicant Rejected: ${response.message}`, 'error');
    }
  })
    .fail((xhr, status, error) => {
      console.error(response)
      swal("Error: Applicant Not Hired", `Error Hiring Applicant:\n${error}\n \nStatus Code: ${status}`, "error");
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

