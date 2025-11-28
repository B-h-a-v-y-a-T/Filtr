// Simulated Database Service using localStorage

const DB_KEYS = {
    USERS: 'filtr_users',
    SESSIONS: 'filtr_session'
};

export const mockDB = {
    // Initialize DB if empty
    init: () => {
        if (!localStorage.getItem(DB_KEYS.USERS)) {
            localStorage.setItem(DB_KEYS.USERS, JSON.stringify([]));
        }
    },

    // Create a new user
    createUser: (userData) => {
        const users = JSON.parse(localStorage.getItem(DB_KEYS.USERS) || '[]');

        // Check if email exists
        if (users.find(u => u.email === userData.email)) {
            throw new Error('User already exists with this email');
        }

        const newUser = {
            id: 'usr_' + Math.random().toString(36).substr(2, 9),
            ...userData,
            createdAt: new Date().toISOString()
        };

        users.push(newUser);
        localStorage.setItem(DB_KEYS.USERS, JSON.stringify(users));
        return newUser;
    },

    // Authenticate user
    loginUser: (email, password) => {
        const users = JSON.parse(localStorage.getItem(DB_KEYS.USERS) || '[]');
        const user = users.find(u => u.email === email && u.password === password);

        if (!user) {
            throw new Error('Invalid email or password');
        }

        // Create session (simple version)
        const session = {
            token: 'tok_' + Math.random().toString(36).substr(2, 9),
            user: { id: user.id, name: user.name, email: user.email },
            expiry: new Date(Date.now() + 24 * 60 * 60 * 1000).toISOString() // 24h
        };

        localStorage.setItem(DB_KEYS.SESSIONS, JSON.stringify(session));
        return session;
    },

    // Get current session
    getSession: () => {
        const sessionStr = localStorage.getItem(DB_KEYS.SESSIONS);
        if (!sessionStr) return null;

        const session = JSON.parse(sessionStr);
        if (new Date(session.expiry) < new Date()) {
            localStorage.removeItem(DB_KEYS.SESSIONS);
            return null;
        }
        return session;
    },

    // Logout
    logout: () => {
        localStorage.removeItem(DB_KEYS.SESSIONS);
    }
};

// Initialize on load
mockDB.init();
