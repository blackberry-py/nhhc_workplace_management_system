
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


// display first 10
// function displayRange(a, b) {
//   hideAll();
//   // display 0 - 1 students
//   $submissions.slice(a, b).fadeIn();
// }

// displayRange(0, itemTotal);

// create pagination links
// let pagination = '';
// for (var i = 0; i <= $submissions.length / 10 - 1; i++) {
//   const listItemStyleWrapper = document.createElement('li')
//   listItemStyleWrapper.classList.add("page-item")
//   const listItemPage = document.createElement("a")
//   listItemPage.innerHTML = i
//   listItemPage.classList.add("page-link")
// //   pagination += `
// //     <li><span class ="page-link">${i}</span></li>
// // `;
//   $paginationList.appendChild(listItemPage);
// }

// click on pagination num,
// pass into display range
// calc and show range
// $('body').on('click', '.page-link', function () {

//   hideAll();

//   // get text number 1 - 5
//   // get ranges for start and end
//   let paginationText = Number($(this).text());
//   let startFrom = paginationText * itemTotal + paginationText;
//   let end = paginationText * itemTotal + paginationText + itemTotal;

//   // display ranges
//   displayRange(startFrom, end);

// });
// $submissionSearch.addEventListener('keyup', function () {
//   hideAll();
//   $submissions.each(() => {
//     $(this).removeClass("result");
//   });


  // // value of searched
  // var text = $(this).val().toLowerCase();
  // // results of search
  // var results = $("tr.client-submission td:contains('" + text.toLowerCase() + "')");

  // results.addClass("result");


  // if student has result class
  // dispaly
  // else hide

  // if ($submissions.hasClass('result')) {
  //   $('.result').show();
  //   $submissions.removeClass('result');

  // }

// });

// $submissionSearch.addEventListener('keyup', function () {
//   if (!this.value) {
//     hideAll();
//     displayRange(0, itemTotal);
//   }

// });

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




// function search_entires() {
//   let input = document.getElementById('searchbar').value
//   input = input.toLowerCase();
//   let x = document.getElementsByClassName('client-submission');

//   for (i = 0; i < x.length; i++) {
//     if (!x[i].innerHTML.toLowerCase().includes(input)) {
//       x[i].style.display = "none";
//     }

//   }
// }
// document.getElementById('searchbar').addEventListener('input', search_entires)
// document.getElementById('searchbar').addEventListener('change', search_entires)
// document.getElementById('searchbar').addEventListener('keyup', search_entires)
// document.getElementById('searchbar').addEventListener('keydown', search_entires)
// document.getElementById('searchbar').addEventListener('focus', search_entires)
// document.getElementById('searchbar').addEventListener('blur', search_entires)



// !SECTION

// SECTION - JQUERY AJAX Post Request to update
function ntfy(message) {
  alert(message)
  console.info('Getting Ready to Reload Page')
  reloadPage()
};
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

function hireApplicant(pk) {
  let data = {
    "pk": pk
  }
  data = JSON.stringify(data)
  $.ajax({
    url: '/hired',
    data: data,
    type: 'POST',
    success: ntfy("Applicant Hired - Email and Username Have Been Emailed")
  }
  )
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

