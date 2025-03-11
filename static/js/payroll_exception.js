$(document).ready(function() {
    const $startTimeField = $('#exception-start-time');
    const $endTimeField = $('#exception-end-time');

    function handleTimeInput() {
        const startTime = $startTimeField.val();
        const endTime = $endTimeField.val();

        if (startTime.length >= 4 && endTime.length >= 4) {
            calculateExceptionHours(formatTimeField(startTime), formatTimeField(endTime));
        }
    }

    function formatTimeField(input) {
        // Remove any non-digit characters
        let cleanedInput = input.replace(/\D/g, '');

        // If the cleaned input has less than 4 digits, pad it with leading zeros
        while (cleanedInput.length < 4) {
            cleanedInput = '0' + cleanedInput;
        }

        // Extract hours and minutes
        const hours = cleanedInput.slice(0, 2).padStart(2, '0');
        const minutes = cleanedInput.slice(2, 4).padStart(2, '0');

        // Combine hours and minutes with a colon
        return `${hours}:${minutes}`;
    }

    function calculateExceptionHours(start, end) {
        // Parse the start and end times
        const startTime = new Date(`1970-01-01T${start}Z`);
        const endTime = new Date(`1970-01-01T${end}Z`);

        // Calculate the difference in milliseconds
        const diffInMilliseconds = endTime - startTime;

        // Convert milliseconds to hours
        const diffInHours = diffInMilliseconds / (1000 * 60 * 60);

        // Get the integer part of the difference in hours
        const exceptionHours = Math.floor(diffInHours);

        // Update the exception hours field
        $('#exception-hours').text(exceptionHours);
    }

    $startTimeField.on('input', handleTimeInput);
    $endTimeField.on('input', handleTimeInput);
});
