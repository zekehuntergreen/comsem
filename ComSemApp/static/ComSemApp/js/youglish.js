/* NOTE
 * Due to the way that Django assigns URLs, they cannot be dynamically acquired
 * in a JavaScript file. Therefore, in any HTML file this script is used in, an html
 * element with the following contents must be placed above this script
 *
 * <input type="hidden" id="youglish-endpoint" data-url="{% url 'get_youglish_videos' %}" />
 */

const ENDPOINT = $("#youglish-endpoint").attr("data-url");

if (ENDPOINT == null) {
    console.error("No endpoint defind for YouGlish get requests");
}

function get_youglish_videos(phrase, accent = "", page = 1) {
    return new Promise((resolve, reject) => {
        $.ajax({
            url : ENDPOINT,
            method : "GET",
            data : {
                phrase : phrase,
                accent : accent,
                page : page
            },
            dataType : "json",
            timeout : 10000
        })
            .then((data, status) => {
                if (status != 200) {
                    if (status == 400) {
                        // TODO : Establish standard for these promise resolutions
                        reject("Bad request");
                    }
                    if (status == 404) {
                        reject("");
                    }
                    if (status == 500) {
                        reject("");
                    }
                }
                else {
                    resolve(data)
                }
            })
            .catch((reason) => reject(reason))
    })
}