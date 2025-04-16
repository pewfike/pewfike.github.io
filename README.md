# Personal Portfolio & Blog Website

A modern, responsive personal portfolio website that serves as both a CV and a blog platform. Built with HTML5, CSS3, and vanilla JavaScript.

## Features

- 📱 Fully responsive design
- 🎨 Modern and clean UI
- 🔄 Smooth scrolling navigation
- 📝 Blog section with dynamic content loading
- 📬 Contact form
- 💼 Professional CV/Resume sections
- ✨ Smooth animations and transitions
- 🌐 Social media integration

## Customization

### Basic Information

1. Open `index.html` and replace the following:
   - "Your Name" with your actual name
   - Update the tagline in the hero section
   - Modify the "About Me" section with your personal information
   - Update the experience timeline with your work history
   - Customize the skills section with your expertise

### Styling

The website uses CSS variables for easy customization. In `styles.css`, you can modify the following variables:

```css
:root {
    --primary-color: #2563eb;
    --secondary-color: #1e40af;
    --text-color: #1f2937;
    --light-text: #6b7280;
    --background: #ffffff;
    --section-bg: #f3f4f6;
}
```

### Blog Posts

To add or modify blog posts, edit the `blogPosts` array in `script.js`:

```javascript
const blogPosts = [
    {
        title: 'Your Blog Title',
        excerpt: 'Blog post excerpt...',
        date: 'YYYY-MM-DD',
        image: 'image-url',
        link: 'post-link'
    },
    // Add more posts...
];
```

### Social Links

Update the social media links in the footer section of `index.html`:

```html
<div class="social-links">
    <a href="your-github-url" target="_blank"><i class="fab fa-github"></i></a>
    <a href="your-linkedin-url" target="_blank"><i class="fab fa-linkedin"></i></a>
    <a href="your-twitter-url" target="_blank"><i class="fab fa-twitter"></i></a>
</div>
```

## Contact Form

The contact form is currently set up to show a success message. To make it functional:

1. Create a backend endpoint to handle form submissions
2. Update the form submission code in `script.js`
3. Add proper form validation and error handling

## Profile Image

Replace the `profile-placeholder.jpg` with your own profile image. Make sure to:
- Use a professional photo
- Keep the image size reasonable (recommended: 800x800px)
- Use the same file name or update the reference in `index.html`

## Development

To run the website locally:
1. Clone this repository
2. Open `index.html` in your browser
3. Make your desired changes
4. Test thoroughly across different devices and browsers

## Deployment

You can deploy this website to any static hosting service like:
- GitHub Pages
- Netlify
- Vercel
- AWS S3
- Firebase Hosting

## Browser Support

This website is built with modern web technologies and should work in all modern browsers:
- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

## License

This project is open source and available under the MIT License.

## Contributing

Feel free to fork this project and customize it for your needs. If you find any bugs or have suggestions for improvements, please open an issue or submit a pull request. 