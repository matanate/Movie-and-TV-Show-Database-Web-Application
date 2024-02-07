// Get the search input element and search list container
const searchInputItem = document.querySelector('.search-input')
const searchListItem = document.querySelector('.search-list')

// Function to toggle and update the search list based on user input
function toggleSearchList(searchInput) {
  // Clear the existing content in the search list
  searchListItem.innerHTML = ''

  // Get the origin URL of the current location
  const originUrl = document.location.origin

  // Check if there is valid search input
  if (searchInput) {
    // Fetch search results based on user input
    fetch('/search-result/?search-input=' + searchInput)
      .then(response => response.json())
      .then(searchResultsObject => {
        // Iterate through search results and create list items
        for (const [titleId, { title, img_url, movie_or_tv }] of Object.entries(
          searchResultsObject,
        )) {
          // Create a new anchor element for each search result
          const listItem = document.createElement('a')

          // Assign attributes to the list item
          Object.assign(listItem, {
            type: 'button',
            className: 'list-group-item list-group-item-action',
            href: `${originUrl}/titles/${movie_or_tv}/${titleId}`,
          })
          // Set the HTML content of the list item
          listItem.innerHTML = `
            <div style="background-image: url('${img_url}')" class="list-group-item-img">
              ${titleCase(movie_or_tv)}
            </div>
            ${title}
          `

          // Append the list item to the search list container
          searchListItem.append(listItem)
        }

        // If no search results, display a message
        if (!searchListItem.innerHTML) {
          listItem = document.createElement('label')
          Object.assign(listItem, {
            type: 'label',
            className: 'list-group-item',
          })
          listItem.innerHTML = 'No results found'
          searchListItem.append(listItem)
        }
      })
      .catch(error => console.error('Error:', error))
  }
}

// Function to convert a string to title case
function titleCase(str) {
  return str.toLowerCase().replace(/(?:^|\s)\w/g, match => match.toUpperCase())
}
