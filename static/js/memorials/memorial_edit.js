// BANNER
document.addEventListener("DOMContentLoaded", function() {
    console.log("Banner script loaded");

    // Get elements
    const banner = document.getElementById('memorialBanner');
    const modal = document.getElementById('bannerSelectionModal');
    const changeBannerBtn = document.getElementById('changeBannerBtn');
    const closeModalBtn = document.getElementById('closeBannerModal');
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    const memorialId = banner.dataset.memorialId;

    // Save banner selection to server
    async function saveBannerSelection(type, value) {
        try {
            const formData = new FormData();
            formData.append('banner_type', type);
            formData.append('banner_value', value);
            
            const response = await fetch(`/memorials/${memorialId}/update-banner/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': csrfToken
                },
                body: formData
            });

            if (!response.ok) {
                throw new Error(`Server responded with ${response.status}`);
            }

            return await response.json();
        } catch (error) {
            console.error('Error saving banner:', error);
            throw error;
        }
    }

    // Handle banner selection
    document.querySelectorAll('.banner-option').forEach(option => {
        option.addEventListener('click', async function() {
            const type = this.dataset.type;
            let value = this.dataset.value;

            try {
                // For images, use full static path for display
                const displayValue = type === 'image' ? `/static/${value}` : value;
                
                // Update visual immediately
                if (type === 'image') {
                    banner.style.backgroundImage = `url('${displayValue}')`;
                    banner.style.backgroundColor = 'transparent';
                } else {
                    banner.style.backgroundImage = 'none';
                    banner.style.backgroundColor = displayValue;
                }

                // Save to server (store relative path for images)
                const saveValue = type === 'image' ? value : displayValue;
                await saveBannerSelection(type, saveValue);

                // Update classes
                banner.className = 'banner ' + (type === 'image' ? 'banner-image' : 'banner-color');
                
                // Close modal
                modal.style.display = 'none';

            } catch (error) {
                // Revert on error
                banner.style.backgroundImage = banner.dataset.originalBg || '';
                banner.style.backgroundColor = banner.dataset.originalColor || '';
                alert(`Failed to update banner: ${error.message}`);
            }
        });
    });

    // Store original banner state
    banner.dataset.originalBg = banner.style.backgroundImage;
    banner.dataset.originalColor = banner.style.backgroundColor;

    // Modal controls
    if (changeBannerBtn) {
        changeBannerBtn.addEventListener('click', () => {
            modal.style.display = 'block';
        });
    }

    if (closeModalBtn) {
        closeModalBtn.addEventListener('click', () => {
            modal.style.display = 'none';
        });
    }

    // Close modal when clicking outside
    document.addEventListener('click', (e) => {
        if (modal.style.display === 'block' && 
            !modal.contains(e.target) && 
            e.target !== changeBannerBtn) {
            modal.style.display = 'none';
        }
    });
});


// NAMES AND DATES 

document.addEventListener('DOMContentLoaded', function() {
    // Handle name form submission
    document.getElementById('name-edit-form').addEventListener('submit', function(e) {
        e.preventDefault();
        const form = e.target;
        const formData = new FormData(form);
        
        // Get the correct URL from the form's action attribute
        const updateUrl = form.action.replace('/edit/', '/update-name/');
        
        fetch(updateUrl, {
            method: 'POST',
            body: formData,
            headers: {
                'X-CSRFToken': formData.get('csrfmiddlewaretoken'),
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
        .then(response => {
            if (!response.ok) {
                return response.text().then(text => { throw new Error(text) });
            }
            return response.json();
        })
        .then(data => {
            if (data.status === 'success') {
                document.getElementById('editable-name').innerHTML = 
                    `${data.new_name} <i class="fas fa-edit ms-2" style="font-size: 0.6em; opacity: 0.7;"></i>`;
                bootstrap.Modal.getInstance(document.getElementById('nameEditModal')).hide();
            } else {
                alert('Error updating name: ' + (data.message || 'Unknown error'));
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Failed to update name. Server responded with: ' + error.message);
        });
    });

    // Handle dates form submission
    document.getElementById('dates-edit-form').addEventListener('submit', function(e) {
        e.preventDefault();
        const form = e.target;
        const formData = new FormData(form);
        
        // Get the correct URL from the form's action attribute
        const updateUrl = form.action.replace('/edit/', '/update-dates/');
        
        fetch(updateUrl, {
            method: 'POST',
            body: formData,
            headers: {
                'X-CSRFToken': formData.get('csrfmiddlewaretoken'),
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
        .then(response => {
            if (!response.ok) {
                return response.text().then(text => { throw new Error(text) });
            }
            return response.json();
        })
        .then(data => {
            if (data.status === 'success') {
                document.getElementById('editable-dates').innerHTML = 
                    `${data.new_dates} <i class="fas fa-edit ms-2" style="font-size: 0.6em; opacity: 0.7;"></i>`;
                bootstrap.Modal.getInstance(document.getElementById('datesEditModal')).hide();
            } else {
                alert('Error updating dates: ' + (data.message || 'Unknown error'));
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Failed to update dates. Server responded with: ' + error.message);
        });
    });
});

// QUOTE SECTION
document.addEventListener('DOMContentLoaded', function() {
    const quoteForm = document.getElementById('quote-edit-form');
    
    if (quoteForm) {
        quoteForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            // Get memorial ID from the form action URL
            const memorialId = quoteForm.action.split('/').filter(part => part).slice(-2, -1)[0];
            
            // Prepare the data
            const formData = new FormData(quoteForm);
            const quoteText = formData.get('quote').trim();
            
            fetch(`/memorials/${memorialId}/update-quote/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': formData.get('csrfmiddlewaretoken'),
                    'X-Requested-With': 'XMLHttpRequest'
                },
                body: JSON.stringify({
                    quote: quoteText
                })
            })
            .then(response => {
                if (!response.ok) {
                    return response.text().then(text => {
                        throw new Error(text || 'Failed to update quote');
                    });
                }
                return response.json();
            })
            .then(data => {
                if (data.status === 'success') {
                    // Update the displayed quote
                    const quoteElement = document.getElementById('editable-quote');
                    quoteElement.innerHTML = data.quote || 
                        `In Loving Memory of ${document.getElementById('editable-name').textContent.trim().split(' ')[0]}`;
                    quoteElement.innerHTML += '<i class="fas fa-edit ms-2" style="font-size: 0.8em; opacity: 0.6;"></i>';
                    
                    // Close the modal
                    bootstrap.Modal.getInstance(document.getElementById('quoteEditModal')).hide();
                    

                } else {
                    throw new Error(data.message || 'Failed to update quote');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('Error updating quote: ' + (error.message || 'Please try again'));
            });
        });
    }
});


// BIOGRAPHY

document.getElementById('biography-edit-form').addEventListener('submit', function(e) {
    e.preventDefault();
    const formData = new FormData(this);
    
    fetch(this.action, {
        method: 'POST',
        body: formData,
        headers: {
            'X-CSRFToken': formData.get('csrfmiddlewaretoken'),
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
    .then(response => {
        if (!response.ok) {
            return response.text().then(text => { throw new Error(text) });
        }
        return response.json();
    })
    .then(data => {
        if (data.success) {
            document.getElementById('editable-biography').innerHTML = 
                data.biography + '<small class="text-muted d-block mt-2"><i class="fas fa-edit"></i> Edit biography</small>';
            // Close modal or show success message
            return bootstrap.Modal.getInstance(document.getElementById('biographyEditModal')).hide();
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Failed to save biography. Please try again.');
    });
});