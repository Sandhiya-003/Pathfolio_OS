// frontend/src/context/AuthContext.jsx
import { createContext, useContext, useEffect, useState, useCallback } from "react";
import { api, ApiError } from "../lib/api";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  const clearSession = useCallback(() => {
    api.setToken(null);
    setUser(null);
  }, []);

  useEffect(() => {
    async function bootstrap() {
      // 1. Check for OAuth token in URL
      const urlParams = new URLSearchParams(window.location.search);
      const authSuccess = urlParams.get("auth") === "success";
      const oauthToken = urlParams.get("token");
      const oauthEmail = urlParams.get("email");
      const oauthUsername = urlParams.get("username");

      if (authSuccess && oauthToken) {
        // Save REAL JWT Token so backend requests succeed
        api.setToken(oauthToken);

        const oauthUser = {
          email: oauthEmail || "",
          username: oauthUsername || oauthEmail?.split("@")[0] || "User",
          fullName: oauthUsername || oauthEmail?.split("@")[0] || "User",
        };

        setUser(oauthUser);

        // Remove token from browser address bar
        window.history.replaceState({}, document.title, window.location.pathname);
        setLoading(false);
        return;
      }

      // 2. Standard bootstrap check
      if (!api.getToken()) {
        setLoading(false);
        return;
      }

      try {
        const me = await api.me();
        setUser(me);
      } catch {
        clearSession();
      } finally {
        setLoading(false);
      }
    }

    bootstrap();

    function onUnauthorized() {
      clearSession();
    }
    window.addEventListener("pathfolio:unauthorized", onUnauthorized);
    return () => window.removeEventListener("pathfolio:unauthorized", onUnauthorized);
  }, [clearSession]);

  async function login(identifier, password) {
    const res = await api.login({ identifier, password });
    api.setToken(res.access_token);
    setUser(res.user);
    return res.user;
  }

  async function register({ username, email, password, fullName }) {
    const res = await api.register({ username, email, password, fullName });
    api.setToken(res.access_token);
    setUser(res.user);
    return res.user;
  }

  function logout() {
    clearSession();
  }

  return (
    <AuthContext.Provider value={{ user, loading, login, register, logout, isAuthenticated: !!user }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}

export { ApiError };