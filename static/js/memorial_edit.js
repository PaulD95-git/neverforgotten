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