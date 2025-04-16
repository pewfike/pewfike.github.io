// Smooth scrolling for navigation links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            window.scrollTo({
                top: target.offsetTop - 80, // Account for fixed header
                behavior: 'smooth'
            });
        }
    });
});

// Contact form handling
const contactForm = document.getElementById('contact-form');
if (contactForm) {
    contactForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const submitButton = contactForm.querySelector('button[type="submit"]');
        submitButton.disabled = true;
        submitButton.textContent = 'Sending...';
        
        try {
            const formData = new FormData(contactForm);
            const formProps = Object.fromEntries(formData);
            
            const response = await fetch('http://127.0.0.1:5000/api/send-email', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(formProps)
            });

            const result = await response.json();
            
            if (response.ok) {
                alert('Thank you for your message! I will get back to you soon.');
                contactForm.reset();
            } else {
                throw new Error(result.error || 'Failed to send message');
            }
        } catch (error) {
            alert('Sorry, there was an error sending your message. Please try again later.');
            console.error('Error:', error);
        } finally {
            submitButton.disabled = false;
            submitButton.textContent = 'Send Message';
        }
    });
}

// Sample blog posts data
const blogPosts = [
    {
        title: 'Getting Started with Web Development',
        excerpt: 'Learn the basics of HTML, CSS, and JavaScript to kickstart your web development journey.',
        date: '2024-03-15',
        image: 'https://source.unsplash.com/random/800x600/?coding',
        link: '#'
    },
    {
        title: 'Best Practices for Clean Code',
        excerpt: 'Discover the principles of writing maintainable and efficient code.',
        date: '2024-03-10',
        image: 'https://source.unsplash.com/random/800x600/?programming',
        link: '#'
    },
    // Add more blog posts as needed
];

// Load blog posts
const blogGrid = document.querySelector('.blog-grid');
if (blogGrid) {
    blogPosts.forEach(post => {
        const article = document.createElement('article');
        article.className = 'blog-card';
        article.innerHTML = `
            <img src="${post.image}" alt="${post.title}">
            <div class="blog-content">
                <h3>${post.title}</h3>
                <time>${post.date}</time>
                <p>${post.excerpt}</p>
                <a href="${post.link}" class="btn secondary">Read More</a>
            </div>
        `;
        blogGrid.appendChild(article);
    });
}

// Add scroll-based animations
const observerOptions = {
    threshold: 0.1,
    rootMargin: '0px 0px -50px 0px'
};

const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.classList.add('visible');
            observer.unobserve(entry.target);
        }
    });
}, observerOptions);

document.querySelectorAll('.section').forEach(section => {
    observer.observe(section);
});

// Add styles for blog cards
const style = document.createElement('style');
style.textContent = `
    .blog-card {
        background: white;
        border-radius: 1rem;
        overflow: hidden;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
        transition: transform 0.3s ease;
    }

    .blog-card:hover {
        transform: translateY(-5px);
    }

    .blog-card img {
        width: 100%;
        height: 200px;
        object-fit: cover;
    }

    .blog-content {
        padding: 1.5rem;
    }

    .blog-content h3 {
        margin-bottom: 0.5rem;
        color: var(--text-color);
    }

    .blog-content time {
        color: var(--light-text);
        font-size: 0.875rem;
        display: block;
        margin-bottom: 1rem;
    }

    .blog-content p {
        margin-bottom: 1.5rem;
    }

    .section {
        opacity: 0;
        transform: translateY(20px);
        transition: opacity 0.8s ease, transform 0.8s ease;
    }

    .section.visible {
        opacity: 1;
        transform: translateY(0);
    }
`;
document.head.appendChild(style); 