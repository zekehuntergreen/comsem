/*
This code is an implementation of the Youglish API that allows a user to search for a word and retrieve relevant YouTube videos containing the word. 
The code fetches video details from the YouTube API, displays the videos in a player, and allows the user to navigate through the videos.

Youglish API - Receives requests from the client and sends them to the Youglish API. It then returns the response to the client-side code.
YouTube API - A set of RESTful APIs that provides functionality to search for videos, retrieve video details, and play videos from youtube.
jQuery - A JavaScript library that simplifies DOM manipulation, event handling, and Ajax interactions.
Ajax - A technique used to make asynchronous HTTP requests from the client-side code to the server-side code. 
*/

$(document).ready(function() {

  // Define the URL for the Youglish proxy API and the query string
  const apiUrl = 'http://localhost:3000/youglish-proxy';
  const query = 'explaining'; //replace with searched for word

  const youtubeApiKey = 'AIzaSyDQoynj7T6sa77hqlheFTgIIuuGTb1dQng';

  // Initialize empty arrays and variables to hold video data
  let videos = [];
  let player;
  let currentVideoIndex = 0;
  
  // Function to fetch video details from the YouTube API
  function fetchVideoDetails(videoId, onSuccess, onFailure) {
    // Make an AJAX request to the YouTube API using jQuery
    $.ajax({
      url: 'https://www.googleapis.com/youtube/v3/videos',
      type: 'GET',
      dataType: 'json',
      data: {
        key: youtubeApiKey,
        id: videoId,
        part: 'snippet,contentDetails,statistics,status',
      },
      success: onSuccess,
      error: function (jqXHR, textStatus, errorThrown) {
        console.error('YouTube Data API request failed:', textStatus, errorThrown);
        console.error('Response:', jqXHR.responseText);
        console.error('Video id: ',videoId);
        if (onFailure) {
          onFailure(jqXHR, textStatus, errorThrown); // If the request fails, call the onFailure function (if provided)
        }
      },
    });
  }

  // Function to request additional Youglish data from the API
  function requestAdditionalYouglishData() {
    // Make an AJAX request to the Youglish proxy API using jQuery
    $.ajax({
      url: apiUrl,
      type: 'GET',
      dataType: 'json',
      data: {
        'q': query,
        'skip': videos.length, 
        'max': 3,
      },
      success: function (response) {
        console.log(response);
        // Add the new results to the existing videos array, slicing to the first 3
        videos = videos.concat(response.results.slice(0, 3));
        // Update the total number of videos in the UI
        $('#total-videos').text(videos.length);
        // Display the current video
        displayVideo(currentVideoIndex);
      },
      error: function (jqXHR, textStatus, errorThrown) {
        console.error('Error:', textStatus, errorThrown);
      },
    });
  }

  //Function displays the video at the specified index.
  function displayVideo(videoIndex) {
    if (videoIndex >= videos.length) {
      console.warn('No more available videos.');
      return;
    }

    // Get the video ID, start time, and end time of the video at the specified index
    const videoId = videos[videoIndex].vid;
    const startTime = videos[videoIndex].start;
    const endTime = videos[videoIndex].end;

    // Calculate the buffered start and end times (2 seconds before and after the specified times)
    const bufferedStartTime = parseInt(startTime) - 2;
    const bufferedEndTime = parseInt(endTime) + 2;

    console.log("Extracted video ID:", videoId);

    // Call the fetchVideoDetails function to get details about the video
    fetchVideoDetails(
      videoId,
      function (response) {
        // Check if the response contains any items and if the video is embeddable and public
        if (response.items.length > 0 && response.items[0].status.embeddable && response.items[0].status.privacyStatus === "public") {
          // If the player already exists, load the video
          if (player) {
            player.loadVideoById({ videoId: videoId, startSeconds: startTime, endSeconds: endTime });
          } else { // Otherwise, create a new player
            player = new YT.Player('video-container', {
              height: '270',
              width: '480',
              videoId: videoId,
              playerVars: {
                'autoplay': 1,
                'start': bufferedStartTime,
                'end': bufferedEndTime,
              },
              events: {
                'onStateChange': onPlayerStateChange,
              },
            });
          }
          // Update the video index and the current video index
          $('#video-index').text(videoIndex + 1);
          currentVideoIndex = videoIndex;
        } else {
          console.warn('Video is not available:', videoId);
          // If the video is not available, skip it and try the next one
          displayVideo(videoIndex + 1);
        }
      },
      function (jqXHR, textStatus, errorThrown) {
        console.error('Error fetching video details:', textStatus, errorThrown);
      }
    );
  }

  
  /**
  * This function handles changes to the state of the YouTube player.
  * It seeks to the start time of the current video when the player starts playing,
  * and reloads the video or moves to the next one when it ends.
  */
  function onPlayerStateChange(event) {
    const startTime = videos[currentVideoIndex].start;
    const endTime = videos[currentVideoIndex].end;

    if (event.data === YT.PlayerState.ENDED) {
      const duration = endTime - startTime;

      if (player.getCurrentTime() < endTime - 1) {
        // If the video ends prematurely, attempt to reload it
        setTimeout(() => {
          player.loadVideoById({ videoId: player.getVideoData().video_id, startSeconds: startTime, endSeconds: endTime });
        }, 1000);
      } else {
        if (currentVideoIndex < videos.length - 1) {
          setTimeout(() => {
            currentVideoIndex++;
            displayVideo(currentVideoIndex);
          }, 3000); // 3-second buffer
        } else {
          requestAdditionalYouglishData();
        }
      }
    } else if (event.data === YT.PlayerState.PLAYING) {
      const currentTime = player.getCurrentTime();

      // Check if the current time is within 1 second of the start time
      if (Math.abs(currentTime - startTime) > 1) {
        player.seekTo(startTime, true);
      }
    }
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

  