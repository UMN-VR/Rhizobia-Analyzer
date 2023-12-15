/**
 * Handles all UI-related functionalities for the visualizer.
 */

/**
 * Displays URL parameters in the UI.
 * @param {Object} params - The URL parameters.
 */
function displayUrlParams(params) {
    const { cropNum, prev, current, next } = params;
    const paramsContainer = document.getElementById('params-container');
    paramsContainer.innerHTML = `
        <p>Crop Number: ${cropNum}</p>
        <p>Previous Date: ${prev}</p>
        <p>Current Date: ${current}</p>
        <p>Next Date: ${next}</p>
    `;
    console.log('Displayed URL parameters.');
}

/**
 * Toggles the visibility of a class of elements based on a checkbox state.
 * @param {string} className - The class name of elements to toggle.
 * @param {HTMLElement} checkbox - The checkbox element.
 */
function toggleVisibility(className, checkbox) {
    const elements = document.getElementsByClassName(className);
    Array.from(elements).forEach(element => {
        element.style.display = checkbox.checked ? 'block' : 'none';
    });
    console.log(`Toggled visibility for elements with class: ${className}`);
}

/**
 * Updates the range slider value display.
 * @param {HTMLElement} slider - The range slider element.
 * @param {HTMLElement} displayElement - The element to display the slider's value.
 */
function updateSliderDisplay(slider, displayElement) {
    displayElement.textContent = slider.value;
    console.log(`Updated slider display: ${slider.value}`);
}

/**
 * Initializes the UI components.
 */
function initUI() {
    // Initialize range sliders
    const sliders = document.querySelectorAll('.range-slider');
    sliders.forEach(slider => {
        const displayElement = document.querySelector(`#${slider.id}-value`);
        slider.addEventListener('input', () => updateSliderDisplay(slider, displayElement));
        // Update display on load
        updateSliderDisplay(slider, displayElement);
    });

    // Initialize checkboxes
    const checkboxes = document.querySelectorAll('.visibility-checkbox');
    checkboxes.forEach(checkbox => {
        const targetClass = checkbox.getAttribute('data-target');
        checkbox.addEventListener('change', () => toggleVisibility(targetClass, checkbox));
    });

    console.log('UI initialized.');
}

/**
 * Creates and appends visualization elements based on the item data.
 * @param {Object} item - The individual item from the data array.
 * @param {string} type - The type of the data (e.g., 'prev', 'current', 'next').
 * @param {string} cropNum - The crop number.
 * @param {number} imageHeight - The height of the image.
 * @param {number} imageWidth - The width of the image.
 */
function createVisualizationElements(item, type, cropNum, imageHeight, imageWidth) {
    const imageContainer = document.querySelector('.image-container');
    const container = document.createElement('div');
    container.style.position = 'absolute';
    container.style.top = `${(item.r.y / imageHeight * 100) - 0.5}%`;
    container.style.left = `${(item.r.x / imageWidth * 100) - 0.5}%`;

    const element = document.createElement('div');
    element.className = `circle-${type}`;
    if (type !== 'current') {
        element.classList.add('hidden');
    }
    element.style.width = `${item.r.w}px`;
    element.style.height = `${item.r.h}px`;

    const hexColor = item.rgb_s;
    const r = parseInt(hexColor.substring(0, 2), 16);
    const g = parseInt(hexColor.substring(2, 4), 16);
    const b = parseInt(hexColor.substring(4, 6), 16);
    const rgbaColor = `rgba(${r}, ${g}, ${b}, 0.5)`;
    element.style.backgroundColor = rgbaColor;

    const tooltip = document.createElement('div');
    tooltip.className = 'tooltip';
    const match_id_full = item.m.id;
    const match_id_num = match_id_full.split('_')[1];
    const match_id_date = match_id_full.split('_')[0];
    const formatted_id_date = `${match_id_date.substring(0,4)}-${match_id_date.substring(4,6)}-${match_id_date.substring(6,8)}`;

    // Constructing the tooltip content
    const tooltipContent = `
        <strong>Match ID:</strong> ${match_id_full}<br>
        <strong>Formatted Date:</strong> ${formatted_id_date}<br>
        <strong>RGB:</strong> ${hexColor}<br>
        <strong>Area:</strong> ${item.area || 'N/A'}<br>
        <strong>Coordinates:</strong> X:${item.r.x}, Y:${item.r.y}<br>
        <strong>Size:</strong> Width:${item.r.w}, Height:${item.r.h}
        // Add more item properties as needed
    `;
    tooltip.innerHTML = tooltipContent;

    element.appendChild(tooltip);
    container.appendChild(element);
    imageContainer.appendChild(container);
}

//export { displayUrlParams, toggleVisibility, initUI, updateSliderDisplay, createVisualizationElements };
