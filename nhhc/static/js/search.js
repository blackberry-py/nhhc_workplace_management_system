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


$submissionSearch.addEventListener('keyup', function () {
    if (!this.value) {
        hideAll();
        displayRange(0, itemTotal);
    }
});

// value of searched
var text = $(this).val().toLowerCase();
// results of search
var results = $("tr.client-submission td:contains('" + text.toLowerCase() + "')");

results.addClass("result");

if ($submissions.hasClass('result')) {
    $('.result').show();
    $submissions.removeClass('result');

}
function search_entires() {
    let input = document.getElementById('searchbar').value
    input = input.toLowerCase();
    let x = document.getElementsByClassName('client-submission');

    for (i = 0; i < x.length; i++) {
        if (!x[i].innerHTML.toLowerCase().includes(input)) {
            x[i].style.display = "none";
        }

    }
}
document.getElementById('searchbar').addEventListener('input', search_entires)
document.getElementById('searchbar').addEventListener('change', search_entires)
document.getElementById('searchbar').addEventListener('keyup', search_entires)
document.getElementById('searchbar').addEventListener('keydown', search_entires)
document.getElementById('searchbar').addEventListener('focus', search_entires)
document.getElementById('searchbar').addEventListener('blur', search_entires)
console.log('Profile Serarch JS Loaded')
