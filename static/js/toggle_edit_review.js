// Variables to store the original HTML content of review rating and comment and the submit button
let outerOriginalRating
let outerOriginalComment
let submitButton

// Function to toggle between displaying and editing a review
function toggleEditReview(reviewId) {
  // Get the elements for review rating, comment, and edit button
  let ratingElement = document.querySelector('#review-rating-' + reviewId)
  let commentTextElement = document.querySelector('#review-comment-' + reviewId)
  let editButton = document.querySelector('#edit-review-btn-' + reviewId)

  // Check if elements are found
  if (ratingElement && commentTextElement && editButton) {
    // Toggle between display and input fields
    if (editButton.checked) {
      // Display input fields for editing

      // Store the original HTML content of review rating and comment
      outerOriginalRating = ratingElement.outerHTML
      outerOriginalComment = commentTextElement.outerHTML

      // Get the inner HTML content of review rating and comment
      const innerOriginalRating = ratingElement.innerHTML
      const innerOriginalComment = commentTextElement.innerHTML.trim()

      // Create a new input element for review rating
      let newRatingElement = document.createElement('input')
      Object.assign(newRatingElement, {
        type: 'number',
        className: 'form-control review-rating',
        id: 'review-rating-' + reviewId,
        name: 'new-rating',
        min: '1',
        max: '10',
        step: '0.1',
        value: innerOriginalRating,
        required: true,
      })

      // Create a new textarea element for review comment
      let newCommentTextElement = document.createElement('textarea')
      Object.assign(newCommentTextElement, {
        className: 'form-control comment-text',
        id: 'review-comment-' + reviewId,
        name: 'new-comment-text',
        rows: '3',
        required: true,
      })
      newCommentTextElement.innerHTML = innerOriginalComment

      // Replace the original review rating and comment with the new input fields
      ratingElement.replaceWith(newRatingElement)
      commentTextElement.replaceWith(newCommentTextElement)

      // Create a new submit element
      submitButton = document.createElement('button')
      Object.assign(submitButton, {
        name: 'update-submit',
        type: 'submit',
        className: 'btn btn-primary',
        value: reviewId,
      })
      submitButton.innerHTML = 'Update Review'
      newCommentTextElement.parentNode.insertBefore(
        submitButton,
        newCommentTextElement.nextSibling,
      )
    } else {
      // Restore the original HTML content of review rating and comment
      ratingElement.outerHTML = outerOriginalRating
      commentTextElement.outerHTML = outerOriginalComment
      // Remove the submit button
      submitButton.remove()
    }
  }
}
