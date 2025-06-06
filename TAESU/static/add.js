document.addEventListener("DOMContentLoaded", () => {
    const now = new Date();
    const year = now.getFullYear();
    const month = String(now.getMonth() + 1).padStart(2, '0');
    const day = String(now.getDate()).padStart(2, '0');
    const hours = String(now.getHours()).padStart(2, '0');
    const minutes = String(now.getMinutes()).padStart(2, '0');
    const datetime = `${year}-${month}-${day}T${hours}:${minutes}`;
    const date = `${year}-${month}-${day}`;

    document.querySelectorAll('.datetimelimit').forEach(input => {

        input.min = datetime;
    });

    document.querySelectorAll('.datelimit').forEach(input => {

        input.min = date;
    });

    document.querySelectorAll('form').forEach(form => {
        form.addEventListener("submit", () => {
            const now = new Date();
            const year = now.getFullYear();
            const month = String(now.getMonth() + 1).padStart(2, '0');
            const day = String(now.getDate()).padStart(2, '0');
            const hours = String(now.getHours()).padStart(2, '0');
            const minutes = String(now.getMinutes()).padStart(2, '0');
            const seconds = String(now.getSeconds()).padStart(2, '0');
            const datetimeNow = `${year}-${month}-${day}T${hours}:${minutes}:${seconds}`;

            document.querySelectorAll('.c_time').forEach(input => {
                input.value = datetimeNow;

            });
        });
    });

});


