
import { fetchJsonData, processData } from './data.js';
import { displayUrlParams, initUI } from './ui.js';

document.addEventListener('DOMContentLoaded', () => {
    console.log('Initializing the visualizer application.');

    // Initialize the UI components
    initUI();

    // Default parameters
    const defaultParams = {
        cropNum: 'crop1000',
        prev: '20230602',
        current: '20230531',
        next: '20230529'
    };

    // Extract URL parameters
    const urlParams = new URLSearchParams(window.location.search);
    let params = {
        cropNum: urlParams.get('crop'),
        prev: urlParams.get('prev'),
        current: urlParams.get('current'),
        next: urlParams.get('next')
    };

    // Flag to indicate whether default values are used
    let usingDefaultParams = false;

    // Check if all parameters are present, else use default values
    if (!params.cropNum || !params.prev || !params.current || !params.next) {
        console.warn('URL parameters missing, using default/testing parameters.');
        params = { ...defaultParams };
        usingDefaultParams = true;

        // Optional: Append default parameters to the URL
        const newUrl = `${window.location.pathname}?crop=${params.cropNum}&prev=${params.prev}&current=${params.current}&next=${params.next}`;
        window.history.replaceState(null, '', newUrl);
    }

    // Display URL parameters in the UI
    displayUrlParams(params);

    // Fetch and process JSON data for each parameter

    // log the params object
    console.log(`params:`, params);

    Object.keys(params).forEach(key => {
        if (params[key]) {

            console.log(`Building file path for with params: 'params.cropNum': ${params.cropNum}, 'params[key]': ${params[key]}`);
            const filePath = `../output/${params.cropNum}/${params[key]}/${params[key]}.json`;
            fetchJsonData(filePath)
                .then(data => {
                    const processedData = processData(data);
                    console.log(`Data processed for ${key}:`, processedData);
                })
                .catch(error => {
                    console.error(`Error fetching data for ${key}:`, error);
                });
        }
    });

    // Additional logic based on usingDefaultParams if needed
});

