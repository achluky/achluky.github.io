---
layout: default
---

<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Ahmad Luky - Academic Portfolio</title>
    <link rel="stylesheet" href="stylesheets/simple-style.css">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
</head>
<body>
    <!-- Main Container -->
    <div class="main-container">
        
        <!-- Header Section -->
        <header class="header">
            <div class="profile-section">
                <div class="profile-image">
                    <i class="fas fa-graduation-cap"></i>
                </div>
                <div class="profile-info">
                    <h1>Ahmad Luky</h1>
                    <p class="title">Academic Researcher & Educator</p>
                    <p class="bio">Passionate about research, writing, and teaching in the academic community</p>
                </div>
            </div>
        </header>

        <!-- Content Grid -->
        <main class="content-grid">
            
            <!-- About Card -->
            <section class="card about-card">
                <div class="card-header">
                    <i class="fas fa-user"></i>
                    <h2>About</h2>
                </div>
                <p>Academic researcher focused on bridging theory and practice. Dedicated to knowledge discovery, education, and mentoring future scholars.</p>
                <div class="skills">
                    <span class="skill-tag"><i class="fas fa-search"></i> Research</span>
                    <span class="skill-tag"><i class="fas fa-pen"></i> Writing</span>
                    <span class="skill-tag"><i class="fas fa-chart-bar"></i> Analysis</span>
                    <span class="skill-tag"><i class="fas fa-chalkboard-teacher"></i> Teaching</span>
                </div>
            </section>

            <!-- Research Card -->
            <section class="card research-card">
                <div class="card-header">
                    <i class="fas fa-microscope"></i>
                    <h2>Research</h2>
                </div>
                <div class="research-areas">
                    <div class="research-item">
                        <i class="fas fa-calculator"></i>
                        <span>Quantitative Analysis</span>
                    </div>
                    <div class="research-item">
                        <i class="fas fa-laptop"></i>
                        <span>Educational Technology</span>
                    </div>
                    <div class="research-item">
                        <i class="fas fa-brain"></i>
                        <span>Data Science</span>
                    </div>
                    <div class="research-item">
                        <i class="fas fa-handshake"></i>
                        <span>Collaborative Research</span>
                    </div>
                </div>
            </section>

            <!-- Stats Card -->
            <section class="card stats-card">
                <div class="card-header">
                    <i class="fas fa-chart-line"></i>
                    <h2>Statistics</h2>
                </div>
                <div class="stats-grid">
                    <div class="stat-item">
                        <div class="stat-number">50+</div>
                        <div class="stat-label"><i class="fas fa-file-alt"></i> Papers</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-number">500+</div>
                        <div class="stat-label"><i class="fas fa-users"></i> Students</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-number">25+</div>
                        <div class="stat-label"><i class="fas fa-project-diagram"></i> Projects</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-number">5+</div>
                        <div class="stat-label"><i class="fas fa-award"></i> Awards</div>
                    </div>
                </div>
            </section>

            <!-- Publications Card -->
            <section class="card publications-card">
                <div class="card-header">
                    <i class="fas fa-book"></i>
                    <h2>Recent Publications</h2>
                </div>
                <div class="publication-list">
                    <div class="publication">
                        <i class="fas fa-file-pdf"></i>
                        <div>
                            <h4>Modern Research Methodologies</h4>
                            <p>Journal of Academic Research, 2024</p>
                        </div>
                    </div>
                    <div class="publication">
                        <i class="fas fa-file-pdf"></i>
                        <div>
                            <h4>Technology in Higher Education</h4>
                            <p>Educational Technology Review, 2023</p>
                        </div>
                    </div>
                </div>
            </section>

            <!-- Teaching Card -->
            <section class="card teaching-card">
                <div class="card-header">
                    <i class="fas fa-chalkboard-teacher"></i>
                    <h2>Teaching</h2>
                </div>
                <div class="course-list">
                    <div class="course">
                        <i class="fas fa-flask"></i>
                        <span>Research Methodology</span>
                    </div>
                    <div class="course">
                        <i class="fas fa-edit"></i>
                        <span>Academic Writing</span>
                    </div>
                    <div class="course">
                        <i class="fas fa-chart-pie"></i>
                        <span>Data Analysis</span>
                    </div>
                </div>
                <p class="teaching-philosophy">
                    <i class="fas fa-quote-left"></i>
                    Fostering critical thinking and independent research through hands-on learning.
                    <i class="fas fa-quote-right"></i>
                </p>
            </section>

            <!-- Contact Card -->
            <section class="card contact-card">
                <div class="card-header">
                    <i class="fas fa-envelope"></i>
                    <h2>Contact</h2>
                </div>
                <div class="contact-list">
                    <div class="contact-item">
                        <i class="fas fa-paper-plane"></i>
                        <a href="mailto:luky.lucky24@gmail.com">luky.lucky24@gmail.com</a>
                    </div>
                    <div class="contact-item">
                        <i class="fab fa-twitter"></i>
                        <a href="#" target="_blank">@ahmadluky</a>
                    </div>
                    <div class="contact-item">
                        <i class="fab fa-linkedin"></i>
                        <a href="#" target="_blank">LinkedIn Profile</a>
                    </div>
                    <div class="contact-item">
                        <i class="fab fa-github"></i>
                        <a href="#" target="_blank">GitHub</a>
                    </div>
                </div>
                <div class="quick-actions">
                    <button class="action-btn" onclick="window.location.href='mailto:luky.lucky24@gmail.com'">
                        <i class="fas fa-envelope"></i> Send Email
                    </button>
                    <button class="action-btn" onclick="downloadCV()">
                        <i class="fas fa-download"></i> Download CV
                    </button>
                </div>
            </section>

        </main>

        <!-- Footer -->
        <footer class="footer">
            <p><i class="fas fa-heart"></i> Made with passion for academic excellence</p>
            <p>&copy; 2026 Ahmad Luky. All rights reserved.</p>
        </footer>

    </div>

    <script>
        // Simple JavaScript for interactions
        function downloadCV() {
            alert('CV download feature will be implemented soon!');
        }

        // Add hover effects
        document.querySelectorAll('.card').forEach(card => {
            card.addEventListener('mouseenter', function() {
                this.style.transform = 'translateY(-5px)';
            });
            
            card.addEventListener('mouseleave', function() {
                this.style.transform = 'translateY(0)';
            });
        });

        // Animate stats on page load
        window.addEventListener('load', function() {
            const statNumbers = document.querySelectorAll('.stat-number');
            statNumbers.forEach(stat => {
                stat.style.opacity = '0';
                setTimeout(() => {
                    stat.style.opacity = '1';
                    stat.style.transform = 'scale(1.1)';
                    setTimeout(() => {
                        stat.style.transform = 'scale(1)';
                    }, 200);
                }, Math.random() * 1000);
            });
        });
    </script>
</body>
</html>
