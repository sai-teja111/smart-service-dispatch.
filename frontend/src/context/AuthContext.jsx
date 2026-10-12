import {
    createContext,
    useContext,
    useEffect,
    useState
} from "react";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {

    const [token, setToken] = useState(
        () => localStorage.getItem("access_token")
    );

    const [user, setUser] = useState(() => {
        const storedUser = localStorage.getItem("user");

        if (!storedUser) {
            return null;
        }

        try {
            return JSON.parse(storedUser);
        } catch {
            localStorage.removeItem("user");
            return null;
        }
    });

    useEffect(() => {
        if (token) {
            localStorage.setItem("access_token", token);
        } else {
            localStorage.removeItem("access_token");
        }
    }, [token]);

    useEffect(() => {
        if (user) {
            localStorage.setItem(
                "user",
                JSON.stringify(user)
            );
        } else {
            localStorage.removeItem("user");
        }
    }, [user]);

    const login = (accessToken, userData) => {
        setToken(accessToken);
        setUser(userData);
    };

    const logout = () => {
        setToken(null);
        setUser(null);
    };

    const isAuthenticated = Boolean(token);

    return (
        <AuthContext.Provider
            value={{
                token,
                user,
                isAuthenticated,
                login,
                logout
            }}
        >
            {children}
        </AuthContext.Provider>
    );
}

export function useAuth() {
    const context = useContext(AuthContext);

    if (!context) {
        throw new Error(
            "useAuth must be used inside AuthProvider"
        );
    }

    return context;
}
