// Grab important DOM elements
const dropArea = document.getElementById('dropArea');
const fileInput = document.getElementById('fileInput');
const formatSelect = document.getElementById('formatSelect');
const dropMessage = document.getElementById('dropMessage');
const messageContainer = document.getElementById('message_container');
const formatHint = document.getElementById('format_hint');

// Click on drop area opens file selector
dropArea.addEventListener('click', () => fileInput.click());

// Highlight drop area on drag events
['dragenter', 'dragover'].forEach(eventName => {
    dropArea.addEventListener(eventName, e => {
        e.preventDefault();
        e.stopPropagation();
        dropArea.classList.add('highlight');
    });
});

// Remove highlight when leaving or dropping
['dragleave', 'drop'].forEach(eventName => {
    dropArea.addEventListener(eventName, e => {
        e.preventDefault();
        e.stopPropagation();
        dropArea.classList.remove('highlight');
    });
});

// Handle file drop
dropArea.addEventListener('drop', e => {
    const files = e.dataTransfer.files;
    if (files.length > 0) {
        fileInput.files = files;
        displayFileName(files[0]);
        updateFormatOptions(files[0]);
    }
});

// Handle file selection via input
fileInput.addEventListener('change', () => {
    if (fileInput.files.length > 0) {
        displayFileName(fileInput.files[0]);
        updateFormatOptions(fileInput.files[0]);
    }
});

// Show file name in drop message
function displayFileName(file) {
    dropMessage.innerHTML = `Selected: ${file.name}<br>
        <small>Supported formats: pdf, csv, xlsx, txt, png, jpg, jpeg, docx</small>`;
}

// Fetch and update output format options based on file type
function updateFormatOptions(file) {
    const ext = file.name.split('.').pop().toLowerCase();
    fetch(`/get_formats/${ext}`)
        .then(response => response.json())
        .then(formats => {
            formatSelect.innerHTML = '<option value="">Select output format</option>';
            formats.forEach(fmt => {
                const option = document.createElement('option');
                option.value = fmt;
                option.textContent = fmt.toUpperCase();
                formatSelect.appendChild(option);
            });
            formatHint.textContent = formats.length > 0
                ? `Valid outputs: ${formats.join(', ').toUpperCase()}`
                : 'No valid conversions for this file type';
        });
}

// Show messages (success, error, etc.)
function showMessage(text, type) {
    messageContainer.innerHTML = `<div class="message ${type}">${text}</div>`;
    setTimeout(() => { messageContainer.innerHTML = ''; }, 3000);
}

// Show converting message when submitting form
document.getElementById('uploadForm').addEventListener('submit', function(e) {
    showMessage('Converting file...', 'success');
});