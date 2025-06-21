// Authentication JavaScript
document.addEventListener('DOMContentLoaded', function() {
    // Import Firebase functions
    const { signInWithEmailAndPassword, createUserWithEmailAndPassword, signInWithPopup, sendPasswordResetEmail, updateProfile } = window.firebaseAuth;
    const auth = window.firebaseAuth;
    const database = window.firebaseDatabase;
    const googleProvider = window.googleProvider;

    // DOM elements
    const loginForm = document.getElementById('loginForm');
    const registerForm = document.getElementById('registerForm');
    const googleLoginBtn = document.getElementById('googleLoginBtn');
    const googleRegisterBtn = document.getElementById('googleRegisterBtn');
    const forgotPasswordLink = document.getElementById('forgotPasswordLink');
    const authMessage = document.getElementById('authMessage');

    // Tab switching
    window.switchTab = function(tab) {
        const loginTab = document.querySelector('.tab-btn[onclick="switchTab(\'login\')"]');
        const registerTab = document.querySelector('.tab-btn[onclick="switchTab(\'register\')"]');
        const loginForm = document.getElementById('login-form');
        const registerForm = document.getElementById('register-form');

        if (tab === 'login') {
            loginTab.classList.add('active');
            registerTab.classList.remove('active');
            loginForm.classList.add('active');
            registerForm.classList.remove('active');
        } else {
            registerTab.classList.add('active');
            loginTab.classList.remove('active');
            registerForm.classList.add('active');
            loginForm.classList.remove('active');
        }
        hideMessage();
    };

    // Show message function
    function showMessage(message, type = 'error') {
        authMessage.textContent = message;
        authMessage.className = `auth-message ${type}`;
        authMessage.style.display = 'block';
        
        // Auto hide after 5 seconds
        setTimeout(() => {
            hideMessage();
        }, 5000);
    }

    // Hide message function
    function hideMessage() {
        authMessage.style.display = 'none';
    }

    // Set loading state
    function setLoading(button, isLoading) {
        const btnText = button.querySelector('.btn-text');
        const btnLoading = button.querySelector('.btn-loading');
        
        if (isLoading) {
            button.disabled = true;
            if (btnText) btnText.style.display = 'none';
            if (btnLoading) btnLoading.style.display = 'inline';
        } else {
            button.disabled = false;
            if (btnText) btnText.style.display = 'inline';
            if (btnLoading) btnLoading.style.display = 'none';
        }
    }

    // Save user data to Firebase Realtime Database
    async function saveUserData(user, additionalData = {}) {
        try {
            const { ref, set } = await import("https://www.gstatic.com/firebasejs/11.9.1/firebase-database.js");
            
            const userData = {
                uid: user.uid,
                email: user.email,
                displayName: user.displayName || additionalData.displayName || '',
                photoURL: user.photoURL || '',
                createdAt: new Date().toISOString(),
                lastLogin: new Date().toISOString(),
                provider: additionalData.provider || 'email',
                ...additionalData
            };

            await set(ref(database, 'users/' + user.uid), userData);
            console.log('User data saved to database');
        } catch (error) {
            console.error('Error saving user data:', error);
        }
    }

    // Update user last login
    async function updateLastLogin(user) {
        try {
            const { ref, update } = await import("https://www.gstatic.com/firebasejs/11.9.1/firebase-database.js");
            
            await update(ref(database, 'users/' + user.uid), {
                lastLogin: new Date().toISOString()
            });
        } catch (error) {
            console.error('Error updating last login:', error);
        }
    }

    // Login form handler
    if (loginForm) {
        loginForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const email = document.getElementById('loginEmail').value;
            const password = document.getElementById('loginPassword').value;
            const loginBtn = document.getElementById('loginBtn');

            if (!email || !password) {
                showMessage('يرجى ملء جميع الحقول المطلوبة');
                return;
            }

            setLoading(loginBtn, true);
            hideMessage();

            try {
                const userCredential = await signInWithEmailAndPassword(auth, email, password);
                const user = userCredential.user;
                
                // Update last login
                await updateLastLogin(user);
                
                showMessage('تم تسجيل الدخول بنجاح! جاري التوجيه...', 'success');
                
                // Redirect to main chat page
                setTimeout(() => {
                    window.location.href = '/';
                }, 1500);
                
            } catch (error) {
                console.error('Login error:', error);
                let errorMessage = 'حدث خطأ أثناء تسجيل الدخول';
                
                switch (error.code) {
                    case 'auth/user-not-found':
                        errorMessage = 'البريد الإلكتروني غير مسجل';
                        break;
                    case 'auth/wrong-password':
                        errorMessage = 'كلمة المرور غير صحيحة';
                        break;
                    case 'auth/invalid-email':
                        errorMessage = 'البريد الإلكتروني غير صالح';
                        break;
                    case 'auth/too-many-requests':
                        errorMessage = 'تم تجاوز عدد المحاولات المسموح. حاول مرة أخرى لاحقاً';
                        break;
                    case 'auth/invalid-credential':
                        errorMessage = 'بيانات الاعتماد غير صحيحة';
                        break;
                }
                
                showMessage(errorMessage);
            } finally {
                setLoading(loginBtn, false);
            }
        });
    }

    // Register form handler
    if (registerForm) {
        registerForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const name = document.getElementById('registerName').value;
            const email = document.getElementById('registerEmail').value;
            const password = document.getElementById('registerPassword').value;
            const confirmPassword = document.getElementById('confirmPassword').value;
            const registerBtn = document.getElementById('registerBtn');

            if (!name || !email || !password || !confirmPassword) {
                showMessage('يرجى ملء جميع الحقول المطلوبة');
                return;
            }

            if (password !== confirmPassword) {
                showMessage('كلمات المرور غير متطابقة');
                return;
            }

            if (password.length < 6) {
                showMessage('كلمة المرور يجب أن تكون 6 أحرف على الأقل');
                return;
            }

            setLoading(registerBtn, true);
            hideMessage();

            try {
                const userCredential = await createUserWithEmailAndPassword(auth, email, password);
                const user = userCredential.user;
                
                // Update user profile with display name
                await updateProfile(user, {
                    displayName: name
                });
                
                // Save user data to database
                await saveUserData(user, {
                    displayName: name,
                    provider: 'email'
                });
                
                showMessage('تم إنشاء الحساب بنجاح! جاري التوجيه...', 'success');
                
                // Redirect to main chat page
                setTimeout(() => {
                    window.location.href = '/';
                }, 1500);
                
            } catch (error) {
                console.error('Registration error:', error);
                let errorMessage = 'حدث خطأ أثناء إنشاء الحساب';
                
                switch (error.code) {
                    case 'auth/email-already-in-use':
                        errorMessage = 'البريد الإلكتروني مستخدم بالفعل';
                        break;
                    case 'auth/invalid-email':
                        errorMessage = 'البريد الإلكتروني غير صالح';
                        break;
                    case 'auth/weak-password':
                        errorMessage = 'كلمة المرور ضعيفة جداً';
                        break;
                }
                
                showMessage(errorMessage);
            } finally {
                setLoading(registerBtn, false);
            }
        });
    }

    // Google Sign In handlers
    async function handleGoogleSignIn() {
        try {
            const result = await signInWithPopup(auth, googleProvider);
            const user = result.user;
            
            // Check if user is new
            const isNewUser = result._tokenResponse?.isNewUser;
            
            if (isNewUser) {
                // Save new user data
                await saveUserData(user, {
                    provider: 'google'
                });
            } else {
                // Update last login for existing user
                await updateLastLogin(user);
            }
            
            showMessage('تم تسجيل الدخول بنجاح! جاري التوجيه...', 'success');
            
            setTimeout(() => {
                window.location.href = '/';
            }, 1500);
            
        } catch (error) {
            console.error('Google sign in error:', error);
            let errorMessage = 'حدث خطأ أثناء تسجيل الدخول بـ Google';
            
            if (error.code === 'auth/popup-closed-by-user') {
                errorMessage = 'تم إلغاء تسجيل الدخول';
            } else if (error.code === 'auth/popup-blocked') {
                errorMessage = 'تم حظر النافذة المنبثقة. يرجى السماح بالنوافذ المنبثقة والمحاولة مرة أخرى';
            }
            
            showMessage(errorMessage);
        }
    }

    if (googleLoginBtn) {
        googleLoginBtn.addEventListener('click', handleGoogleSignIn);
    }

    if (googleRegisterBtn) {
        googleRegisterBtn.addEventListener('click', handleGoogleSignIn);
    }

    // Forgot password handler
    if (forgotPasswordLink) {
        forgotPasswordLink.addEventListener('click', async (e) => {
            e.preventDefault();
            
            const email = document.getElementById('loginEmail').value;
            
            if (!email) {
                showMessage('يرجى إدخال البريد الإلكتروني أولاً');
                return;
            }

            try {
                await sendPasswordResetEmail(auth, email);
                showMessage('تم إرسال رابط إعادة تعيين كلمة المرور إلى بريدك الإلكتروني', 'success');
            } catch (error) {
                console.error('Password reset error:', error);
                let errorMessage = 'حدث خطأ أثناء إرسال رابط إعادة التعيين';
                
                if (error.code === 'auth/user-not-found') {
                    errorMessage = 'البريد الإلكتروني غير مسجل';
                } else if (error.code === 'auth/invalid-email') {
                    errorMessage = 'البريد الإلكتروني غير صالح';
                }
                
                showMessage(errorMessage);
            }
        });
    }

    // Check if user is already logged in
    auth.onAuthStateChanged((user) => {
        if (user) {
            // User is signed in, redirect to main page
            console.log('User already logged in:', user.email);
            // Uncomment the line below if you want to auto-redirect
            // window.location.href = '/';
        }
    });
});

// Utility functions
function validateEmail(email) {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
}

function validatePassword(password) {
    return password.length >= 6;
} 