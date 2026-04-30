/**
 * AquaSentinel AI - Password Recovery Controller
 */

const FORGOT_PASSWORD = {
    async requestQuestion(email) {
        try {
            const data = await API.auth.forgotPasswordQuestion(email);
            if (data.success) {
                return data.security_question;
            }
        } catch (err) {
            UI.showToast(err.message, 'error');
            throw err;
        }
    },

    async verifyAnswer(email, answer) {
        try {
            const data = await API.auth.verifyAnswer({ email, security_answer: answer });
            if (data.success) {
                return data.reset_token;
            }
        } catch (err) {
            UI.showToast(err.message, 'error');
            throw err;
        }
    },

    async resetPassword(email, resetToken, newPassword) {
        try {
            const data = await API.auth.resetPassword({ 
                email, 
                reset_token: resetToken, 
                new_password: newPassword 
            });
            if (data.success) {
                UI.showToast(data.message, 'success');
                setTimeout(() => {
                    window.location.href = 'login.html';
                }, 2000);
                return data;
            }
        } catch (err) {
            UI.showToast(err.message, 'error');
            throw err;
        }
    }
};
