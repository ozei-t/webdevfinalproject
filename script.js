document.getElementById('search-form').addEventListener('submit', function(event) {
    event.preventDefault(); // Prevent default form submission
    
    const searchQuery = document.getElementById('search-input').value.trim(); 
    if (searchQuery === '') {
        alert('Enter an Artist\'s Name'); // Corrected the alert message
        return;
    }

    const accessToken = 'WgL88zDw74vN0BHApKBu4Mfoz_EObXEFHKgxUlfdIhUcgZFvp5Vi7RcL0hs8J3rL';
    
    const apiUrl = `https://api.genius.com/search?q=${encodeURIComponent(searchQuery)}`;

    fetch(apiUrl, {
        headers: {
            'Authorization': `Bearer ${accessToken}`
        }
    })
    .then(response => response.json())
    .then(data => {
        displaySearchResults(data.response.hits);
    })
    .catch(error => {
        console.error('Error fetching data:', error);
    });
});

function displaySearchResults(results) {
    const searchResultsDiv = document.getElementById('search-results');
    searchResultsDiv.innerHTML = ''; // Clear previous search results

    if (results.length === 0) {
        searchResultsDiv.textContent = 'No results'; // Corrected the text content
        return;
    }

    results.forEach(result => {
        const resultDiv = document.createElement('div');
        resultDiv.textContent = result.result.full_title;
        searchResultsDiv.appendChild(resultDiv);
    });
}
