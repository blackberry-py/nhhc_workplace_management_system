// SECTION - Profile Editabiity Toggle

const editProfileButton = document.getElementById("edit-button")
const cancelChangesButton = document.getElementById("reset-id-cancel")
const saveChangeButton = document.getElementById("submit-id-save")

function makeProfileEditable() {
  const editableFields = document.querySelectorAll('.editable')
  editableFields.forEach((field) => {
    field.removeAttribute('readonly')
  })
  saveChangeButton.removeAttribute('hidden')
  cancelChangesButton.removeAttribute('hidden')
  editProfileButton.hidden = true
}

function cancelPendingEdits() {
  window.location.reload();
}

function makeProfileUnEditable() {
  const editableFields = document.querySelectorAll('.editable')
  console.log('Called')
  editableFields.forEach((field) => {
    console.log(field)
    field.disabled = true
    console.log(`${field} is disabled`)
  })
  cancelChangesButton.hidden = true
  saveChangeButton.hidden = true
}

cancelChangesButton.addEventListener('click', cancelPendingEdits)
editProfileButton.addEventListener('click', makeProfileEditable)
window.addEventListener('load', makeProfileUnEditable)
