document.addEventListener('DOMContentLoaded', () => {
    const kategoriLinks = document.querySelectorAll('.btn-kategori');
    const sections = document.querySelectorAll('#coffee, #non-coffee, #snack');

    // Scroll halus menggunakan scrollIntoView()
    kategoriLinks.forEach(link => {
        link.addEventListener('click', function (e) {
            const targetId = this.getAttribute('href');
            const targetEl = document.querySelector(targetId);

            if (targetEl) {
                e.preventDefault();
                targetEl.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });

                // Update hash di URL
                history.replaceState(null, null, targetId);
            }
        });
    });

    // Highlight aktif saat scroll manual
    window.addEventListener('scroll', () => {
        const scrollY = window.scrollY + 100; // offset sticky navbar
        console.log('scrollY:', scrollY);

        let currentSectionId = null;

        sections.forEach(section => {
            console.log('Section:', section.id, 'offsetTop:', section.offsetTop);
            if (scrollY >= section.offsetTop) {
                currentSectionId = section.id;
            }
        });

        console.log('Current active section:', currentSectionId);

        if (currentSectionId) {
            kategoriLinks.forEach(link => {
                link.classList.remove('btn-primary');
                link.classList.add('btn-outline-primary');
            });

            const activeLink = document.querySelector(`.btn-kategori[href="#${currentSectionId}"]`);
            if (activeLink) {
                activeLink.classList.add('btn-primary');
                activeLink.classList.remove('btn-outline-primary');
            }
        }
    });


    // Jika halaman dibuka langsung dengan hash
    const currentHash = window.location.hash;
    if (currentHash && document.querySelector(currentHash)) {
        setTimeout(() => {
            document.querySelector(currentHash).scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        }, 100);
    }
});