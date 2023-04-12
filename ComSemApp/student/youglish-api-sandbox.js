/*
This code is an implementation of the Youglish API that allows a user to search for a word and retrieve relevant YouTube videos containing the word. 
The code fetches video details from the YouTube API, displays the videos in a player, and allows the user to navigate through the videos.

Youglish API - Receives requests from the client and sends them to the Youglish API. It then returns the response to the client-side code.
YouTube API - A set of RESTful APIs that provides functionality to search for videos, retrieve video details, and play videos from youtube.
jQuery - A JavaScript library that simplifies DOM manipulation, event handling, and Ajax interactions.
Ajax - A technique used to make asynchronous HTTP requests from the client-side code to the server-side code. 

C:/Users/Jared/GonzagaCPSC/YouglishAPI_JQuery-AJAX/youglish-test.html
*/

$(document).ready(function() {

  // Define the URL for the Youglish proxy API and the query string
  
  //use this for node server
  const apiUrl = 'http://localhost:3000/youglish-proxy';
  //use this apiUrl if using Django
  //const apiUrl = '/youglish-proxy';

  const query = 'explaining'; //replace with searched for word

  // Initialize empty arrays and variables to hold video data
  let videos = [];
  let currentVideoIndex = 0;
  

  // Function to display the sentence with highlighting
  function displaySentence(sentence, query) {
    const highlightedSentence = sentence.replace(
      new RegExp(`\\b${query}\\b`, 'gi'),
      (match) => `<mark>${match}</mark>`
    );
    $('#sentence-container').html(highlightedSentence);
  }

  //Function displays the video at the specified index.
  async function displayVideo(videoIndex, sentences = 2) {
    if (videoIndex >= videos.length) {
      console.warn('No more available videos.');
      return;
    }
  
    const videoId = videos[videoIndex].vid;
    const startTime = videos[videoIndex].start;
    const sentenceDuration = videos[videoIndex].dur;
    const endTime = startTime + sentences * sentenceDuration;
  
    console.log('Extracted video ID:', videoId);
  
    const iframe = document.createElement('iframe');
    iframe.width = '480';
    iframe.height = '270';
    iframe.src = `https://www.youtube.com/embed/${videoId}?start=${startTime}&end=${endTime}&autoplay=1&enablejsapi=1`;
    iframe.allow = 'accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture';
  
    const videoContainer = document.getElementById('video-container');
    videoContainer.innerHTML = ''; // Clear the previous iframe
    videoContainer.appendChild(iframe);
  
    $('#video-index').text(videoIndex + 1);
    currentVideoIndex = videoIndex;
  
    displaySentence(videos[videoIndex].display, query);
  }

  function displayVideos(results) {
    videos = results;
    // Update the total number of videos displayed
    $('#total-videos').text(videos.length);
    displayVideo(currentVideoIndex);
  }
  
  // Set a click event for the 'Previous Video' button
  $('#prev-video').on('click', function() {
    if (currentVideoIndex > 0) {
      currentVideoIndex--;
      displayVideo(currentVideoIndex);
    }
  });
  
  // Set a click event for the 'Next Video' button
  $('#next-video').on('click', function() {
    if (currentVideoIndex < videos.length - 1) {
      currentVideoIndex++;
      displayVideo(currentVideoIndex);
    }
  });
  
  function getYouglishData() {
    // Make a GET request to the Youglish API to retrieve data
    $.ajax({
      url: apiUrl,
      type: 'GET',
      dataType: 'json',
      data: {
        'q': query,
        'max': 3,
      },
      success: function(response) {
        console.log(response);
        displayVideos(response.results);
      },
      error: function(jqXHR, textStatus, errorThrown) {
        console.error('Error:', textStatus, errorThrown);
      },
    });
  }
  
  // Retrieve Youglish data when the page loads
  getYouglishData();
});
