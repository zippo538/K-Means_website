document.addEventListener('DOMContentLoaded', function() {
    // Mobile Menu Toggle
    const mobileMenu = document.getElementById('mobile-menu');
    const navbarMenu = document.getElementById('navbar-menu');
    
    if (mobileMenu && navbarMenu) {
        mobileMenu.addEventListener('click', function() {
            this.classList.toggle('active');
            navbarMenu.classList.toggle('active');
        });
    }
    
    // Close menu when clicking on nav links (mobile)
    document.querySelectorAll('.nav-link').forEach(link => {
        link.addEventListener('click', function() {
            if (window.innerWidth <= 768) {
                mobileMenu.classList.remove('active');
                navbarMenu.classList.remove('active');
            }
        });
    });
    
    // Dropdown functionality for desktop
    if (window.innerWidth > 768) {
        document.querySelectorAll('.dropdown').forEach(dropdown => {
            dropdown.addEventListener('mouseenter', function() {
                this.querySelector('.dropdown-menu').style.opacity = '1';
                this.querySelector('.dropdown-menu').style.visibility = 'visible';
                this.querySelector('.dropdown-menu').style.transform = 'translateY(0)';
                this.querySelector('.dropdown-icon').style.transform = 'rotate(180deg)';
            });
            
            dropdown.addEventListener('mouseleave', function() {
                this.querySelector('.dropdown-menu').style.opacity = '0';
                this.querySelector('.dropdown-menu').style.visibility = 'hidden';
                this.querySelector('.dropdown-menu').style.transform = 'translateY(10px)';
                this.querySelector('.dropdown-icon').style.transform = 'rotate(0)';
            });
        });
    }
    
    // Dropdown functionality for mobile
    if (window.innerWidth <= 768) {
        document.querySelectorAll('.dropdown-toggle').forEach(toggle => {
            toggle.addEventListener('click', function(e) {
                e.preventDefault();
                const dropdown = this.parentElement;
                const menu = dropdown.querySelector('.dropdown-menu');
                
                // Close all other dropdowns
                document.querySelectorAll('.dropdown-menu').forEach(item => {
                    if (item !== menu) {
                        item.style.display = 'none';
                    }
                });
                
                // Toggle current dropdown
                if (menu.style.display === 'block') {
                    menu.style.display = 'none';
                } else {
                    menu.style.display = 'block';
                }
            });
        });
    }
    
    // Highlight active link
    document.querySelectorAll('.nav-link, .dropdown-item').forEach(link => {
        if (link.href === window.location.href) {
            link.classList.add('active');
            
            // If this is a dropdown item, highlight its parent too
            if (link.classList.contains('dropdown-item')) {
                const dropdown = link.closest('.dropdown');
                if (dropdown) {
                    dropdown.querySelector('.dropdown-toggle').classList.add('active');
                }
            }
        }
    });
    
    // Update on window resize
    window.addEventListener('resize', function() {
        if (window.innerWidth > 768) {
            // Reset mobile menu
            if (mobileMenu) mobileMenu.classList.remove('active');
            if (navbarMenu) navbarMenu.classList.remove('active');
            
            // Reset dropdowns
            document.querySelectorAll('.dropdown-menu').forEach(menu => {
                menu.style.display = '';
            });
        }
    });
});