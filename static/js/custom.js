// Custom JavaScript for Support System

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Auto-dismiss alerts after 5 seconds
    setTimeout(function() {
        var alerts = document.querySelectorAll('.alert');
        alerts.forEach(function(alert) {
            var bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        });
    }, 5000);
    
    // Mark all notifications as read
    $('#mark-all-read').on('click', function(e) {
        e.preventDefault();
        
        const formData = new FormData();
        
        $.ajax({
            url: '/notifications/mark-read/',
            type: 'POST',
            data: formData,
            processData: false,
            contentType: false,
            headers: {
                'X-CSRFToken': getCSRFToken()
            },
            success: function(response) {
                if (response.success) {
                    $('.notification-item.unread').removeClass('unread');
                    $('.notification-badge').remove();
                    showAlert('success', 'All notifications marked as read');
                }
            },
            error: function() {
                showAlert('danger', 'Error marking notifications as read');
            }
        });
    });
    
    // Mark individual notification as read
    $(document).on('click', '.mark-notification-read', function(e) {
        e.preventDefault();
        e.stopPropagation();
        
        const notificationItem = $(this).closest('.notification-item');
        const notificationId = notificationItem.data('notification-id');
        
        const formData = new FormData();
        formData.append('notification_id', notificationId);
        
        $.ajax({
            url: '/notifications/mark-read/',
            type: 'POST',
            data: formData,
            processData: false,
            contentType: false,
            headers: {
                'X-CSRFToken': getCSRFToken()
            },
            success: function(response) {
                if (response.success) {
                    notificationItem.removeClass('unread');
                    
                    // Update notification badge count
                    const badge = $('.notification-badge');
                    const count = parseInt(badge.text());
                    if (count > 1) {
                        badge.text(count - 1);
                    } else {
                        badge.remove();
                    }
                }
            },
            error: function() {
                showAlert('danger', 'Error marking notification as read');
            }
        });
    });
    
    // Helper function to get CSRF token
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
    
    // Helper function to show alerts
    function showAlert(message, type) {
        var alertContainer = document.getElementById('alert-container');
        if (!alertContainer) {
            alertContainer = document.createElement('div');
            alertContainer.id = 'alert-container';
            alertContainer.style.position = 'fixed';
            alertContainer.style.top = '20px';
            alertContainer.style.right = '20px';
            alertContainer.style.zIndex = '9999';
            document.body.appendChild(alertContainer);
        }
        
        var alert = document.createElement('div');
        alert.className = 'alert alert-' + type + ' alert-dismissible fade show';
        alert.innerHTML = message + 
            '<button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>';
        
        alertContainer.appendChild(alert);
        
        setTimeout(function() {
            var bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    }

    // Category-Department relationship (if applicable)
    var categorySelect = document.getElementById('id_category');
    var departmentSelect = document.getElementById('id_department');
    
    if (categorySelect && departmentSelect) {
        categorySelect.addEventListener('change', function() {
            // This would be implemented if categories are related to departments
            // For now, it's just a placeholder for future functionality
            console.log('Category changed to:', categorySelect.value);
        });
    }

    // Ticket status color indicator
    var statusBadges = document.querySelectorAll('.badge');
    statusBadges.forEach(function(badge) {
        var status = badge.textContent.trim().toLowerCase();
        if (status === 'open') {
            badge.classList.add('bg-open');
        } else if (status === 'in progress') {
            badge.classList.add('bg-in_progress');
        } else if (status === 'pending') {
            badge.classList.add('bg-pending');
        } else if (status === 'resolved') {
            badge.classList.add('bg-resolved');
        } else if (status === 'closed') {
            badge.classList.add('bg-closed');
        }
    });

    // Confirm delete actions
    var deleteButtons = document.querySelectorAll('.btn-delete');
    deleteButtons.forEach(function(button) {
        button.addEventListener('click', function(e) {
            if (!confirm('Are you sure you want to delete this item? This action cannot be undone.')) {
                e.preventDefault();
            }
        });
    });

    // Form validation
    var forms = document.querySelectorAll('.needs-validation');
    Array.prototype.slice.call(forms).forEach(function(form) {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        }, false);
    });
});