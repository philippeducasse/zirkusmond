(function () {
    function defaultTimeForDate(value) {
        if (!value) {
            return '19:00';
        }
        var date = new Date(value + 'T00:00:00');
        if (isNaN(date.getTime())) {
            return '19:00';
        }
        var weekday = date.getUTCDay(); // 5 = Friday, 6 = Saturday
        if (weekday === 5 || weekday === 6) {
            return '20:00';
        }
        return '19:00';
    }

    function subtractHour(timeValue) {
        if (!timeValue) {
            return '';
        }
        var parts = timeValue.split(':');
        if (parts.length < 2) {
            return '';
        }
        var hour = parseInt(parts[0], 10);
        var minute = parseInt(parts[1], 10);
        if (isNaN(hour) || isNaN(minute)) {
            return '';
        }
        hour -= 1;
        if (hour < 0) {
            hour += 24;
        }
        return (hour < 10 ? '0' + hour : hour) + ':' + (minute < 10 ? '0' + minute : minute);
    }

    function adjustAdmissionTime(row) {
        var timeInput = row.querySelector('.event-time-input');
        var admissionInput = row.querySelector('.admission-time-input');
        if (!timeInput || !admissionInput) {
            return;
        }

        timeInput.dataset.userModified = timeInput.dataset.userModified || 'false';
        admissionInput.dataset.userModified = admissionInput.dataset.userModified || 'false';

        function updateAdmission() {
            if (admissionInput.dataset.userModified === 'true') {
                return;
            }
            if (!timeInput.value) {
                return;
            }
            var newValue = subtractHour(timeInput.value);
            if (!newValue) {
                return;
            }
            admissionInput.value = newValue;
            admissionInput.dataset.userModified = 'false';
        }

        function syncAdmission() {
            updateAdmission();
        }

        timeInput.addEventListener('change', syncAdmission);
        timeInput.addEventListener('input', syncAdmission);

        admissionInput.addEventListener('input', function () {
            admissionInput.dataset.userModified = 'true';
        });

        if (!admissionInput.value) {
            updateAdmission();
        }
    }

    function applyDefaults(row) {
        var dateInput = row.querySelector('.event-date-input');
        var timeInput = row.querySelector('.event-time-input');
        var admissionInput = row.querySelector('.admission-time-input');
        if (!dateInput || !timeInput || !admissionInput) {
            return;
        }

        timeInput.dataset.userModified = timeInput.dataset.userModified || 'false';
        admissionInput.dataset.userModified = admissionInput.dataset.userModified || 'false';

        function updateTimeIfNeeded() {
            if (timeInput.value && timeInput.dataset.userModified === 'true') {
                return;
            }
            var newValue = defaultTimeForDate(dateInput.value);
            timeInput.value = newValue;
            timeInput.dataset.userModified = 'false';
        }

        dateInput.addEventListener('change', updateTimeIfNeeded);
        timeInput.addEventListener('input', function () {
            timeInput.dataset.userModified = 'true';
        });

        if (!timeInput.value) {
            updateTimeIfNeeded();
        }
        adjustAdmissionTime(row);
        if (!admissionInput.value) {
            var initialAdmission = subtractHour(timeInput.value) || '18:00';
            admissionInput.value = initialAdmission;
            admissionInput.dataset.userModified = 'false';
        }
    }

    function initInlineRows(scope) {
        scope.querySelectorAll('.dynamic-event_set').forEach(applyDefaults);
    }

    document.addEventListener('DOMContentLoaded', function () {
        initInlineRows(document);
        document.body.addEventListener('formset:added', function (event) {
            applyDefaults(event.target);
        });
    });
})();
