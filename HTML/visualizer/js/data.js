/**
 * Fetches JSON data from a given file path.
 * @param {string} filePath - The path to the JSON file.
 * @returns {Promise<Object>} A promise that resolves to the JSON data.
 */
function fetchJsonData(filePath) {
    console.log(`Fetching JSON data from: ${filePath}`);
    return fetch(filePath)
        .then(response => {
            if (!response.ok) {
                throw new Error(`Network response was not ok for ${filePath}`);
            }
            return response.json();
        })
        .then(data => {
            console.log(`Data fetched successfully from ${filePath}`);
            return data;
        })
        .catch(error => {
            console.error('Error fetching JSON:', error);
            throw error;  // Rethrow the error for handling by the caller
        });
}


/**
 * Formats a date string from 'YYYYMMDD' to 'YYYY-MM-DD' format.
 * @param {string} dateStr - The date string in 'YYYYMMDD' format.
 * @returns {string} The formatted date string.
 */
function formatDate(dateStr) {
    if (!dateStr || dateStr.length !== 8) {
        console.warn('Invalid date string:', dateStr);
        return 'Invalid Date';
    }
    return `${dateStr.substring(0, 4)}-${dateStr.substring(4, 6)}-${dateStr.substring(6, 8)}`;
}

/**
 * Processes the fetched JSON data for visualization.
 * @param {Object[]} data - The JSON data array to process.
 * @param {string} type - The type of data (e.g., 'prev', 'current', 'next').
 * @param {string} cropNum - The crop number.
 * @param {number} imageHeight - The height of the image.
 * @param {number} imageWidth - The width of the image.
 */
function processData(data, type, cropNum, imageHeight, imageWidth) {
    data.forEach(item => {
        createVisualizationElements(item, type, cropNum, imageHeight, imageWidth);
    });
}

//export { fetchJsonData, processData, formatDate, processData };