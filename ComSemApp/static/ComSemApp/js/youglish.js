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
            timeout : 10000,
            statusCode : {
                200 : (data) => { console.log("a"); resolve(data); }, 
                400 : () => { console.log("b"); reject("Bad request");} ,
                404 : () => { console.log("c"); reject("");} ,
                500 : () => { console.log("d"); reject("");}
            },
            error : (reason) => { console.log("e"); reject(reason); } 
        })
    });
}